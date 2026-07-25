from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
YAML_FILE = ROOT / "防DNS泄露.yaml"
JS_FILE = ROOT / "防DNS泄露.js"
STASH_FILE = ROOT / "stash.stoverride"
CI_FILE = ROOT / ".github/workflows/validate-config.yml"
README_FILE = ROOT / "README.md"


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.write_text(text, encoding="utf-8")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def replace_group_filter_yaml(text, group_name, new_filter, label):
    pattern = re.compile(
        rf'(?ms)(^\s*(?:-\s+)?name:\s*{re.escape(group_name)}\s*$.*?^\s*filter:\s*")[^"]*(")'
    )
    text, count = pattern.subn(rf'\1{new_filter}\2', text, count=1)
    if count != 1:
        raise SystemExit(f"{label}: failed to update filter for {group_name}")
    return text


def replace_group_filter_js(text, group_name, new_filter, label):
    pattern = re.compile(
        rf'(^\s*\{{[^\n]*name:\s*"{re.escape(group_name)}"[^\n]*filter:\s*")[^"]*("[^\n]*$)',
        re.MULTILINE,
    )
    text, count = pattern.subn(rf'\1{new_filter}\2', text, count=1)
    if count != 1:
        raise SystemExit(f"{label}: failed to update JS filter for {group_name}")
    return text


def move_rule(text, exact_line, anchor_line, inserted_line, label):
    lines = text.splitlines()
    lines = [line for line in lines if line.strip() != exact_line.strip()]
    try:
        index = next(i for i, line in enumerate(lines) if line.strip() == anchor_line.strip())
    except StopIteration:
        raise SystemExit(f"{label}: anchor not found: {anchor_line}")
    indent = re.match(r"^\s*", lines[index]).group(0)
    lines.insert(index + 1, indent + inserted_line.strip())
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


FILTERS = {
    "香港": "(?i)(广港|香港|Hong ?Kong|HKG|🇭🇰|(^|[^A-Z])HK([^A-Z]|$))",
    "台湾": "(?i)(广台|台湾|台灣|Tai ?Wan|Taiwan|TWN|🇹🇼|(^|[^A-Z])TW([^A-Z]|$))",
    "日本": "(?i)(广日|日本|川日|东京|大阪|泉日|埼玉|沪日|深日|Japan|🇯🇵|(^|[^A-Z])JP([^A-Z]|$))",
    "新加坡": "(?i)(广新|新加坡|坡|狮城|Singapore|🇸🇬|(^|[^A-Z])SG([^A-Z]|$))",
    "美国": "(?i)(广美|美国|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|洛杉|圣何塞|圣克拉|西雅|芝加|United States|USA|🇺🇸|(^|[^A-Z])US([^A-Z]|$))",
    "韩国": "(?i)(广韩|韩国|韓國|首尔|春川|Korea|🇰🇷|(^|[^A-Z])KR([^A-Z]|$))",
    "越南": "(?i)(越南|Vietnam|Ho ?Chi ?Minh|HCM|🇻🇳|(^|[^A-Z])VN([^A-Z]|$))",
    "中国": "(?i)(广中|中国|上海|北京|广州|深圳|江苏|浙江|China|🇨🇳|(^|[^A-Z])CN([^A-Z]|$))",
}


# ---------------- Main YAML ----------------
yaml = read(YAML_FILE)

# IPv6 follows the client/software setting instead of being forced by the override.
yaml = yaml.replace("  inet6-address:\n    - fd00:1::1/126\n", "")
yaml = yaml.replace("  ipv6: true\n", "")
yaml = yaml.replace("  fake-ip-range6: fdfe:dcba:9876::1/64\n", "")

yaml = replace_once(
    yaml,
    "  default-nameserver: [223.5.5.5, 119.29.29.29]\n",
    "  default-nameserver:\n    - https://223.5.5.5/dns-query\n    - https://1.1.1.1/dns-query\n",
    "YAML encrypted bootstrap DNS",
)
yaml = replace_once(
    yaml,
    "  direct-nameserver:\n    - https://223.5.5.5/dns-query\n    - https://doh.pub/dns-query\n  direct-nameserver-follow-policy: false\n",
    "  direct-nameserver:\n    - https://1.1.1.1/dns-query\n    - https://8.8.8.8/dns-query\n  direct-nameserver-follow-policy: true\n",
    "YAML direct DNS policy",
)
yaml = replace_once(
    yaml,
    "  # 越南服务：优先越南节点，第二位 DIRECT；兼顾越南本地服务可用性和直连场景。\n",
    "  # 越南服务：越南本地网络默认直连，必要时可切换到越南或周边节点。\n",
    "YAML Vietnam comment",
)
yaml = replace_once(
    yaml,
    "    proxies: [越南-自动, DIRECT, 越南节点, 新加坡-自动, 新加坡节点, 香港-自动, 香港节点, 节点选择]\n",
    "    proxies: [DIRECT, 越南-自动, 越南节点, 新加坡-自动, 新加坡节点, 香港-自动, 香港节点, 节点选择]\n",
    "YAML Vietnam policy order",
)
yaml = replace_once(
    yaml,
    "    proxies: [美国节点, 日本节点, 新加坡节点, 香港节点, 美国-自动, 日本-自动, 新加坡-自动, 香港-自动, 节点选择, DIRECT]\n",
    "    proxies: [美国-自动, 日本-自动, 新加坡-自动, 香港-自动, 美国节点, 日本节点, 新加坡节点, 香港节点, 节点选择, DIRECT]\n",
    "YAML AI policy order",
)

for region, value in FILTERS.items():
    yaml = replace_group_filter_yaml(yaml, f"{region}节点", value, "YAML region filters")
    yaml = replace_group_filter_yaml(yaml, f"{region}-自动", value, "YAML region filters")

yaml = replace_once(
    yaml,
    "  reject: &meta_domain\n    type: http\n    behavior: domain\n    format: mrs\n    interval: 86400\n",
    "  reject: &meta_domain\n    type: http\n    behavior: domain\n    format: mrs\n    interval: 86400\n    proxy: 节点选择\n",
    "YAML provider proxy template",
)
yaml = replace_once(
    yaml,
    "  telegramcidr:\n    type: http\n    behavior: ipcidr\n    format: mrs\n    interval: 86400\n",
    "  telegramcidr:\n    type: http\n    behavior: ipcidr\n    format: mrs\n    interval: 86400\n    proxy: 节点选择\n",
    "YAML telegram provider proxy",
)
yaml = move_rule(
    yaml,
    '- "RULE-SET,reject,广告过滤"',
    '- "GEOIP,LAN,DIRECT,no-resolve"',
    '- "RULE-SET,reject,广告过滤"',
    "YAML ad rule priority",
)
write(YAML_FILE, yaml)


# ---------------- JavaScript override ----------------
js = read(JS_FILE)
js = js.replace('    "inet6-address": ["fd00:1::1/126"],\n', "")
js = js.replace("    ipv6: true,\n", "")
js = js.replace('    "fake-ip-range6": "fdfe:dcba:9876::1/64",\n', "")
js = replace_once(
    js,
    '    "default-nameserver": ["223.5.5.5", "119.29.29.29"],\n',
    '    "default-nameserver": [\n      "https://223.5.5.5/dns-query",\n      "https://1.1.1.1/dns-query",\n    ],\n',
    "JS encrypted bootstrap DNS",
)
js = replace_once(
    js,
    '    "direct-nameserver": [\n      "https://223.5.5.5/dns-query",\n      "https://doh.pub/dns-query",\n    ],\n    "direct-nameserver-follow-policy": false,\n',
    '    "direct-nameserver": [\n      "https://1.1.1.1/dns-query",\n      "https://8.8.8.8/dns-query",\n    ],\n    "direct-nameserver-follow-policy": true,\n',
    "JS direct DNS policy",
)
js = replace_once(
    js,
    '  { name: "越南服务", type: "select", proxies: ["越南-自动", "DIRECT", "越南节点", "新加坡-自动", "新加坡节点", "香港-自动", "香港节点", "节点选择"],',
    '  { name: "越南服务", type: "select", proxies: ["DIRECT", "越南-自动", "越南节点", "新加坡-自动", "新加坡节点", "香港-自动", "香港节点", "节点选择"],',
    "JS Vietnam policy order",
)
js = replace_once(
    js,
    '  { name: "AI", type: "select", proxies: ["美国节点", "日本节点", "新加坡节点", "香港节点", "美国-自动", "日本-自动", "新加坡-自动", "香港-自动", "节点选择", "DIRECT"],',
    '  { name: "AI", type: "select", proxies: ["美国-自动", "日本-自动", "新加坡-自动", "香港-自动", "美国节点", "日本节点", "新加坡节点", "香港节点", "节点选择", "DIRECT"],',
    "JS AI policy order",
)
for region, value in FILTERS.items():
    js = replace_group_filter_js(js, f"{region}节点", value, "JS region filters")
    js = replace_group_filter_js(js, f"{region}-自动", value, "JS region filters")
js = replace_once(
    js,
    '  interval: 86400,\n};\n',
    '  interval: 86400,\n  proxy: "节点选择",\n};\n',
    "JS provider proxy template",
)
js = replace_once(
    js,
    '  telegramcidr: { type: "http", behavior: "ipcidr", format: "mrs", interval: 86400, url:',
    '  telegramcidr: { type: "http", behavior: "ipcidr", format: "mrs", interval: 86400, proxy: "节点选择", url:',
    "JS telegram provider proxy",
)
js = move_rule(
    js,
    "RULE-SET,reject,广告过滤",
    "GEOIP,LAN,DIRECT,no-resolve",
    "RULE-SET,reject,广告过滤",
    "JS ad rule priority",
)
write(JS_FILE, js)


# ---------------- Stash override ----------------
stash = read(STASH_FILE)
stash = stash.replace("  ipv6: true\n", "")
stash = replace_once(
    stash,
    "    proxies: [越南-自动, DIRECT, 越南节点, 新加坡-自动, 新加坡节点, 香港-自动, 香港节点, 节点选择]\n",
    "    proxies: [DIRECT, 越南-自动, 越南节点, 新加坡-自动, 新加坡节点, 香港-自动, 香港节点, 节点选择]\n",
    "Stash Vietnam policy order",
)
stash = replace_once(
    stash,
    "    proxies: [美国节点, 日本节点, 新加坡节点, 香港节点, 美国-自动, 日本-自动, 新加坡-自动, 香港-自动, 节点选择, DIRECT]\n",
    "    proxies: [美国-自动, 日本-自动, 新加坡-自动, 香港-自动, 美国节点, 日本节点, 新加坡节点, 香港节点, 节点选择, DIRECT]\n",
    "Stash AI policy order",
)
for region, value in FILTERS.items():
    stash = replace_group_filter_yaml(stash, f"{region}节点", value, "Stash region filters")
    stash = replace_group_filter_yaml(stash, f"{region}-自动", value, "Stash region filters")
stash = stash.replace(
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/",
    "https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@meta/",
)
stash = move_rule(
    stash,
    "- RULE-SET,reject,广告过滤",
    "- GEOIP,LAN,DIRECT,no-resolve",
    "- RULE-SET,reject,广告过滤",
    "Stash ad rule priority",
)
write(STASH_FILE, stash)


# ---------------- CI safety and semantic checks ----------------
ci = read(CI_FILE)
ci = replace_once(
    ci,
    "      - name: Compare YAML and JS full config\n        run: |\n",
    "      - name: Compare YAML and JS full config\n        if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository\n        run: |\n",
    "CI safe JS evaluation",
)
semantic_step = r'''
      - name: Check policy semantics
        run: |
          ruby <<'RUBY'
          require "yaml"

          main = YAML.safe_load_file("防DNS泄露.yaml", aliases: true)
          stash = YAML.safe_load_file("stash.stoverride", aliases: true)
          errors = []

          dns = main.fetch("dns", {})
          tun = main.fetch("tun", {})
          bootstrap = Array(dns["default-nameserver"])
          unless bootstrap.any? && bootstrap.all? { |item| item.to_s.match?(%r{\A(?:https|tls)://}) }
            errors << "main default-nameserver must use encrypted IP-based resolvers"
          end
          errors << "direct-nameserver-follow-policy must be true" unless dns["direct-nameserver-follow-policy"] == true
          errors << "IPv6 must follow client settings (dns.ipv6 present)" if dns.key?("ipv6")
          errors << "IPv6 must follow client settings (fake-ip-range6 present)" if dns.key?("fake-ip-range6")
          errors << "IPv6 must follow client settings (tun.inet6-address present)" if tun.key?("inet6-address")

          groups = Array(main["proxy-groups"]).to_h { |group| [group["name"], group] }
          errors << "Vietnam policy must default to DIRECT" unless Array(groups.dig("越南服务", "proxies")).first == "DIRECT"
          errors << "AI policy must prefer an automatic group" unless Array(groups.dig("AI", "proxies")).first.to_s.end_with?("-自动")

          rules = Array(main["rules"])
          ad_index = rules.index("RULE-SET,reject,广告过滤")
          ai_index = rules.index("RULE-SET,openai,AI")
          errors << "ad rule must appear before service rules" unless ad_index && ai_index && ad_index < ai_index

          Hash(main["rule-providers"] || {}).each do |name, provider|
            errors << "rule-provider #{name} must download through 节点选择" unless provider["proxy"] == "节点选择"
          end

          Hash(stash["rule-providers"] || {}).each do |name, provider|
            if provider["url"].to_s.include?("raw.githubusercontent.com")
              errors << "Stash rule-provider #{name} still uses GitHub Raw"
            end
          end
          errors << "Stash IPv6 must follow client settings" if Hash(stash["dns"] || {}).key?("ipv6")

          if errors.any?
            warn errors.map { |item| "- #{item}" }.join("\n")
            exit 1
          end
          puts "Policy semantic checks passed."
          RUBY

'''
marker = "\n  validate-mihomo:\n"
if marker not in ci:
    raise SystemExit("CI semantic check insertion point not found")
ci = ci.replace(marker, "\n" + semantic_step + "  validate-mihomo:\n", 1)
write(CI_FILE, ci)


# ---------------- README ----------------
readme = read(README_FILE)
readme = replace_once(
    readme,
    "- IPv6：各版本均保持 IPv6 开启，适合需要 IPv6 可用性的网络环境。\n",
    "- IPv6：覆写不强制开启或关闭 IPv6，跟随客户端/软件自身设置。\n",
    "README IPv6 feature",
)
readme = replace_once(
    readme,
    "- 本配置默认启用 fake-ip 和 IPv6；主配置还启用 TUN DNS 劫持，建议先备份原客户端配置。\n",
    "- 本配置默认启用 fake-ip；IPv6 跟随客户端/软件设置。主配置包含 TUN DNS 劫持参数，建议先备份原客户端配置。\n",
    "README usage note",
)
readme = replace_once(
    readme,
    "- `stash.stoverride` 是 Stash 专用版本，保留 DNS、Sniffer、策略组、规则集和规则分流，并保持 IPv6 开启。\n",
    "- `stash.stoverride` 是 Stash 专用版本，保留 DNS、Sniffer、策略组、规则集和规则分流；IPv6 跟随 Stash 自身设置。\n",
    "README Stash IPv6 note",
)
readme = replace_once(
    readme,
    "- 越南服务独立分组，适合 Zalo、Grab、Shopee 越南、越南航空/票务/本地站点等场景。\n",
    "- 越南服务独立分组并默认 DIRECT，适合在越南本地网络访问 Zalo、Grab、Shopee 越南、航空/票务和本地站点。\n",
    "README Vietnam behavior",
)
readme = replace_once(
    readme,
    "- DNS 防泄露：启用 `respect-rules`，按规则分流 DNS 请求。\n",
    "- DNS 防泄露：启用 `respect-rules`，按规则分流 DNS 请求；Mihomo 主配置使用加密启动 DNS，并让直连 DNS 遵循策略。\n",
    "README DNS behavior",
)
write(README_FILE, readme)

print("Mihomo configuration fixes applied successfully.")
