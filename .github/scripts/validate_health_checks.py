#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys

AUTOMATIC_HEALTH_CHECKS = {
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
SELECT_HEALTH_CHECKS = {
    "节点选择": ("https://cp.cloudflare.com/generate_204", "204"),
    "漏网之鱼": ("https://www.gstatic.com/generate_204", "204"),
    "越南服务": ("https://www.google.com.vn/generate_204", "204"),
    "国内服务": (
        "https://connectivitycheck.platform.hicloud.com/generate_204",
        "204",
    ),
    "GitHub": ("https://github.com/favicon.ico", "200"),
    "YouTube": ("https://www.youtube.com/generate_204", "204"),
    "Netflix": (
        "https://assets.nflxext.com/ffe/siteui/common/icons/nficon2016.ico",
        "200",
    ),
    "AI": ("https://auth.openai.com/favicon.ico", "200"),
    "谷歌服务": ("https://www.google.com/generate_204", "204"),
    "电报消息": ("https://telegram.org/favicon.ico", "200"),
    "Meta / X": ("https://www.facebook.com/favicon.ico", "200"),
    "游戏平台": ("https://cdn.cloudflare.steamstatic.com/favicon.ico", "200"),
    "微软服务": ("https://www.microsoft.com/favicon.ico", "200"),
    "TikTok": ("https://www.tiktok.com/favicon.ico", "200"),
    "苹果服务": ("https://captive.apple.com/hotspot-detect.html", "200"),
    "Spotify": ("https://open.spotify.com/favicon.ico", "200"),
    "哔哩哔哩港澳台": (
        "https://p.bstarstatic.com/fe-static/deps/bilibili_tv.ico?v=1",
        "200",
    ),
    "全部节点": ("https://connectivitycheck.gstatic.com/generate_204", "204"),
    "香港节点": ("https://www.google.com.hk/generate_204", "204"),
    "台湾节点": ("https://www.google.com.tw/generate_204", "204"),
    "日本节点": ("https://www.google.co.jp/generate_204", "204"),
    "新加坡节点": ("https://www.google.com.sg/generate_204", "204"),
    "美国节点": ("https://www.google.com/generate_204", "204"),
    "韩国节点": ("https://www.google.co.kr/generate_204", "204"),
    "越南节点": ("https://www.google.com.vn/generate_204", "204"),
    "中国节点": ("https://www.baidu.com", "200"),
}
GROUP_HEALTH_CHECKS = {**SELECT_HEALTH_CHECKS, **AUTOMATIC_HEALTH_CHECKS}
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
RETURN_TO_CHINA_PATTERN = (
    "(?:回国|港广|港沪|港深|沪港|深港|广中)"
)
FOREIGN_REGION_PATTERN = (
    "(?:广港|香港|Hong ?Kong|🇭🇰|(^|[^A-Z])HK([^A-Z]|$)|(^|[^A-Z])HKG([^A-Z]|$)|"
    "广台|台湾|台灣|Tai ?Wan|Taiwan|🇹🇼|(^|[^A-Z])TW([^A-Z]|$)|"
    "(^|[^A-Z])TWN([^A-Z]|$)|(^|[^A-Z])TPE([^A-Z]|$)|"
    "广日|日本|川日|东京|大阪|泉日|埼玉|沪日|深日|Japan|🇯🇵|"
    "(^|[^A-Z])JP([^A-Z]|$)|(^|[^A-Z])NRT([^A-Z]|$)|"
    "(^|[^A-Z])HND([^A-Z]|$)|(^|[^A-Z])KIX([^A-Z]|$)|"
    "广新|新加坡|坡县|狮城|Singapore|🇸🇬|(^|[^A-Z])SG([^A-Z]|$)|"
    "(^|[^A-Z])SGP([^A-Z]|$)|(^|[^A-Z])SIN([^A-Z]|$)|"
    "广美|美国|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|洛杉|圣何塞|圣克拉|"
    "西雅|芝加|United ?States|🇺🇸|(^|[^A-Z])US([^A-Z]|$)|"
    "(^|[^A-Z])USA([^A-Z]|$)|"
    "广韩|韩国|韓國|首尔|春川|Korea|🇰🇷|(^|[^A-Z])KR([^A-Z]|$)|"
    "(^|[^A-Z])ICN([^A-Z]|$)|(^|[^A-Z])SEL([^A-Z]|$)|"
    "越南|Vietnam|Ho ?Chi ?Minh|胡志明|河内|Hanoi|🇻🇳|"
    "(^|[^A-Z])VN([^A-Z]|$)|(^|[^A-Z])HCM([^A-Z]|$)|"
    "(^|[^A-Z])HCMC([^A-Z]|$)|(^|[^A-Z])SGN([^A-Z]|$)|"
    "(^|[^A-Z])HAN([^A-Z]|$)|"
    "澳门|澳門|Macao|Macau|🇲🇴|(^|[^A-Z])MO([^A-Z]|$)|"
    "(^|[^A-Z])MFM([^A-Z]|$))"
)
DOMESTIC_NODE_PATTERN = (
    "(?:中国|上海|北京|广州|深圳|江苏|浙江|🇨🇳|"
    "(^|[^A-Z])China([^A-Z]|$)|"
    "(^|[^A-Z])CN(?!2(?:[^0-9]|$))([^A-Z]|$))"
)
GOOD_CHINA_FILTER = (
    f"(?i)^(?:.*{RETURN_TO_CHINA_PATTERN}|"
    f"(?!.*{FOREIGN_REGION_PATTERN}).*{DOMESTIC_NODE_PATTERN}).*$"
)
GOOD_AUTO_FILTER = (
    "(?i)^(?!.*(?:官网|套餐|流量|异常|剩余|到期|过期|更新|联系|群))"
    f"(?!(?:.*{RETURN_TO_CHINA_PATTERN}|"
    f"(?!.*{FOREIGN_REGION_PATTERN}).*{DOMESTIC_NODE_PATTERN})).*$"
)
RETURN_TO_CHINA_EXCLUDE_FILTER = "(?i)(回国|港广|港沪|港深|沪港|深港|广中)"
GOOD_HONG_KONG_FILTER = (
    "(?i)(广港|香港|Hong ?Kong|🇭🇰|(^|[^A-Z])HK([^A-Z]|$)|(^|[^A-Z])HKG([^A-Z]|$))"
)
REGION_FILTERS = {
    "香港": GOOD_HONG_KONG_FILTER,
    "台湾": "(?i)(广台|台湾|台灣|Tai ?Wan|Taiwan|🇹🇼|(^|[^A-Z])TW([^A-Z]|$)|(^|[^A-Z])TWN([^A-Z]|$)|(^|[^A-Z])TPE([^A-Z]|$))",
    "日本": "(?i)(广日|日本|川日|东京|大阪|泉日|埼玉|沪日|深日|Japan|🇯🇵|(^|[^A-Z])JP([^A-Z]|$)|(^|[^A-Z])NRT([^A-Z]|$)|(^|[^A-Z])HND([^A-Z]|$)|(^|[^A-Z])KIX([^A-Z]|$))",
    "新加坡": "(?i)(广新|新加坡|坡县|狮城|Singapore|🇸🇬|(^|[^A-Z])SG([^A-Z]|$)|(^|[^A-Z])SGP([^A-Z]|$)|(^|[^A-Z])SIN([^A-Z]|$))",
    "美国": "(?i)(广美|美国|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|洛杉|圣何塞|圣克拉|西雅|芝加|United ?States|🇺🇸|(^|[^A-Z])US([^A-Z]|$)|(^|[^A-Z])USA([^A-Z]|$))",
    "韩国": "(?i)(广韩|韩国|韓國|首尔|春川|Korea|🇰🇷|(^|[^A-Z])KR([^A-Z]|$)|(^|[^A-Z])ICN([^A-Z]|$)|(^|[^A-Z])SEL([^A-Z]|$))",
    "越南": "(?i)(越南|Vietnam|Ho ?Chi ?Minh|胡志明|河内|Hanoi|🇻🇳|(^|[^A-Z])VN([^A-Z]|$)|(^|[^A-Z])HCM([^A-Z]|$)|(^|[^A-Z])HCMC([^A-Z]|$)|(^|[^A-Z])SGN([^A-Z]|$)|(^|[^A-Z])HAN([^A-Z]|$))",
    "中国": GOOD_CHINA_FILTER,
}
PORTABLE_REGION_FILTERS = {
    region: (
        pattern
        if region == "中国"
        else "(?i)^(?!.*(回国|港广|港沪|港深|沪港|深港|广中)).*"
        + pattern.removeprefix("(?i)")
    )
    for region, pattern in REGION_FILTERS.items()
}
REGION_GROUP_FILTERS = {
    group_name: pattern
    for region, pattern in REGION_FILTERS.items()
    for group_name in (f"{region}节点", f"{region}-自动")
}
PORTABLE_REGION_GROUP_FILTERS = {
    group_name: PORTABLE_REGION_FILTERS[region]
    for region in REGION_FILTERS
    for group_name in (f"{region}节点", f"{region}-自动")
}
EXPECTED_INCLUDE_ALL_GROUPS = {"全部节点", "自动选择", *REGION_GROUP_FILTERS}
REGION_CODE_SAMPLES = {
    "香港": ("[SSR]HK2", "[SSR]HKG2"),
    "台湾": ("[SSR]TW2", "[SSR]TWN2", "[SSR]TPE2"),
    "日本": ("[SSR]JP2", "[SSR]NRT2", "[SSR]HND2", "[SSR]KIX2"),
    "新加坡": ("[SSR]SG2", "[SSR]SGP2", "[SSR]SIN2"),
    "美国": ("[SSR]US2", "[SSR]USA2"),
    "韩国": ("[SSR]KR2", "[SSR]ICN2", "[SSR]SEL2"),
    "越南": ("[SSR]VN2", "[SSR]HCM2", "[SSR]HCMC2", "[SSR]SGN2", "[SSR]HAN2"),
    "中国": ("[SSR]CN", "[SSR]CN01", "[SSR]CN-01", "[SSR]CN02"),
}
NON_REGION_SAMPLES = (
    "[SSR]Jerusalem",
    "[SSR]Lausanne",
    "[SSR]UKR-01",
    "[SSR]SVN-01",
    "[SSR]ASGARD-01",
    "[SSR]BHKP-01",
    "[SSR]XJPK-01",
    "[SSR]Chinatown 01",
    "[SSR]山坡线路",
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
)
REGIONAL_RETURN_SAMPLES = {
    "香港": "[SSR]HK_回国",
    "台湾": "[SSR]TW_回国",
    "日本": "[SSR]JP_回国",
    "新加坡": "[SSR]SG_回国",
    "美国": "[SSR]US_回国",
    "韩国": "[SSR]KR_回国",
    "越南": "[SSR]VN_回国",
}
FOREIGN_SAMPLES = (
    "[TRO]新加坡V4",
    "[TRO]日本大阪15",
    "[SSR]台湾2",
)
FOREIGN_CONTEXT_SAMPLES = (
    ("[SSR]香港 CN2 GIA", "香港"),
    ("[SSR]美国 CN2 GIA", "美国"),
    ("[SSR]中国香港", "香港"),
    ("[SSR]China Hong Kong", "香港"),
    ("[SSR]中国台湾", "台湾"),
    ("[SSR]中国-日本 IPLC", "日本"),
    ("[SSR]China Mobile HK", "香港"),
    ("[SSR]澳门 CN2", None),
    ("[SSR]CN2", None),
)
DOMESTIC_APP_PACKAGES = (
    "com.tencent.mm",
    "com.eg.android.AlipayGphone",
)
VIETNAM_APP_PACKAGES = (
    "com.zing.zalo",
    "com.shopee.vn",
    "com.grabtaxi.passenger",
    "xyz.be.customer",
    "com.jtexpress.customer.vn",
    "com.viettel.ViettelPost",
    "com.vnp.myvinaphone",
    "vn.com.vng.zalopay",
    "com.mservice.momotransfer",
    "com.VCB",
    "vn.com.techcombank.bb.app",
    "com.vnpay.bidv",
    "com.mbmobile",
    "com.vietinbank.ipay",
    "vn.tiki.app.tikiandroid",
    "com.lazada.android",
    "com.deliverynow",
)
VIETNAM_EXACT_DOMAINS = (
    "zalopay.vn",
    "shopeefood.vn",
    "techcombank.com",
)
DOMESTIC_RULE_PROVIDERS = {
    "wechat": "rule/Clash/WeChat/WeChat.yaml",
    "alipay": "rule/Clash/AliPay/AliPay.yaml",
}
RULE_PROVIDER_SIZE_LIMIT = 4194304
SHADOWROCKET_REQUIRED_RULES = (
    "rule/Shadowrocket/Twitter/Twitter.list,Meta / X",
    "rule/Shadowrocket/Facebook/Facebook.list,Meta / X",
    "geo/geosite/steam@cn.list,国内服务",
    "geo/geosite/category-games-cn.list,国内服务",
    "geo/geosite/steam.list,游戏平台",
    "geo/geosite/category-games-!cn.list,游戏平台",
    "rule/Shadowrocket/WeChat/WeChat.list,国内服务",
    "rule/Shadowrocket/AliPay/AliPay.list,国内服务",
)
GAME_PROVIDER_ROUTES = {
    "steam-cn": ("steam@cn.mrs", "国内服务"),
    "category-games-cn": ("category-games-cn.mrs", "国内服务"),
    "steam": ("steam.mrs", "游戏平台"),
    "category-games-global": ("category-games-!cn.mrs", "游戏平台"),
}
FORBIDDEN_STEAM_PROCESS_RULES = (
    "PROCESS-NAME,com.valvesoftware.android.steam.community,游戏平台",
    "PROCESS-NAME,steam.exe,游戏平台",
    "PROCESS-NAME,steamwebhelper.exe,游戏平台",
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


def shadowrocket_setting(text: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^{re.escape(key)}\s*=\s*(.+?)\s*$", text)
    if not match:
        fail(f"shadowrocket.conf: setting {key!r} was not found")
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


def shadowrocket_select_members(group: str) -> list[str]:
    parts = [part.strip() for part in group.split(",")]
    if not parts or parts[0] != "select":
        fail("shadowrocket.conf: expected a select policy group")
    return [part for part in parts[1:] if part and "=" not in part]


def check_group_file(filename: str, *, stash: bool) -> None:
    text = Path(filename).read_text(encoding="utf-8")
    telegram_checked = False
    regional_groups_checked: set[str] = set()
    health_groups_checked: set[str] = set()
    include_all_groups_checked: set[str] = set()
    select_count = 0
    expected_region_filters = (
        PORTABLE_REGION_GROUP_FILTERS if stash else REGION_GROUP_FILTERS
    )

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
            elif name in SELECT_HEALTH_CHECKS:
                health_groups_checked.add(name)
                expected_url, expected_status = SELECT_HEALTH_CHECKS[name]
                expected_keys = {"url", "expected-status", "timeout"}
                if direct_keys != expected_keys:
                    fail(
                        f"{filename}: select group {name!r} health-check keys "
                        f"must be {sorted(expected_keys)}, found {sorted(direct_keys)}"
                    )
                if value(block, "url") != expected_url:
                    fail(
                        f"{filename}: select group {name!r} does not use "
                        f"{expected_url}"
                    )
                if value(block, "expected-status") != expected_status:
                    fail(
                        f"{filename}: select group {name!r} expected-status "
                        f"must be {expected_status}"
                    )
                if value(block, "timeout") != "10000":
                    fail(
                        f"{filename}: select group {name!r} timeout is not 10000 ms"
                    )
            elif direct_keys:
                fail(
                    f"{filename}: select group {name!r} contains unexpected "
                    f"health-check keys {sorted(direct_keys)}"
                )

        if group_type == "url-test" or merged:
            if name not in AUTOMATIC_HEALTH_CHECKS:
                fail(f"{filename}: unexpected url-test group {name!r}")
            health_groups_checked.add(name)
            expected_url, expected_status = AUTOMATIC_HEALTH_CHECKS[name]
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

        if not stash and value(block, "include-all") == "true":
            include_all_groups_checked.add(name)
            if value(block, "empty-fallback") != "REJECT":
                fail(f"{filename}: {name} must fail closed with empty-fallback: REJECT")

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

        if name in expected_region_filters:
            regional_groups_checked.add(name)
            if value(block, "filter") != expected_region_filters[name]:
                fail(f"{filename}: {name} filter is not synchronized")
            if (
                not stash
                and not name.startswith("中国")
                and value(block, "exclude-filter") != RETURN_TO_CHINA_EXCLUDE_FILTER
            ):
                fail(f"{filename}: {name} does not exclude return-to-China nodes")

    if not telegram_checked:
        fail(f"{filename}: Telegram policy group was not found")
    if regional_groups_checked != set(REGION_GROUP_FILTERS):
        missing = sorted(set(REGION_GROUP_FILTERS) - regional_groups_checked)
        fail(f"{filename}: regional policy groups are incomplete: {missing}")
    expected_health_groups = (
        set(AUTOMATIC_HEALTH_CHECKS) if stash else set(GROUP_HEALTH_CHECKS)
    )
    if health_groups_checked != expected_health_groups:
        missing = sorted(expected_health_groups - health_groups_checked)
        extra = sorted(health_groups_checked - expected_health_groups)
        fail(
            f"{filename}: health-check groups differ; "
            f"missing={missing}, extra={extra}"
        )
    if stash and select_count < 20:
        fail(f"{filename}: unexpectedly found only {select_count} select groups")
    if not stash:
        direct_include_all_groups = EXPECTED_INCLUDE_ALL_GROUPS - {
            "香港-自动",
            "台湾-自动",
            "日本-自动",
            "新加坡-自动",
            "美国-自动",
            "韩国-自动",
            "越南-自动",
        }
        if include_all_groups_checked != direct_include_all_groups:
            fail(
                f"{filename}: directly declared include-all groups differ: "
                f"{sorted(include_all_groups_checked)}"
            )


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

for server in (
    "https://1.1.1.1/dns-query#节点选择",
    "https://8.8.8.8/dns-query#节点选择",
):
    if yaml_text.count(server) < 7 or js_text.count(server) < 7:
        fail(f"external DNS does not consistently follow 节点选择: {server}")

if "https://8.8.8.8/dns-query#DIRECT" in yaml_text or "https://8.8.8.8/dns-query#DIRECT" in js_text:
    fail("external fallback DNS is still pinned to DIRECT")

for policy in (
    "rule-set:steam-cn",
    "rule-set:category-games-cn",
    "rule-set:wechat",
    "rule-set:alipay",
    "+.aliapp.org",
):
    if policy not in yaml_text or policy not in js_text:
        fail(f"Mihomo domestic DNS policy is missing: {policy}")

for domain in ("+.alipaylog.com", "+.aliapp.org"):
    if domain not in stash_text:
        fail(f"stash.stoverride: domestic DNS policy is missing: {domain}")

if "  follow-rule: true" not in stash_text:
    fail("stash.stoverride: DNS queries do not follow routing rules")
if "  proxy-server-nameserver: #!replace" not in stash_text:
    fail("stash.stoverride: proxy bootstrap DNS is missing")
if re.search(r"(?m)^\s+-\s+(?:223\.5\.5\.5|119\.29\.29\.29)\s*$", stash_text):
    fail("stash.stoverride: plaintext bootstrap DNS remains")

expected_size_line = f"    size-limit: {RULE_PROVIDER_SIZE_LIMIT}"
if yaml_text.count(expected_size_line) != 4:
    fail("防DNS泄露.yaml: rule-provider size limits are incomplete")
if js_text.count(f'"size-limit": {RULE_PROVIDER_SIZE_LIMIT}') != 4:
    fail("防DNS泄露.js: rule-provider size limits are incomplete")

for filename, text in (
    ("防DNS泄露.yaml", yaml_text),
    ("防DNS泄露.js", js_text),
    ("stash.stoverride", stash_text),
    ("shadowrocket.conf", shadowrocket_text),
):
    for keyword in FORBIDDEN_VIETNAM_KEYWORDS:
        if f"DOMAIN-KEYWORD,{keyword},越南服务" in text:
            fail(f"{filename}: broad Vietnam DOMAIN-KEYWORD remains: {keyword}")

    for domain in VIETNAM_EXACT_DOMAINS:
        if f"DOMAIN-SUFFIX,{domain},越南服务" not in text:
            fail(f"{filename}: precise Vietnam domain is missing: {domain}")

for filename, text in (
    ("防DNS泄露.yaml", yaml_text),
    ("防DNS泄露.js", js_text),
    ("stash.stoverride", stash_text),
):
    for package in FORBIDDEN_BROWSER_PACKAGES:
        if f"PROCESS-NAME,{package},国内服务" in text:
            fail(f"{filename}: browser is still pinned to 国内服务: {package}")

    if GOOD_ALL_NODES_FILTER not in text:
        fail(f"{filename}: safe all-node filter is missing")
    if GOOD_AUTO_FILTER not in text:
        fail(f"{filename}: safe automatic filter is missing")
    if GOOD_CHINA_FILTER not in text:
        fail(f"{filename}: return-to-China filter is missing")
    expected_region_filters = (
        PORTABLE_REGION_GROUP_FILTERS
        if filename == "stash.stoverride"
        else REGION_GROUP_FILTERS
    )
    for group_name, pattern in expected_region_filters.items():
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

for package in VIETNAM_APP_PACKAGES:
    process_rule = f"PROCESS-NAME,{package},越南服务"
    if process_rule not in yaml_text or process_rule not in js_text:
        fail(f"Android Vietnam process rule is missing: {package}")

for filename, text in (
    ("防DNS泄露.yaml", yaml_text),
    ("防DNS泄露.js", js_text),
    ("stash.stoverride", stash_text),
):
    for provider, (source_name, policy) in GAME_PROVIDER_ROUTES.items():
        if source_name not in text:
            fail(f"{filename}: game provider source is missing: {source_name}")
        if f"RULE-SET,{provider},{policy}" not in text:
            fail(f"{filename}: game provider {provider} is not routed to {policy}")
    domestic_game_position = text.find("RULE-SET,category-games-cn,国内服务")
    overseas_game_position = text.find("DOMAIN-SUFFIX,steampowered.com,游戏平台")
    if not 0 <= domestic_game_position < overseas_game_position:
        fail(f"{filename}: domestic game rules must precede overseas game rules")
    if "RULE-SET,category-games,游戏平台" in text:
        fail(f"{filename}: combined China/global game provider is still active")

for filename, text in (("防DNS泄露.yaml", yaml_text), ("防DNS泄露.js", js_text)):
    for process_rule in FORBIDDEN_STEAM_PROCESS_RULES:
        if process_rule in text:
            fail(f"{filename}: Steam process rule bypasses CN/global domain split")

for filename, text in (("防DNS泄露.yaml", yaml_text), ("防DNS泄露.js", js_text)):
    if "PROCESS-NAME,tv.danmaku.bili,国内服务" not in text:
        fail(f"{filename}: mainland Bilibili app must use 国内服务")
    if "PROCESS-NAME,com.bstar.intl,哔哩哔哩港澳台" not in text:
        fail(f"{filename}: international Bilibili app routing is missing")

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
return_exclude_pattern = re.compile(RETURN_TO_CHINA_EXCLUDE_FILTER)
for proxy_name in RETURN_TO_CHINA_SAMPLES:
    if not china_pattern.search(proxy_name):
        fail(f"China filter rejected return node: {proxy_name}")
    if auto_pattern.search(proxy_name):
        fail(f"automatic selection accepted return node: {proxy_name}")
for proxy_name in FOREIGN_SAMPLES:
    if china_pattern.search(proxy_name):
        fail(f"China filter accepted foreign node: {proxy_name}")
    if not auto_pattern.search(proxy_name):
        fail(f"automatic selection rejected foreign node: {proxy_name}")

for proxy_name, expected_region in FOREIGN_CONTEXT_SAMPLES:
    if china_pattern.search(proxy_name):
        fail(f"China filter accepted foreign-context node: {proxy_name}")
    if not auto_pattern.search(proxy_name):
        fail(f"automatic selection rejected foreign-context node: {proxy_name}")
    if expected_region and not re.search(REGION_FILTERS[expected_region], proxy_name):
        fail(f"{expected_region} filter rejected foreign-context node: {proxy_name}")

for region, proxy_name in REGIONAL_RETURN_SAMPLES.items():
    if not china_pattern.search(proxy_name):
        fail(f"China filter rejected {region} return node: {proxy_name}")
    if not re.search(REGION_FILTERS[region], proxy_name):
        fail(f"{region} return test fixture is not recognized by its base filter: {proxy_name}")
    if not return_exclude_pattern.search(proxy_name):
        fail(f"regional exclude filter missed return node: {proxy_name}")
    if re.search(PORTABLE_REGION_FILTERS[region], proxy_name):
        fail(f"portable {region} filter accepted return node: {proxy_name}")

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
            f"shadowrocket.conf: group {group_name!r} does not use "
            f"{expected_url}"
        )
    if group_name in SELECT_HEALTH_CHECKS:
        timeout_match = re.search(r"(?:^|,)\s*timeout\s*=\s*(\d+)", group)
        if not timeout_match or timeout_match.group(1) != "10":
            fail(
                f"shadowrocket.conf: select group {group_name!r} "
                "timeout must be 10 seconds"
            )

for group_name, expected_filter in PORTABLE_REGION_GROUP_FILTERS.items():
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
    if not shadow_auto_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: automatic selection rejected foreign node: {proxy_name}")
for proxy_name, expected_region in FOREIGN_CONTEXT_SAMPLES:
    if shadow_china_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: China filter accepted foreign-context node: {proxy_name}")
    if not shadow_auto_pattern.search(proxy_name):
        fail(
            "shadowrocket.conf: automatic selection rejected foreign-context "
            f"node: {proxy_name}"
        )
    if expected_region:
        region_pattern = re.compile(
            shadowrocket_regex(
                shadowrocket_group(shadowrocket_text, f"{expected_region}节点")
            )
        )
        if not region_pattern.search(proxy_name):
            fail(
                f"shadowrocket.conf: {expected_region} filter rejected "
                f"foreign-context node: {proxy_name}"
            )
for proxy_name in NON_REGION_SAMPLES:
    if not shadow_auto_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: automatic selection rejected non-regional node: {proxy_name}")

for region, proxy_name in REGIONAL_RETURN_SAMPLES.items():
    shadow_region_pattern = re.compile(
        shadowrocket_regex(shadowrocket_group(shadowrocket_text, f"{region}节点"))
    )
    if shadow_region_pattern.search(proxy_name):
        fail(f"shadowrocket.conf: {region} filter accepted return node: {proxy_name}")

for key in ("dns-server", "fallback-dns-server", "proxy-dns-server"):
    for server in shadowrocket_setting(shadowrocket_text, key):
        if not server.startswith(("https://", "tls://", "quic://", "h3://")):
            fail(f"shadowrocket.conf: {key} contains plaintext DNS: {server}")
for server in shadowrocket_setting(shadowrocket_text, "fallback-dns-server"):
    if "#proxy" not in server.lower():
        fail(f"shadowrocket.conf: fallback DNS is not proxied: {server}")

shadow_rules = shadowrocket_text.split("[Rule]", 1)[-1]
advertising_rule = (
    "rule/Shadowrocket/Advertising/Advertising.list,广告过滤"
)
advertising_position = shadow_rules.find(advertising_rule)
first_service_position = shadow_rules.find("DOMAIN-SUFFIX,chatgpt.com,AI")
if advertising_position < 0 or first_service_position < 0:
    fail("shadowrocket.conf: advertising or service routing rule is missing")
if advertising_position > first_service_position:
    fail("shadowrocket.conf: advertising rule must precede service rules")

for required_rule in SHADOWROCKET_REQUIRED_RULES:
    if required_rule not in shadow_rules:
        fail(f"shadowrocket.conf: synchronized service rule is missing: {required_rule}")

shadow_domestic_game_position = shadow_rules.find(
    "geo/geosite/category-games-cn.list,国内服务"
)
shadow_overseas_game_position = shadow_rules.find(
    "DOMAIN-SUFFIX,steampowered.com,游戏平台"
)
if not 0 <= shadow_domestic_game_position < shadow_overseas_game_position:
    fail("shadowrocket.conf: domestic game rules must precede overseas game rules")
for obsolete_rule in (
    "rule/Shadowrocket/Steam/Steam.list,游戏平台",
    "rule/Shadowrocket/Game/Game.list,游戏平台",
):
    if obsolete_rule in shadow_rules:
        fail(f"shadowrocket.conf: obsolete combined game rule remains: {obsolete_rule}")

wechat_position = shadow_rules.find("rule/Shadowrocket/WeChat/WeChat.list,国内服务")
alipay_position = shadow_rules.find("rule/Shadowrocket/AliPay/AliPay.list,国内服务")
china_position = shadow_rules.find("rule/Shadowrocket/China/China_Domain.list,国内服务")
if not (0 <= wechat_position < china_position and 0 <= alipay_position < china_position):
    fail("shadowrocket.conf: WeChat and AliPay rules must precede the general China list")

yaml_select_members = {}
for block in group_blocks(yaml_text):
    members = inline_items(value(block, "proxies"))
    if members:
        yaml_select_members[value(block, "name")] = members
for group_name, expected_members in yaml_select_members.items():
    actual_members = shadowrocket_select_members(
        shadowrocket_group(shadowrocket_text, group_name)
    )
    if actual_members != expected_members:
        fail(
            f"shadowrocket.conf: {group_name} members differ from the main config: "
            f"{actual_members!r}"
        )

if "policy-select-name=自动选择" not in shadowrocket_group(
    shadowrocket_text, "节点选择"
):
    fail("shadowrocket.conf: 节点选择 must default to 自动选择")
if "policy-select-name=香港-自动" not in shadowrocket_group(
    shadowrocket_text, "GitHub"
):
    fail("shadowrocket.conf: GitHub must default to 香港-自动")

for group_name in ("国内服务", "越南服务"):
    if not re.match(
        r"select\s*,\s*DIRECT(?:\s*,|$)",
        shadowrocket_group(shadowrocket_text, group_name),
    ):
        fail(f"shadowrocket.conf: {group_name} must default to DIRECT")

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
  includeAllGroups: enabled["proxy-groups"]
    .filter((group) => group["include-all"])
    .map((group) => ({ name: group.name, emptyFallback: group["empty-fallback"] })),
  providerSizeLimits: Object.fromEntries(
    Object.entries(enabled["rule-providers"])
      .map(([name, provider]) => [name, provider["size-limit"] ?? null])
  ),
  dnsFallback: enabled.dns.fallback,
  proxyGroups: enabled["proxy-groups"].map((group) => ({
    name: group.name,
    type: group.type,
    url: group.url ?? null,
    expectedStatus: group["expected-status"] ?? null,
    interval: group.interval ?? null,
    timeout: group.timeout ?? null,
    lazy: group.lazy ?? null,
    tolerance: group.tolerance ?? null,
    maxFailedTimes: group["max-failed-times"] ?? null,
  })),
}));
'''

try:
    completed = subprocess.run(
        ["node", "-e", node_code],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
except (OSError, subprocess.CalledProcessError) as exc:
    fail(f"could not evaluate JavaScript override: {exc}")

js_result = json.loads(completed.stdout)
if {key: js_result.get(key) for key in ("enabled", "disabled")} != {
    "enabled": True,
    "disabled": False,
}:
    fail(f"JavaScript override did not preserve tun.enable: {js_result!r}")

js_groups = {
    group["name"]: group for group in js_result.get("proxyGroups", [])
}
for group_name, (expected_url, expected_status) in SELECT_HEALTH_CHECKS.items():
    group = js_groups.get(group_name)
    if not group:
        fail(f"防DNS泄露.js: select group is missing: {group_name}")
    if group.get("type") != "select":
        fail(f"防DNS泄露.js: {group_name} is not a select group")
    if group.get("url") != expected_url:
        fail(f"防DNS泄露.js: {group_name} does not use {expected_url}")
    if str(group.get("expectedStatus")) != expected_status:
        fail(
            f"防DNS泄露.js: {group_name} expected-status must be "
            f"{expected_status}"
        )
    if group.get("timeout") != 10000:
        fail(f"防DNS泄露.js: {group_name} timeout is not 10000 ms")
    periodic_keys = {
        key: group.get(key)
        for key in ("interval", "lazy", "tolerance", "maxFailedTimes")
        if group.get(key) is not None
    }
    if periodic_keys:
        fail(
            f"防DNS泄露.js: select group {group_name} enables periodic "
            f"health checks: {periodic_keys}"
        )

js_include_all = {
    item["name"]: item.get("emptyFallback")
    for item in js_result.get("includeAllGroups", [])
}
if set(js_include_all) != EXPECTED_INCLUDE_ALL_GROUPS:
    fail(f"防DNS泄露.js: include-all groups differ: {sorted(js_include_all)}")
for group_name, fallback in js_include_all.items():
    if fallback != "REJECT":
        fail(f"防DNS泄露.js: {group_name} does not fail closed")

provider_size_limits = js_result.get("providerSizeLimits", {})
if not provider_size_limits or any(
    size != RULE_PROVIDER_SIZE_LIMIT for size in provider_size_limits.values()
):
    fail(f"防DNS泄露.js: invalid provider size limits: {provider_size_limits!r}")

expected_external_fallback = [
    "https://1.1.1.1/dns-query#节点选择",
    "https://8.8.8.8/dns-query#节点选择",
]
if js_result.get("dnsFallback") != expected_external_fallback:
    fail("防DNS泄露.js: external DNS fallback does not follow 节点选择")

print("health-check and routing topology OK")
