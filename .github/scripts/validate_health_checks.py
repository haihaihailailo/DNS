#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys

TEST_URL = "https://1.1.1.1/cdn-cgi/trace"
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
    "(?i)^(?!.*(官网|套餐|流量|异常|剩余|到期|过期|更新|联系|群|回国|中国|China|上海|北京|广州|深圳|江苏|浙江|🇨🇳)).*$"
)


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


def first_inline_item(raw: str) -> str:
    value_text = raw.strip()
    if value_text.startswith("[") and value_text.endswith("]"):
        value_text = value_text[1:-1]
    return value_text.split(",", 1)[0].strip()


def check_group_file(filename: str, *, stash: bool) -> None:
    text = Path(filename).read_text(encoding="utf-8")
    telegram_checked = False
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
            if value(block, "url") != TEST_URL:
                fail(
                    f"{filename}: url-test group {name!r} does not use {TEST_URL}"
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

    if not telegram_checked:
        fail(f"{filename}: Telegram policy group was not found")
    if stash and select_count < 20:
        fail(f"{filename}: unexpectedly found only {select_count} select groups")


check_group_file("防DNS泄露.yaml", stash=False)
check_group_file("stash.stoverride", stash=True)

yaml_text = Path("防DNS泄露.yaml").read_text(encoding="utf-8")
js_text = Path("防DNS泄露.js").read_text(encoding="utf-8")
stash_text = Path("stash.stoverride").read_text(encoding="utf-8")

if "#自动选择" in yaml_text or "#自动选择" in js_text:
    fail("DNS still depends on 自动选择")

for server in (
    "https://1.1.1.1/dns-query#DIRECT",
    "https://223.5.5.5/dns-query#DIRECT",
):
    if server not in yaml_text or server not in js_text:
        fail(f"missing direct proxy-server DNS {server}")

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
