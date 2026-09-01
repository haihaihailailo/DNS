#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys

GROUP_HEALTH_CHECKS = {
    "自动选择": ("https://cp.cloudflare.com/generate_204", "204"),
    "香港-自动": ("https://www.google.com.hk/generate_204", "204"),
    "台湾-自动": ("https://www.google.com.tw/generate_204", "204"),
    "日本-自动": ("https://www.google.co.jp/generate_204", "204"),
    "新加坡-自动": ("https://www.google.com.sg/generate_204", "204"),
    "美国-自动": ("https://www.google.com/generate_204", "204"),
    "韩国-自动": ("https://www.google.co.kr/generate_204", "204"),
    "越南-自动": ("https://www.google.com.vn/generate_204", "204"),
    "中国-自动": ("https://www.baidu.com", "200"),
}
HEALTH_KEYS = {
    "url",
    "expected-status",
    "interval",
    "timeout",
    "max-failed-times",
    "lazy",
    "tolerance",
}
FORBIDDEN_VIETNAM_KEYWORDS = (
    "zalo",
    "grab",
    "gojek",
    "tiki",
    "zing",
    "momo",
    "zalopay",
    "baemin",
    "shopeefood",
)
FORBIDDEN_BROWSER_PACKAGES = (
    "com.heytap.browser",
    "com.android.browser",
)
GOOD_ALL_NODES_FILTER = (
    "(?i)^(?!.*(官网|套餐|流量|异常|剩余|到期|过期|更新|联系|群)).*$"
)
GOOD_AUTO_FILTER = (
    "(?i)^(?!.*(官网|套餐|流量|异常|剩余|到期|过期|更新|联系|群|回国|港广|港沪|港深|沪港|深港|广中|中国|上海|北京|广州|深圳|江苏|浙江|China|🇨🇳|(^|[^A-Z])CN([^A-Z]|$))).*$"
)
GOOD_CHINA_FILTER = (
    "(?i)(回国|港广|港沪|港深|沪港|深港|广中|中国|上海|北京|广州|深圳|江苏|浙江|China|🇨🇳|(^|[^A-Z])CN([^A-Z]|$))"
)
REGION_FILTERS = {
    "香港": "(?i)(广港|香港|Hong ?Kong|🇭🇰|(^|[^A-Z])HK([^A-Z]|$)|(^|[^A-Z])HKG([^A-Z]|$))",
    "台湾": "(?i)(广台|台湾|台灣|Tai ?Wan|Taiwan|🇹🇼|(^|[^A-Z])TW([^A-Z]|$)|(^|[^A-Z])TWN([^A-Z]|$))",
    "日本": "(?i)(广日|日本|川日|东京|大阪|泉日|埼玉|沪日|深日|Japan|🇯🇵|(^|[^A-Z])JP([^A-Z]|$))",
    "新加坡": "(?i)(广新|新加坡|坡|狮城|Singapore|🇸🇬|(^|[^A-Z])SG([^A-Z]|$))",
    "美国": "(?i)(广美|美国|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|洛杉|圣何塞|圣克拉|西雅|芝加|United ?States|🇺🇸|(^|[^A-Z])US([^A-Z]|$)|(^|[^A-Z])USA([^A-Z]|$))",
    "韩国": "(?i)(广韩|韩国|韓國|首尔|春川|Korea|🇰🇷|(^|[^A-Z])KR([^A-Z]|$))",
    "越南": "(?i)(越南|Vietnam|Ho ?Chi ?Minh|🇻🇳|(^|[^A-Z])VN([^A-Z]|$)|(^|[^A-Z])HCM([^A-Z]|$))",
    "中国": GOOD_CHINA_FILTER,
}
REGION_GROUP_FILTERS = {
    group_name: pattern
    for region, pattern in REGION_FILTERS.items()
    for group_name in (f"{region}节点", f"{region}-自动")
}
REGION_CODE_SAMPLES = {
    "香港": ("[SSR]HK2", "[SSR]HKG2"),
    "台湾": ("[SSR]TW2", "[SSR]TWN2"),
    "日本": ("[SSR]JP2",),
    "新加坡": ("[SSR]SG2",),
    "美国": ("[SSR]US2", "[SSR]USA2"),
    "韩国": ("[SSR]KR2",),
    "越南": ("[SSR]VN2", "[SSR]HCM2"),
    "中国": ("[SSR]CN2",),
}
NON_REGION_SAMPLES = (
    "[SSR]Jerusalem",
    "[SSR]Lausanne",
    "[SSR]UKR-01",
    "[SSR]SVN-01",
    "[SSR]ASGARD-01",
    "[SSR]BHKP-01",
    "[SSR]XJPK-01",
)
RETURN_TO_CHINA_SAMPLES = (
    "[SSR]港广专线3_回国",
    "[SSR]港沪专线3_回国",
    "IEPL回国",
    "广州回国01",
    "上海回国",
    "[SSR]港广专线3",
    "[SSR]港沪专线3",
    "[SSR]广中专线3",
    "[SSR]CN2",
)
FOREIGN_SAMPLES = (
    "[TRO]新加坡V4",
    "[TRO]日本大阪15",
    "[SSR]台湾2",
)
DOMESTIC_APP_PACKAGES = (
    "com.tencent.mm",
    "com.eg.android.AlipayGphone",
)
DOMESTIC_RULE_PROVIDERS = {
    "wechat": "rule/Clash/WeChat/WeChat.yaml",
    "alipay": "rule/Clash/AliPay/AliPay.yaml",
}


def fail(message: str) -> None:
    print(f"health-check validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def group_blocks(text: str) -> list[list[str]]:
    lines = text.splitlines()
    try:
        start = next(
            i for i, line in enumerate(lines)
            if re.match(r"^proxy-groups:\s*(?:#!replace)?\s*$", line)
        )
    except StopIteration as exc:
        raise ValueError("proxy-groups section not found") from exc

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^[^\s#][^:]*:\s*(?:#!\w+)?\s*$", lines[i]):
            end = i
            break

    starts = [i for i in range(start + 1, end) if lines[i].startswith("  - ")]
    return [
        lines[group_start : (starts[pos + 1] if pos + 1 < len(starts) else end)]
        for pos, group_start in enumerate(starts)
    ]


def value(block: list[str], key: str) -> str:
    for line in block:
        match = re.match(rf"^(?:  - |    ){re.escape(key)}:\s*(.+?)\s*$", line)
        if match:
            result = match.group(1)
            if (
                len(result) >= 2
                and result[0] == result[-1]
                and result[0] in {'"', "'"}
            ):
                result = result[1:-1]
            return result
    return ""


def inline_items(raw: str) -> list[str]:
    value_text = raw.strip()
    if value_text.startswith("[") and value_text.endswith("]"):
        value_text = value_text[1:-1]
    return [item.strip() for item in value_text.split(",") if item.strip()]


def first_inline_item(raw: str) -> str:
    items = inline_items(raw)
    return items[0] if items else ""


def shadowrocket_group(text: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}\s*=\s*(.+?)\s*$", text)
    if not match:
        fail(f"shadowrocket.conf: policy group {name!r} was not found")
    return match.group(1)


def shadowrocket_regex(group: str) -> str:
    match = re.search(
        r"policy-regex-filter\s*=\s*(.+?)(?=,\s*(?:url|interval|tolerance)\s*=|$)",
        group,
    )
    if not match:
        fail("shadowrocket.conf: policy-regex-filter was not found")
    return match.group(1).strip()


def check_group_file(filename: str, *, stash: bool) -> None:
    text = Path(filename).read_text(encoding="utf-8")
    telegram_checked = False
    regional_groups_checked: set[str] = set()
    health_groups_checked: set[str] = set()
    select_count = 0

    for block in group_blocks(text):
        group_type = value(block, "type")
        name = value(block, "name")
        merged = any("<<: *urltest_base" in line for line in block)
        direct_keys = {
            match.group(1)
            for line in block
            if (match := re.match(r"^    ([A-Za-z0-9-]+):", line))
            and match.group(1) in HEALTH_KEYS
        }

        if group_type == "select":
            select_count += 1
            if stash:
                if value(block, "interval") != "-1":
                    fail(
                        f"{filename}: Stash select group {name!r} must set interval: -1"
                    )
                unexpected = direct_keys - {"interval"}
                if unexpected:
                    fail(
                        f"{filename}: select group {name!r} contains "
                        f"unexpected health-check keys {sorted(unexpected)}"
                    )
            elif direct_keys:
                fail(
                    f"{filename}: Mihomo select group {name!r} contains "
                    f"health-check keys {sorted(direct_keys)}"
                )

        if group_type == "url-test" or merged:
            if name not in GROUP_HEALTH_CHECKS:
                fail(f"{filename}: unexpected url-test group {name!r}")
            health_groups_checked.add(name)
            expected_url, expected_status = GROUP_HEALTH_CHECKS[name]
            if value(block, "url") != expected_url:
                fail(
                    f"{filename}: url-test group {name!r} does not use "
                    f"{expected_url}"
                )
            if not stash and value(block, "expected-status") != expected_status:
                fail(
                    f"{filename}: url-test group {name!r} expected-status "
                    f"must be {expected_status}"
                )
            if value(block, "timeout") != "10000":
                fail(
                    f"{filename}: url-test group {name!r} timeout is not 10000 ms"
                )
            expected_lazy = "false" if name == "自动选择" else "true"
            if value(block, "lazy") != expected_lazy:
                fail(
                    f"{filename}: url-test group {name!r} lazy must be "
                    f"{expected_lazy}"
                )

        if name == "电报消息":
            telegram_checked = True
            first_proxy = first_inline_item(value(block, "proxies"))
            if first_proxy != "新加坡-自动":
                fail(
                    f"{filename}: Telegram must default to 新加坡-自动, "
                    f"found {first_proxy!r}"
                )

        dual_location_modes = {
            "国内服务": "中国-自动",
            "越南服务": "越南-自动",
        }
        if name in dual_location_modes:
            proxies = inline_items(value(block, "proxies"))
            first_proxy = proxies[0] if proxies else ""
            if first_proxy != "DIRECT":
                fail(
                    f"{filename}: {name} must default to DIRECT, "
                    f"found {first_proxy!r}"
                )
            alternate = dual_location_modes[name]
            if alternate not in proxies:
                fail(f"{filename}: {name} lacks alternate policy {alternate}")

        if name == "自动选择" and value(block, "filter") != GOOD_AUTO_FILTER:
            fail(f"{filename}: automatic selection filter is not synchronized")

        if name in REGION_GROUP_FILTERS:
            regional_groups_checked.add(name)
            if value(block, "filter") != REGION_GROUP_FILTERS[name]:
                fail(f"{filename}: {name} filter is not synchronized")

    if not telegram_checked:
        fail(f"{filename}: Telegram policy group was not found")
    if regional_groups_checked != set(REGION_GROUP_FILTERS):
        missing = sorted(set(REGION_GROUP_FILTERS) - regional_groups_checked)
        fail(f"{filename}: regional policy groups are incomplete: {missing}")
    if health_groups_checked != set(GROUP_HEALTH_CHECKS):
        missing = sorted(set(GROUP_HEALTH_CHECKS) - health_groups_checked)
        fail(f"{filename}: health-check groups are incomplete: {missing}")
    if stash and select_count < 20:
        fail(f"{filename}: unexpectedly found only {select_count} select groups")


check_group_file("防DNS泄露.yaml", stash=False)
check_group_file("stash.stoverride", stash=True)

yaml_text = Path("防DNS泄露.yaml").read_text(encoding="utf-8")
js_text = Path("防DNS泄露.js").read_text(encoding="utf-8")
stash_text = Path("stash.stoverride").read_text(encoding="utf-8")
shadowrocket_text = Path("shadowrocket.conf").read_text(encoding="utf-8")

if "#自动选择" in yaml_text or "#自动选择" in js_text:
    fail("DNS still depends on 自动选择")

for server in (
    "https://1.1.1.1/dns-query#DIRECT",
    "https://223.5.5.5/dns-query#DIRECT",
):
    if server not in yaml_text or server not in js_text:
        fail(f"missing direct proxy-server DNS {server}")

for policy in ("rule-set:wechat", "rule-set:alipay", "+.aliapp.org"):
    if policy not in yaml_text or policy not in js_text:
        fail(f"Mihomo domestic DNS policy is missing: {policy}")

for domain in ("+.alipaylog.com", "+.aliapp.org"):
    if domain not in stash_text:
        fail(f"stash.stoverride: domestic DNS policy is missing: {domain}")

for filename, text in (
    ("防DNS泄露.yaml", yaml_text),
    ("防DNS泄露.js", js_text),
    ("stash.stoverride", stash_text),
):
    for keyword in FORBIDDEN_VIETNAM_KEYWORDS:
        if f"DOMAIN-KEYWORD,{keyword},越南服务" in text:
            fail(f"{filename}: broad Vietnam DOMAIN-KEYWORD remains: {keyword}")

    for package in FORBIDDEN_BROWSER_PACKAGES:
        if f"PROCESS-NAME,{package},国内服务" in text:
            fail(f"{filename}: browser is still pinned to 国内服务: {package}")

    if GOOD_ALL_NODES_FILTER not in text:
        fail(f"{filename}: safe all-node filter is missing")
    if GOOD_AUTO_FILTER not in text:
        fail(f"{filename}: safe automatic filter is missing")
    if GOOD_CHINA_FILTER not in text:
        fail(f"{filename}: return-to-China filter is missing")
    for group_name, pattern in REGION_GROUP_FILTERS.items():
        if pattern not in text:
            fail(f"{filename}: regional filter is missing for {group_name}")

    for provider, source_path in DOMESTIC_RULE_PROVIDERS.items():
        if source_path not in text:
            fail(f"{filename}: {provider} provider source is missing")
        rule = f"RULE-SET,{provider},国内服务"
        if rule not in text:
            fail(f"{filename}: {provider} is not routed to 国内服务")
        if text.rfind(rule) > text.rfind("RULE-SET,cn,国内服务"):
            fail(f"{filename}: {provider} must precede the general China rule")

    if "DOMAIN-SUFFIX,aliapp.org,国内服务" not in text:
        fail(f"{filename}: Alipay CDN gap aliapp.org is not covered")

    if "RULE-SET,wechat,国内服务,no-resolve" not in text:
        fail(f"{filename}: WeChat rule set must use no-resolve")

for package in DOMESTIC_APP_PACKAGES:
    process_rule = f"PROCESS-NAME,{package},国内服务"
    if process_rule not in yaml_text or process_rule not in js_text:
        fail(f"Android domestic process rule is missing: {package}")

if re.search(
    r"(?m)^\s+-\s+(?:com\.tencent\.mm|com\.eg\.android\.AlipayGphone)\s*$",
    yaml_text,
):
    fail("防DNS泄露.yaml: WeChat or Alipay still bypasses TUN")
for package in DOMESTIC_APP_PACKAGES:
    if f'"{package}",' in js_text:
        fail(f"防DNS泄露.js: {package} still bypasses TUN")

china_pattern = re.compile(GOOD_CHINA_FILTER)
auto_pattern = re.compile(GOOD_AUTO_FILTER)
for proxy_name in RETURN_TO_CHINA_SAMPLES:
    if not china_pattern.search(proxy_name):
        fail(f"China filter rejected return node: {proxy_name}")
    if auto_pattern.search(proxy_name):
        fail(f"automatic selection accepted return node: {proxy_name}")
for proxy_name in FOREIGN_SAMPLES:
    if china_pattern.search(proxy_name):
        fail(f"China filter accepted foreign node: {proxy_name}")

for region, proxy_names in REGION_CODE_SAMPLES.items():
    pattern = re.compile(REGION_FILTERS[region])
    for proxy_name in proxy_names:
        if not pattern.search(proxy_name):
            fail(f"{region} filter rejected bounded code node: {proxy_name}")

for proxy_name in NON_REGION_SAMPLES:
    if not auto_pattern.search(proxy_name):
        fail(f"automatic selection rejected non-regional node: {proxy_name}")
    for region, filter_text in REGION_FILTERS.items():
        if re.search(filter_text, proxy_name):
            fail(f"{region} filter accepted embedded-code node: {proxy_name}")

for group_name, (expected_url, _) in GROUP_HEALTH_CHECKS.items():
    group = shadowrocket_group(shadowrocket_text, group_name)
    match = re.search(r"(?:^|,)\s*url\s*=\s*([^,\s]+)", group)
    if not match or match.group(1) != expected_url:
        fail(
            f"shadowrocket.conf: url-test group {group_name!r} does not use "
            f"{expected_url}"
        )

for group_name, expected_filter in REGION_GROUP_FILTERS.items():
    if shadowrocket_regex(shadowrocket_group(shadowrocket_text, group_name)) != expected_filter:
        fail(f"shadowrocket.conf: {group_name} filter is not synchronized")

shadow_china_pattern = re.compile(
    shadowrocket_regex(shadowrocket_group(shadowrocket_text, "中国节点"))
)
shadow_auto_pattern = re.compile(
    shadowrocket_regex(shadowrocket_group(shadowrocket_text, "自动选择"))
)
for proxy_name in RETURN_TO_CHINA_SAMPLES:
    if not shadow_china_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: China filter rejected return node: {proxy_name}")
    if shadow_auto_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: automatic selection accepted return node: {proxy_name}")
for proxy_name in FOREIGN_SAMPLES:
    if shadow_china_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: China filter accepted foreign node: {proxy_name}")
for proxy_name in NON_REGION_SAMPLES:
    if not shadow_auto_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: automatic selection rejected non-regional node: {proxy_name}")

for group_name in ("国内服务", "越南服务"):
    if not re.match(
        r"select\s*,\s*DIRECT(?:\s*,|$)",
        shadowrocket_group(shadowrocket_text, group_name),
    ):
        fail(f"shadowrocket.conf: {group_name} must default to DIRECT")

section = js_text[js_text.index('OVERRIDE["proxy-groups"] = [') :]
section = section[: section.index("\n];")]
for line in section.splitlines():
    if 'type: "select"' not in line:
        continue
    forbidden = [
        key
        for key in HEALTH_KEYS
        if re.search(
            rf'(?:^|,\s*){re.escape(chr(34) + key + chr(34) if "-" in key else key)}:',
            line,
        )
    ]
    if forbidden:
        fail(
            f"防DNS泄露.js: select group contains {forbidden}: {line.strip()}"
        )

if '{ name: "电报消息", type: "select", proxies: ["新加坡-自动",' not in js_text:
    fail("防DNS泄露.js: Telegram does not default to 新加坡-自动")

if '{ name: "国内服务", type: "select", proxies: ["DIRECT", "中国-自动",' not in js_text:
    fail("防DNS泄露.js: domestic dual-location policies are incomplete")

node_code = r'''
const fs = require("fs");
const vm = require("vm");
const code = fs.readFileSync("防DNS泄露.js", "utf8");
const sandbox = { console };
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: "防DNS泄露.js" });
const enabled = vm.runInContext("main({ tun: { enable: true } })", sandbox);
const disabled = vm.runInContext("main({ tun: { enable: false } })", sandbox);
process.stdout.write(JSON.stringify({
  enabled: enabled.tun && enabled.tun.enable,
  disabled: disabled.tun && disabled.tun.enable,
}));
'''

try:
    completed = subprocess.run(
        ["node", "-e", node_code],
        check=True,
        capture_output=True,
        text=True,
    )
except (OSError, subprocess.CalledProcessError) as exc:
    fail(f"could not evaluate JavaScript override: {exc}")

tun_result = json.loads(completed.stdout)
if tun_result != {"enabled": True, "disabled": False}:
    fail(f"JavaScript override did not preserve tun.enable: {tun_result!r}")

print("health-check and routing topology OK")
