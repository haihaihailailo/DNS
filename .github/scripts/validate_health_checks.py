#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
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


def fail(message: str) -> None:
    print(f"health-check validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def group_blocks(text: str) -> list[list[str]]:
    lines = text.splitlines()
    start = next(
        i for i, line in enumerate(lines)
        if re.match(r"^proxy-groups:\s*(?:#!replace)?\s*$", line)
    )
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^[^\s#][^:]*:\s*(?:#!\w+)?\s*$", lines[i]):
            end = i
            break
    starts = [i for i in range(start + 1, end) if lines[i].startswith("  - ")]
    return [
        lines[group_start:(starts[pos + 1] if pos + 1 < len(starts) else end)]
        for pos, group_start in enumerate(starts)
    ]


def value(block: list[str], key: str) -> str:
    for line in block:
        match = re.match(rf"^(?:  - |    ){re.escape(key)}:\s*(.+?)\s*$", line)
        if match:
            result = match.group(1)
            if len(result) >= 2 and result[0] == result[-1] and result[0] in {'"', "'"}:
                result = result[1:-1]
            return result
    return ""


for filename in ("防DNS泄露.yaml", "stash.stoverride"):
    text = Path(filename).read_text(encoding="utf-8")
    for block in group_blocks(text):
        group_type = value(block, "type")
        name = value(block, "name")
        merged = any("<<: *urltest_base" in line for line in block)
        if group_type == "select":
            found = {
                match.group(1)
                for line in block
                if (match := re.match(r"^    ([A-Za-z0-9-]+):", line))
                and match.group(1) in HEALTH_KEYS
            }
            if found:
                fail(f"{filename}: select group {name!r} contains {sorted(found)}")
        if group_type == "url-test" or merged:
            if value(block, "url") != TEST_URL:
                fail(f"{filename}: url-test group {name!r} does not use the stable test URL")
            if value(block, "timeout") != "10000":
                fail(f"{filename}: url-test group {name!r} timeout is not 10000 ms")
            expected_lazy = "false" if name == "自动选择" else "true"
            if value(block, "lazy") != expected_lazy:
                fail(f"{filename}: url-test group {name!r} lazy must be {expected_lazy}")

yaml_text = Path("防DNS泄露.yaml").read_text(encoding="utf-8")
js_text = Path("防DNS泄露.js").read_text(encoding="utf-8")
if "#自动选择" in yaml_text or "#自动选择" in js_text:
    fail("DNS still depends on 自动选择")
for server in (
    "https://1.1.1.1/dns-query#DIRECT",
    "https://223.5.5.5/dns-query#DIRECT",
):
    if server not in yaml_text or server not in js_text:
        fail(f"missing direct proxy-server DNS {server}")

section = js_text[js_text.index('OVERRIDE["proxy-groups"] = ['):]
section = section[:section.index("\n];")]
for line in section.splitlines():
    if 'type: "select"' in line:
        forbidden = [
            key for key in HEALTH_KEYS
            if re.search(rf'(?:^|,\s*){re.escape(chr(34) + key + chr(34) if "-" in key else key)}:', line)
        ]
        if forbidden:
            fail(f"防DNS泄露.js: select group contains {forbidden}: {line.strip()}")

print("health-check topology OK")
