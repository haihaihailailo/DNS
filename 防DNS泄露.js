/**
 * 文件说明：Clash Party / Mihomo Party JavaScript 覆写版本。
 * 维护口径：本文件必须与 防DNS泄露.yaml 的关键配置保持同步，CI 会自动比对。
 * 注释只解释结构，不改变实际覆写逻辑。
 */

/**
 * 防DNS泄露.js
 * Converted from 防DNS泄露.yaml for Clash Party / Mihomo Party JavaScript override.
 * Entry point: main(config) must return the modified config.
 */

// 远程 domain rule-provider 的通用模板。
const META_DOMAIN_PROVIDER = {
  type: "http",
  behavior: "domain",
  format: "mrs",
  interval: 86400,
  proxy: "节点选择",
};


// 地区自动测速组的通用模板。
const URLTEST_BASE = {
  type: "url-test",
  interval: 300,
  tolerance: 50,
  url: "https://www.gstatic.com/generate_204",
  "expected-status": 204,
  lazy: true,
  hidden: true,
  "include-all": true,
  filter: "(?i)^(?!.*(官网|套餐|流量|异常|剩余|到期|过期|更新|联系|群|VIP|回国|中国|CN|China|上海|北京|广州|深圳|江苏|浙江|🇨🇳)).*$",
  icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/speed.svg",
};


// 主覆写对象：包含全局、sniffer、TUN、DNS 等基础配置。
const OVERRIDE = {
  "unified-delay": true,
  profile: {
    "store-selected": true,
    "store-fake-ip": true,
  },
  "geo-auto-update": true,
  "geo-update-interval": 24,
  "tcp-concurrent": true,
  sniffer: {
    enable: true,
    "parse-pure-ip": true,
    // 这些域名依赖真实 DNS / 局域网 / 推送 / 时间服务，跳过嗅探避免目标被误改写。
    "skip-domain": [
      "+.lan",
      "+.local",
      "+.home.arpa",
      "+.localdomain",
      "router.asus.com",
      "tplogin.cn",
      "miwifi.com",
      "tendawifi.com",
      "time.*.com",
      "time.*.gov",
      "time.windows.com",
      "pool.ntp.org",
      "+.ntp.org",
      "+.push.apple.com",
      "courier.push.apple.com",
      "localhost.ptlogin2.qq.com",
      "localhost.sec.qq.com",
      "localhost.work.weixin.qq.com",
    ],
    "skip-dst-address": [
      "10.0.0.0/8",
      "172.16.0.0/12",
      "192.168.0.0/16",
      "100.64.0.0/10",
      "169.254.0.0/16",
      "fc00::/7",
      "fe80::/10",
    ],
    sniff: {
      HTTP: {
        ports: ["80", "8080-8880"],
        "override-destination": true,
      },
      TLS: {
        ports: [443, 8443],
      },
      QUIC: {
        ports: [443, 8443],
      },
    },
  },
  tun: {
    stack: "mixed",
    "auto-route": true,
    "auto-detect-interface": true,
    "dns-hijack": ["any:53", "tcp://any:53"],
    "strict-route": true,
    "route-exclude-address": [
      "10.0.0.0/8",
      "172.16.0.0/12",
      "192.168.0.0/16",
      "100.64.0.0/10",
      "169.254.0.0/16",
      "fc00::/7",
      "fe80::/10",
    ],
    "exclude-package": [
      "com.tencent.mm",
      "com.eg.android.AlipayGphone",
    ],
  },
  dns: {
    enable: true,
    listen: "127.0.0.1:1053",
    "prefer-h3": false,
    "respect-rules": true,
    "use-system-hosts": false,
    "cache-algorithm": "arc",
    "enhanced-mode": "fake-ip",
    "fake-ip-range": "198.18.0.1/16",
    // blacklist：匹配 fake-ip-filter 的域名返回真实 IP，其余域名返回 fake-ip。
    "fake-ip-filter-mode": "blacklist",
    "fake-ip-filter": [
      "+.lan",
      "+.local",
      "+.home.arpa",
      "+.localdomain",
      "router.asus.com",
      "tplogin.cn",
      "miwifi.com",
      "tendawifi.com",
      "+.msftconnecttest.com",
      "+.msftncsi.com",
      "+.push.apple.com",
      "courier.push.apple.com",
      "localhost.ptlogin2.qq.com",
      "localhost.sec.qq.com",
      "+.in-addr.arpa",
      "+.ip6.arpa",
      "time.*.com",
      "time.*.gov",
      "time.windows.com",
      "pool.ntp.org",
      "+.ntp.org",
      "+.stun.*",
      "stun.*.*",
      "localhost.work.weixin.qq.com",
    ],
    "default-nameserver": [
      "https://223.5.5.5/dns-query",
      "https://1.1.1.1/dns-query",
    ],
    nameserver: [
      "https://223.5.5.5/dns-query",
      "https://doh.pub/dns-query",
    ],
    fallback: [
      "https://1.1.1.1/dns-query#自动选择",
      "https://8.8.8.8/dns-query#自动选择",
    ],
    "fallback-filter": {
      geoip: true,
      "geoip-code": "CN",
      ipcidr: ["240.0.0.0/4"],
    },
    "proxy-server-nameserver": [
      "https://223.5.5.5/dns-query",
      "https://doh.pub/dns-query",
    ],
    "direct-nameserver": [
      "https://1.1.1.1/dns-query",
      "https://8.8.8.8/dns-query",
    ],
    "direct-nameserver-follow-policy": true,
    "nameserver-policy": {
      "rule-set:private": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "rule-set:cn": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "rule-set:microsoft": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "+.windowsupdate.com": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "+.download.windowsupdate.com": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "+.mp.microsoft.com": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "+.delivery.mp.microsoft.com": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "+.dl.delivery.mp.microsoft.com": ["https://223.5.5.5/dns-query", "https://doh.pub/dns-query"],
      "rule-set:geolocation-!cn": ["https://1.1.1.1/dns-query#自动选择", "https://8.8.8.8/dns-query#自动选择"],
      "rule-set:google": ["https://1.1.1.1/dns-query#自动选择", "https://8.8.8.8/dns-query#自动选择"],
      "rule-set:youtube": ["https://1.1.1.1/dns-query#自动选择", "https://8.8.8.8/dns-query#自动选择"],
      "rule-set:openai": ["https://1.1.1.1/dns-query#自动选择", "https://8.8.8.8/dns-query#自动选择"],
      "rule-set:github": ["https://1.1.1.1/dns-query#自动选择", "https://8.8.8.8/dns-query#自动选择"],
      "+.googleapis.cn": ["https://1.1.1.1/dns-query#自动选择", "https://8.8.8.8/dns-query#自动选择"],
    },
  },
  "proxy-groups": [],
  "rule-providers": {},
  rules: [],
};


// 策略组：与 YAML 的 proxy-groups 保持同步。
OVERRIDE["proxy-groups"] = [
  { name: "节点选择", type: "select", proxies: ["自动选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "中国-自动", "中国节点", "全部节点", "DIRECT"], url: "https://www.gstatic.com/generate_204", "expected-status": 204, interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/adjust.svg" },
  { name: "漏网之鱼", type: "select", proxies: ["节点选择", "自动选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "中国-自动", "中国节点", "DIRECT", "全部节点"], url: "https://www.gstatic.com/generate_204", "expected-status": 204, interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/fish.svg" },
  { name: "越南服务", type: "select", proxies: ["DIRECT", "越南-自动", "越南节点", "新加坡-自动", "新加坡节点", "香港-自动", "香港节点", "节点选择"], url: "https://zalo.me", "expected-status": "200/301/302", interval: 300, icon: "https://flagcdn.com/w320/vn.png" },
  { name: "国内服务", type: "select", proxies: ["DIRECT", "中国-自动", "中国节点", "香港-自动", "香港节点", "节点选择"], url: "https://www.baidu.com", "expected-status": "200/302", interval: 300, icon: "https://flagcdn.com/w320/cn.png" },
  { name: "GitHub", type: "select", proxies: ["香港-自动", "新加坡-自动", "日本-自动", "美国-自动", "香港节点", "新加坡节点", "日本节点", "美国节点", "节点选择", "DIRECT"], url: "https://github.com", "expected-status": "200/301/302", interval: 300, icon: "https://github.githubassets.com/favicons/favicon.svg" },
  { name: "YouTube", type: "select", proxies: ["节点选择", "自动选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "DIRECT"], url: "https://www.youtube.com/generate_204", "expected-status": "200/204/301/302", interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/youtube.svg" },
  { name: "Netflix", type: "select", proxies: ["节点选择", "自动选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "DIRECT"], url: "https://www.netflix.com", "expected-status": "200/301/302", interval: 300, icon: "https://testingcf.jsdelivr.net/gh/xiaolin-007/clash@main/icon/netflix.svg" },
  { name: "AI", type: "select", proxies: ["美国-自动", "日本-自动", "新加坡-自动", "香港-自动", "美国节点", "日本节点", "新加坡节点", "香港节点", "节点选择", "DIRECT"], url: "https://chatgpt.com/cdn-cgi/trace", "expected-status": 200, interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/chatgpt.svg" },
  { name: "谷歌服务", type: "select", proxies: ["节点选择", "新加坡节点", "日本节点", "香港节点", "美国节点", "新加坡-自动", "日本-自动", "香港-自动", "美国-自动", "自动选择", "DIRECT"], url: "https://www.gstatic.com/generate_204", "expected-status": 204, interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/google.svg" },
  { name: "电报消息", type: "select", proxies: ["新加坡-自动", "自动选择", "节点选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "中国-自动", "中国节点", "DIRECT"], url: "https://core.telegram.org", "expected-status": "200/301/302", interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/telegram.svg" },
  { name: "Meta / X", type: "select", proxies: ["节点选择", "自动选择", "新加坡-自动", "新加坡节点", "香港-自动", "香港节点", "日本-自动", "日本节点", "美国-自动", "美国节点", "台湾-自动", "台湾节点", "DIRECT"], url: "https://www.facebook.com", "expected-status": "200/301/302", interval: 300, icon: "https://www.facebook.com/favicon.ico" },
  { name: "游戏平台", type: "select", proxies: ["节点选择", "DIRECT", "自动选择", "香港-自动", "香港节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点"], url: "https://store.steampowered.com", "expected-status": "200/301/302", interval: 300, icon: "https://store.steampowered.com/favicon.ico" },
  { name: "微软服务", type: "select", proxies: ["DIRECT", "香港-自动", "新加坡-自动", "中国-自动", "香港节点", "新加坡节点", "中国节点", "美国-自动", "美国节点", "节点选择"], url: "http://www.msftconnecttest.com/connecttest.txt", "expected-status": 200, interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/microsoft.svg" },
  { name: "TikTok", type: "select", proxies: ["节点选择", "自动选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "DIRECT"], url: "https://www.tiktok.com", "expected-status": "200/301/302", interval: 300, icon: "https://testingcf.jsdelivr.net/gh/xiaolin-007/clash@main/icon/tiktok.svg" },
  { name: "苹果服务", type: "select", proxies: ["DIRECT", "自动选择", "节点选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "中国-自动", "中国节点"], url: "https://www.apple.com/library/test/success.html", "expected-status": 200, interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/apple.svg" },
  { name: "Spotify", type: "select", proxies: ["节点选择", "自动选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "DIRECT"], url: "https://open.spotify.com", "expected-status": "200/301/302", interval: 300, icon: "https://testingcf.jsdelivr.net/gh/xiaolin-007/clash@main/icon/spotify.svg" },
  { name: "哔哩哔哩港澳台", type: "select", proxies: ["DIRECT", "自动选择", "节点选择", "香港-自动", "香港节点", "台湾-自动", "台湾节点", "日本-自动", "日本节点", "新加坡-自动", "新加坡节点", "美国-自动", "美国节点", "韩国-自动", "韩国节点", "越南-自动", "越南节点", "中国-自动", "中国节点"], url: "https://www.bilibili.com", "expected-status": "200/301/302", interval: 300, icon: "https://testingcf.jsdelivr.net/gh/xiaolin-007/clash@main/icon/bilibili.svg" },
  { name: "广告过滤", type: "select", proxies: ["REJECT", "DIRECT"], url: "https://www.gstatic.com/generate_204", "expected-status": 204, interval: 300, icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/bug.svg" },
  { name: "全部节点", type: "select", "include-all": true, url: "https://www.gstatic.com/generate_204", "expected-status": 204, interval: 300, filter: "(?i)^(?!.*(官网|套餐|流量|异常|剩余|到期|过期|更新|联系|群|VIP)).*$", icon: "https://testingcf.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/adjust.svg" },
  { ...URLTEST_BASE, name: "自动选择" },
  { name: "香港节点", type: "select", "include-all": true, url: "https://www.google.com.hk/generate_204", "expected-status": "200/204/301/302", interval: 300, filter: "(?i)(广港|香港|Hong ?Kong|HKG|🇭🇰|(^|[^A-Z])HK([^A-Z]|$))", icon: "https://flagcdn.com/w320/hk.png" },
  { ...URLTEST_BASE, name: "香港-自动", url: "https://www.google.com.hk/generate_204", "expected-status": "200/204/301/302", filter: "(?i)(广港|香港|Hong ?Kong|HKG|🇭🇰|(^|[^A-Z])HK([^A-Z]|$))", icon: "https://flagcdn.com/w320/hk.png" },
  { name: "台湾节点", type: "select", "include-all": true, url: "https://www.google.com.tw/generate_204", "expected-status": "200/204/301/302", interval: 300, filter: "(?i)(广台|台湾|台灣|Tai ?Wan|Taiwan|TWN|🇹🇼|(^|[^A-Z])TW([^A-Z]|$))", icon: "https://flagcdn.com/w320/tw.png" },
  { ...URLTEST_BASE, name: "台湾-自动", url: "https://www.google.com.tw/generate_204", "expected-status": "200/204/301/302", filter: "(?i)(广台|台湾|台灣|Tai ?Wan|Taiwan|TWN|🇹🇼|(^|[^A-Z])TW([^A-Z]|$))", icon: "https://flagcdn.com/w320/tw.png" },
  { name: "日本节点", type: "select", "include-all": true, url: "https://www.google.co.jp/generate_204", "expected-status": "200/204/301/302", interval: 300, filter: "(?i)(广日|日本|川日|东京|大阪|泉日|埼玉|沪日|深日|Japan|🇯🇵|(^|[^A-Z])JP([^A-Z]|$))", icon: "https://flagcdn.com/w320/jp.png" },
  { ...URLTEST_BASE, name: "日本-自动", url: "https://www.google.co.jp/generate_204", "expected-status": "200/204/301/302", filter: "(?i)(广日|日本|川日|东京|大阪|泉日|埼玉|沪日|深日|Japan|🇯🇵|(^|[^A-Z])JP([^A-Z]|$))", icon: "https://flagcdn.com/w320/jp.png" },
  { name: "新加坡节点", type: "select", "include-all": true, url: "https://www.google.com.sg/generate_204", "expected-status": "200/204/301/302", interval: 300, filter: "(?i)(广新|新加坡|坡|狮城|Singapore|🇸🇬|(^|[^A-Z])SG([^A-Z]|$))", icon: "https://flagcdn.com/w320/sg.png" },
  { ...URLTEST_BASE, name: "新加坡-自动", url: "https://www.google.com.sg/generate_204", "expected-status": "200/204/301/302", filter: "(?i)(广新|新加坡|坡|狮城|Singapore|🇸🇬|(^|[^A-Z])SG([^A-Z]|$))", icon: "https://flagcdn.com/w320/sg.png" },
  { name: "美国节点", type: "select", "include-all": true, url: "https://www.google.com/generate_204", "expected-status": "200/204/301/302", interval: 300, filter: "(?i)(广美|美国|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|洛杉|圣何塞|圣克拉|西雅|芝加|United States|USA|🇺🇸|(^|[^A-Z])US([^A-Z]|$))", icon: "https://flagcdn.com/w320/us.png" },
  { ...URLTEST_BASE, name: "美国-自动", url: "https://www.google.com/generate_204", "expected-status": "200/204/301/302", filter: "(?i)(广美|美国|纽约|波特兰|达拉斯|俄勒|凤凰城|费利蒙|洛杉|圣何塞|圣克拉|西雅|芝加|United States|USA|🇺🇸|(^|[^A-Z])US([^A-Z]|$))", icon: "https://flagcdn.com/w320/us.png" },
  { name: "韩国节点", type: "select", "include-all": true, url: "https://www.google.co.kr/generate_204", "expected-status": "200/204/301/302", interval: 300, filter: "(?i)(广韩|韩国|韓國|首尔|春川|Korea|🇰🇷|(^|[^A-Z])KR([^A-Z]|$))", icon: "https://flagcdn.com/w320/kr.png" },
  { ...URLTEST_BASE, name: "韩国-自动", url: "https://www.google.co.kr/generate_204", "expected-status": "200/204/301/302", filter: "(?i)(广韩|韩国|韓國|首尔|春川|Korea|🇰🇷|(^|[^A-Z])KR([^A-Z]|$))", icon: "https://flagcdn.com/w320/kr.png" },
  { name: "越南节点", type: "select", "include-all": true, url: "https://zalo.me", "expected-status": "200/301/302", interval: 300, filter: "(?i)(越南|Vietnam|Ho ?Chi ?Minh|HCM|🇻🇳|(^|[^A-Z])VN([^A-Z]|$))", icon: "https://flagcdn.com/w320/vn.png" },
  { ...URLTEST_BASE, name: "越南-自动", url: "https://zalo.me", "expected-status": "200/301/302", filter: "(?i)(越南|Vietnam|Ho ?Chi ?Minh|HCM|🇻🇳|(^|[^A-Z])VN([^A-Z]|$))", icon: "https://flagcdn.com/w320/vn.png" },
  { name: "中国节点", type: "select", "include-all": true, url: "https://www.baidu.com", "expected-status": "200/302", interval: 300, filter: "(?i)(广中|中国|上海|北京|广州|深圳|江苏|浙江|China|🇨🇳|(^|[^A-Z])CN([^A-Z]|$))", icon: "https://flagcdn.com/w320/cn.png" },
  { name: "中国-自动", type: "url-test", interval: 300, tolerance: 50, url: "https://www.baidu.com", "expected-status": "200/302", lazy: true, hidden: true, "include-all": true, filter: "(?i)(广中|中国|上海|北京|广州|深圳|江苏|浙江|China|🇨🇳|(^|[^A-Z])CN([^A-Z]|$))", icon: "https://flagcdn.com/w320/cn.png" },
];


// 远程规则集：与 YAML 的 rule-providers 保持同步。
OVERRIDE["rule-providers"] = {
  reject: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ads-all.mrs", path: "./ruleset/metacubex/category-ads-all.mrs" },
  private: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/private.mrs", path: "./ruleset/metacubex/private.mrs" },
  cn: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.mrs", path: "./ruleset/metacubex/cn.mrs" },
  "geolocation-!cn": { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/geolocation-!cn.mrs", path: "./ruleset/metacubex/geolocation-!cn.mrs" },
  google: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/google.mrs", path: "./ruleset/metacubex/google.mrs" },
  youtube: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/youtube.mrs", path: "./ruleset/metacubex/youtube.mrs" },
  github: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/github.mrs", path: "./ruleset/metacubex/github.mrs" },
  microsoft: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/microsoft.mrs", path: "./ruleset/metacubex/microsoft.mrs" },
  openai: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/openai.mrs", path: "./ruleset/metacubex/openai.mrs" },
  telegram: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/telegram.mrs", path: "./ruleset/metacubex/telegram.mrs" },
  netflix: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/netflix.mrs", path: "./ruleset/metacubex/netflix.mrs" },
  tiktok: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/tiktok.mrs", path: "./ruleset/metacubex/tiktok.mrs" },
  spotify: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/spotify.mrs", path: "./ruleset/metacubex/spotify.mrs" },
  apple: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/apple.mrs", path: "./ruleset/metacubex/apple.mrs" },
  biliintl: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/biliintl.mrs", path: "./ruleset/metacubex/biliintl.mrs" },
twitter: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/twitter.mrs", path: "./ruleset/metacubex/twitter.mrs" },
  facebook: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/facebook.mrs", path: "./ruleset/metacubex/facebook.mrs" },
  steam: { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/steam.mrs", path: "./ruleset/metacubex/steam.mrs" },
  "category-games": { ...META_DOMAIN_PROVIDER, url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-games.mrs", path: "./ruleset/metacubex/category-games.mrs" },
  telegramcidr: { type: "http", behavior: "ipcidr", format: "mrs", interval: 86400, proxy: "节点选择", url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/telegram.mrs", path: "./ruleset/metacubex/telegramcidr.mrs" },
};


// 分流规则文本：与 YAML 的 rules 顺序和内容保持同步。
const RULES_TEXT = `
IP-CIDR,0.0.0.0/8,DIRECT,no-resolve
IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
IP-CIDR,169.254.0.0/16,DIRECT,no-resolve
IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
IP-CIDR,224.0.0.0/4,DIRECT,no-resolve
IP-CIDR,255.255.255.255/32,DIRECT,no-resolve
IP-CIDR6,::1/128,DIRECT,no-resolve
IP-CIDR6,fc00::/7,DIRECT,no-resolve
IP-CIDR6,fe80::/10,DIRECT,no-resolve
DOMAIN-SUFFIX,local,DIRECT
DOMAIN-SUFFIX,lan,DIRECT
RULE-SET,private,DIRECT
GEOIP,LAN,DIRECT,no-resolve
RULE-SET,reject,广告过滤
PROCESS-NAME,com.openai.chatgpt,AI
PROCESS-NAME,com.google.android.apps.bard,AI
PROCESS-NAME,com.anthropic.claude,AI
PROCESS-NAME,ai.perplexity.app.android,AI
PROCESS-NAME,com.microsoft.copilot,AI
PROCESS-NAME,com.twitter.android,Meta / X
PROCESS-NAME,com.facebook.katana,Meta / X
PROCESS-NAME,com.facebook.orca,Meta / X
PROCESS-NAME,com.instagram.android,Meta / X
PROCESS-NAME,com.instagram.barcelona,Meta / X
PROCESS-NAME,org.telegram.messenger,电报消息
PROCESS-NAME,org.telegram.group,电报消息
PROCESS-NAME,com.whatsapp,Meta / X
PROCESS-NAME,com.reddit.frontpage,节点选择
PROCESS-NAME,com.discord,节点选择
PROCESS-NAME,org.thoughtcrime.securesms,节点选择
PROCESS-NAME,jp.naver.line.android,节点选择
PROCESS-NAME,com.snapchat.android,节点选择
PROCESS-NAME,com.pinterest,节点选择
PROCESS-NAME,com.linkedin.android,节点选择
PROCESS-NAME,com.duolingo,节点选择
PROCESS-NAME,com.google.android.googlequicksearchbox,谷歌服务
PROCESS-NAME,com.google.android.apps.maps,谷歌服务
PROCESS-NAME,com.google.android.gm,谷歌服务
PROCESS-NAME,com.google.android.apps.docs,谷歌服务
PROCESS-NAME,com.google.android.apps.translate,谷歌服务
PROCESS-NAME,com.android.vending,谷歌服务
PROCESS-NAME,com.google.android.gms,谷歌服务
PROCESS-NAME,com.google.android.gsf,谷歌服务
PROCESS-NAME,com.google.android.gsf.login,谷歌服务
PROCESS-NAME,com.google.android.partnersetup,谷歌服务
PROCESS-NAME,com.google.android.configupdater,谷歌服务
PROCESS-NAME,com.google.android.onetimeinitializer,谷歌服务
PROCESS-NAME,com.google.android.as.oss,谷歌服务
PROCESS-NAME,com.google.android.contactkeys,谷歌服务
PROCESS-NAME,com.google.android.inputmethod.latin,谷歌服务
PROCESS-NAME,com.google.android.apps.authenticator2,谷歌服务
PROCESS-NAME,com.google.ar.core,谷歌服务
PROCESS-NAME,com.google.android.marvin.talkback,谷歌服务
PROCESS-NAME,com.google.android.accessibility.switchaccess,谷歌服务
PROCESS-NAME,com.google.android.printservice.recommendation,谷歌服务
PROCESS-NAME,com.google.android.apps.photos,谷歌服务
PROCESS-NAME,com.google.android.calendar,谷歌服务
PROCESS-NAME,com.google.android.projection.gearhead,谷歌服务
PROCESS-NAME,com.google.earth,谷歌服务
PROCESS-NAME,com.microsoft.appmanager,微软服务
PROCESS-NAME,com.microsoft.deviceintegrationservice,微软服务
PROCESS-NAME,com.microsoftsdk.crossdeviceservicebroker,微软服务
PROCESS-NAME,com.tencent.mobileqq,国内服务
PROCESS-NAME,com.tencent.tim,国内服务
PROCESS-NAME,com.tencent.soter.soterserver,国内服务
PROCESS-NAME,com.sina.weibo,国内服务
PROCESS-NAME,com.zhihu.android,国内服务
PROCESS-NAME,com.taobao.taobao,国内服务
PROCESS-NAME,com.tmall.wireless,国内服务
PROCESS-NAME,com.jingdong.app.mall,国内服务
PROCESS-NAME,com.xunmeng.pinduoduo,国内服务
PROCESS-NAME,me.ele,国内服务
PROCESS-NAME,com.sankuai.meituan,国内服务
PROCESS-NAME,com.sankuai.meituan.takeoutnew,国内服务
PROCESS-NAME,com.dianping.v1,国内服务
PROCESS-NAME,ctrip.android.view,国内服务
PROCESS-NAME,com.Qunar,国内服务
PROCESS-NAME,com.autonavi.minimap,国内服务
PROCESS-NAME,com.baidu.BaiduMap,国内服务
PROCESS-NAME,com.sdu.didi.psnger,国内服务
PROCESS-NAME,com.MobileTicket,国内服务
PROCESS-NAME,com.unionpay,国内服务
PROCESS-NAME,com.ss.android.ugc.aweme,国内服务
PROCESS-NAME,com.ss.android.ugc.aweme.mobile,国内服务
PROCESS-NAME,com.ss.android.ugc.aweme.lite,国内服务
PROCESS-NAME,com.smile.gifmaker,国内服务
PROCESS-NAME,com.kuaishou.nebula,国内服务
PROCESS-NAME,com.xingin.xhs,国内服务
PROCESS-NAME,com.youku.phone,国内服务
PROCESS-NAME,com.qiyi.video,国内服务
PROCESS-NAME,com.tencent.qqlive,国内服务
PROCESS-NAME,com.ss.android.article.news,国内服务
PROCESS-NAME,com.netease.cloudmusic,国内服务
PROCESS-NAME,com.tencent.qqmusic,国内服务
PROCESS-NAME,com.kugou.android,国内服务
PROCESS-NAME,com.icbc,国内服务
PROCESS-NAME,com.chinamworld.main,国内服务
PROCESS-NAME,com.cmbchina.ccd.pluto.cmbActivity,国内服务
PROCESS-NAME,com.greenpoint.android.mc10086.activity,国内服务
PROCESS-NAME,com.sinovatech.unicom.ui,国内服务
PROCESS-NAME,com.ct.client,国内服务
PROCESS-NAME,com.tencent.wework,国内服务
PROCESS-NAME,com.alibaba.android.rimet,国内服务
PROCESS-NAME,com.ss.android.lark,国内服务
PROCESS-NAME,com.baidu.netdisk,国内服务
PROCESS-NAME,com.tencent.weiyun,国内服务
PROCESS-NAME,cn.wps.moffice_eng,国内服务
PROCESS-NAME,com.tencent.androidqqmail,国内服务
PROCESS-NAME,com.tencent.wemeet.app,国内服务
PROCESS-NAME,com.taobao.idlefish,国内服务
PROCESS-NAME,com.achievo.vipshop,国内服务
PROCESS-NAME,com.alibaba.wireless,国内服务
PROCESS-NAME,com.cainiao.wireless,国内服务
PROCESS-NAME,com.fcbox.hiveconsumer,国内服务
PROCESS-NAME,com.intsig.camscanner,国内服务
PROCESS-NAME,com.manmanbuy.bijia,国内服务
PROCESS-NAME,com.max.xiaoheihe,国内服务
PROCESS-NAME,com.umetrip.android.msky.app,国内服务
PROCESS-NAME,com.oneplus.bbs,国内服务
PROCESS-NAME,com.oneplus.member,国内服务
PROCESS-NAME,com.oppo.store,国内服务
PROCESS-NAME,com.heytap.market,国内服务
PROCESS-NAME,com.heytap.browser,国内服务
PROCESS-NAME,com.nearme.instant.platform,国内服务
PROCESS-NAME,com.netease.uuremote,国内服务
PROCESS-NAME,com.lptiyu.tanke,国内服务
PROCESS-NAME,com.deepseek.chat,国内服务
PROCESS-NAME,com.larus.nova,国内服务
PROCESS-NAME,com.tencent.tmgp.cf,国内服务
PROCESS-NAME,com.x7890.shortcutcreator,国内服务
PROCESS-NAME,com.tryfun.intelligent,国内服务
PROCESS-NAME,com.ktls.fileinfo,国内服务
PROCESS-NAME,com.jingcai.apps.qualitydev,国内服务
PROCESS-NAME,com.dragon.read,国内服务
PROCESS-NAME,com.example.gxcs_app,国内服务
PROCESS-NAME,com.jingyao.easybike,国内服务
PROCESS-NAME,com.cmic.heduohao,国内服务
PROCESS-NAME,com.lemon.lv,国内服务
PROCESS-NAME,com.ksjhaoka.a,国内服务
PROCESS-NAME,com.coolapk.market,国内服务
PROCESS-NAME,com.taou.maimai,国内服务
PROCESS-NAME,com.eusoft.ting.en,国内服务
PROCESS-NAME,com.mt.mtxx.mtxx,国内服务
PROCESS-NAME,com.midea.connect,国内服务
PROCESS-NAME,com.job.android,国内服务
PROCESS-NAME,com.redteamobile.roaming,国内服务
PROCESS-NAME,com.tianyancha.skyeye,国内服务
PROCESS-NAME,com.newcapec.mobile.ncp,国内服务
PROCESS-NAME,com.tencent.weread,国内服务
PROCESS-NAME,com.mi.health,国内服务
PROCESS-NAME,com.xt.retouch,国内服务
PROCESS-NAME,com.iflytek.inputmethod,国内服务
PROCESS-NAME,com.chaoxing.mobile,国内服务
PROCESS-NAME,cn.com.chsi.chsiapp,国内服务
PROCESS-NAME,com.youdao.dict,国内服务
PROCESS-NAME,com.maxframing.mipad,国内服务
PROCESS-NAME,com.able.wisdomtree,国内服务
PROCESS-NAME,com.fifedu.fifiplat,国内服务
PROCESS-NAME,com.zte.smarthome,国内服务
PROCESS-NAME,com.netease.mail,国内服务
PROCESS-NAME,com.jd.jrapp,国内服务
PROCESS-NAME,com.xiaomi.smarthome,国内服务
PROCESS-NAME,com.xiaomi.shop,国内服务
PROCESS-NAME,com.xiaomi.market,国内服务
PROCESS-NAME,com.xiaomi.vipaccount,国内服务
PROCESS-NAME,cn.wps.moffice_eng.xiaomi.lite,国内服务
PROCESS-NAME,com.iflytek.inputmethod.miui,国内服务
PROCESS-NAME,com.sohu.inputmethod.sogou.xiaomi,国内服务
PROCESS-NAME,com.heytap.health,国内服务
PROCESS-NAME,com.heytap.themestore,国内服务
PROCESS-NAME,com.oplus.member,国内服务
PROCESS-NAME,com.cnspeedtest.globalspeed,国内服务
PROCESS-NAME,com.chinamworld.bocmbci,国内服务
PROCESS-NAME,com.bankcomm.Bankcomm,国内服务
PROCESS-NAME,cn.com.spdb.mobilebank.per,国内服务
PROCESS-NAME,cmb.pb,国内服务
PROCESS-NAME,com.kingpoint.gmcchh,国内服务
PROCESS-NAME,cn.gov.pbc.dcep,国内服务
PROCESS-NAME,cn.gov.tax.its,国内服务
PROCESS-NAME,com.cdb.sla,国内服务
PROCESS-NAME,cn.cyberIdentity.certification,国内服务
PROCESS-NAME,com.sohu.inputmethod.sogouoem,国内服务
PROCESS-NAME,com.android.browser,国内服务
PROCESS-NAME,com.finshell.wallet,国内服务
PROCESS-NAME,com.unionpay.tsmservice,国内服务
PROCESS-NAME,com.heytap.cloud,国内服务
PROCESS-NAME,com.heytap.mcs,国内服务
PROCESS-NAME,com.heytap.openid,国内服务
PROCESS-NAME,com.heytap.vip,国内服务
PROCESS-NAME,com.heytap.htms,国内服务
PROCESS-NAME,com.heytap.tas,国内服务
PROCESS-NAME,com.heytap.accessory,国内服务
PROCESS-NAME,com.heytap.mydevices,国内服务
PROCESS-NAME,com.heytap.opluscarlink,国内服务
PROCESS-NAME,andes.oplus.documentsreader,国内服务
PROCESS-NAME,com.coloros.findmyphone,国内服务
PROCESS-NAME,com.coloros.oshare,国内服务
PROCESS-NAME,com.coloros.phonemanager,国内服务
PROCESS-NAME,com.coloros.filemanager,国内服务
PROCESS-NAME,com.coloros.gallery3d,国内服务
PROCESS-NAME,com.coloros.weather2,国内服务
PROCESS-NAME,com.coloros.weather.service,国内服务
PROCESS-NAME,com.coloros.note,国内服务
PROCESS-NAME,com.coloros.calendar,国内服务
PROCESS-NAME,com.coloros.video,国内服务
PROCESS-NAME,com.coloros.backuprestore,国内服务
PROCESS-NAME,com.coloros.remoteguardservice,国内服务
PROCESS-NAME,com.coloros.operationManual,国内服务
PROCESS-NAME,com.coloros.assistantscreen,国内服务
PROCESS-NAME,com.coloros.translate,国内服务
PROCESS-NAME,com.oplus.account,国内服务
PROCESS-NAME,com.oplus.vip,国内服务
PROCESS-NAME,com.oplus.ota,国内服务
PROCESS-NAME,com.oplus.romupdate,国内服务
PROCESS-NAME,com.oplus.sau,国内服务
PROCESS-NAME,com.oplus.cota,国内服务
PROCESS-NAME,com.oplus.apprecover,国内服务
PROCESS-NAME,com.oplus.pay,国内服务
PROCESS-NAME,com.oplus.safecenter,国内服务
PROCESS-NAME,com.oplus.games,国内服务
PROCESS-NAME,com.oplus.ocar,国内服务
PROCESS-NAME,com.oplus.linker,国内服务
PROCESS-NAME,com.oplus.cast,国内服务
PROCESS-NAME,com.oplus.remotecontrol,国内服务
PROCESS-NAME,com.oplus.dfs,国内服务
PROCESS-NAME,com.oplus.melody,国内服务
PROCESS-NAME,com.oplus.location,国内服务
PROCESS-NAME,com.oplus.acc.gac,国内服务
PROCESS-NAME,com.oplus.networksense,国内服务
PROCESS-NAME,com.oplus.nas,国内服务
PROCESS-NAME,com.oplus.nhs,国内服务
PROCESS-NAME,com.oplus.beaconlink,国内服务
PROCESS-NAME,com.oplus.healthservice,国内服务
PROCESS-NAME,com.oplus.aiwriter,国内服务
PROCESS-NAME,com.oplus.aiunit,国内服务
PROCESS-NAME,com.oplus.aicall,国内服务
PROCESS-NAME,com.oplus.aimemory,国内服务
PROCESS-NAME,com.oplus.owork,国内服务
PROCESS-NAME,com.newcall,国内服务
PROCESS-NAME,com.ted.number,国内服务
PROCESS-NAME,com.opos.ads,国内服务
PROCESS-NAME,com.xiaomi.xmsf,国内服务
PROCESS-NAME,com.xiaomi.account,国内服务
PROCESS-NAME,com.miui.cloudservice,国内服务
PROCESS-NAME,com.miui.cloudbackup,国内服务
PROCESS-NAME,com.miui.micloudsync,国内服务
PROCESS-NAME,com.xiaomi.micloud.sdk,国内服务
PROCESS-NAME,com.miui.newmidrive,国内服务
PROCESS-NAME,com.xiaomi.finddevice,国内服务
PROCESS-NAME,com.miui.findmy,国内服务
PROCESS-NAME,com.xiaomi.mi_connect_service,国内服务
PROCESS-NAME,com.miui.mishare.connectivity,国内服务
PROCESS-NAME,com.xiaomi.mirror,国内服务
PROCESS-NAME,com.milink.service,国内服务
PROCESS-NAME,com.xiaomi.payment,国内服务
PROCESS-NAME,com.miui.weather2,国内服务
PROCESS-NAME,com.miui.gallery,国内服务
PROCESS-NAME,com.miui.notes,国内服务
PROCESS-NAME,com.miui.securitycenter,国内服务
PROCESS-NAME,com.miui.securitymanager,国内服务
PROCESS-NAME,com.miui.packageinstaller,国内服务
PROCESS-NAME,com.miui.hybrid,国内服务
PROCESS-NAME,com.xiaomi.gamecenter.sdk.service,国内服务
PROCESS-NAME,com.xiaomi.migameservice,国内服务
PROCESS-NAME,com.xiaomi.minigame,国内服务
PROCESS-NAME,com.miui.yellowpage,国内服务
PROCESS-NAME,com.miui.bugreport,国内服务
PROCESS-NAME,com.miui.personalassistant,国内服务
PROCESS-NAME,com.xiaomi.mibrain.speech,国内服务
PROCESS-NAME,com.miui.voiceassist,国内服务
PROCESS-NAME,com.miui.voiceassistProxy,国内服务
PROCESS-NAME,com.xiaomi.scanner,国内服务
PROCESS-NAME,com.miui.cleanmaster,国内服务
PROCESS-NAME,com.xiaomi.ugd,国内服务
PROCESS-NAME,com.android.updater,国内服务
PROCESS-NAME,com.lbe.security.miui,国内服务
PROCESS-NAME,com.miuix.editor,国内服务
PROCESS-NAME,com.mobiletools.systemhelper,国内服务
PROCESS-NAME,com.google.android.youtube,YouTube
PROCESS-NAME,com.google.android.apps.youtube.music,YouTube
PROCESS-NAME,com.google.android.apps.youtube.kids,YouTube
PROCESS-NAME,com.netflix.mediaclient,Netflix
PROCESS-NAME,com.spotify.music,Spotify
PROCESS-NAME,com.zhiliaoapp.musically,TikTok
PROCESS-NAME,tv.twitch.android.app,节点选择
PROCESS-NAME,tv.danmaku.bili,哔哩哔哩港澳台
PROCESS-NAME,com.bstar.intl,哔哩哔哩港澳台
PROCESS-NAME,com.github.android,GitHub
PROCESS-NAME,com.valvesoftware.android.steam.community,游戏平台
PROCESS-NAME,zed.rainxch.githubstore,GitHub
PROCESS-NAME,com.zing.zalo,越南服务
PROCESS-NAME,com.shopee.vn,越南服务
PROCESS-NAME,com.grabtaxi.passenger,越南服务
PROCESS-NAME,xyz.be.customer,越南服务
PROCESS-NAME,com.jtexpress.customer.vn,越南服务
PROCESS-NAME,com.viettel.ViettelPost,越南服务
PROCESS-NAME,com.vnp.myvinaphone,越南服务
PROCESS-NAME,org.zwanoo.android.speedtest,节点选择
PROCESS-NAME,com.mynat.android,节点选择
PROCESS-NAME,com.eup.hanzii,节点选择
PROCESS-NAME,ChatGPT.exe,AI
PROCESS-NAME,Claude.exe,AI
PROCESS-NAME,Perplexity.exe,AI
PROCESS-NAME,Copilot.exe,AI
PROCESS-NAME,Codex.exe,AI
PROCESS-NAME,codex.exe,AI
PROCESS-NAME,codex,AI
PROCESS-NAME,Telegram.exe,电报消息
PROCESS-NAME,Discord.exe,节点选择
PROCESS-NAME,WhatsApp.exe,Meta / X
PROCESS-NAME,Signal.exe,节点选择
PROCESS-NAME,LINE.exe,节点选择
PROCESS-NAME,Messenger.exe,Meta / X
PROCESS-NAME,Zalo.exe,越南服务
PROCESS-NAME,Zalo,越南服务
PROCESS-NAME,WeChat.exe,国内服务
PROCESS-NAME,WeChatAppEx.exe,国内服务
PROCESS-NAME,Weixin.exe,国内服务
PROCESS-NAME,QQ.exe,国内服务
PROCESS-NAME,TIM.exe,国内服务
PROCESS-NAME,DingTalk.exe,国内服务
PROCESS-NAME,WXWork.exe,国内服务
PROCESS-NAME,Feishu.exe,国内服务
PROCESS-NAME,Lark.exe,节点选择
PROCESS-NAME,wps.exe,国内服务
PROCESS-NAME,et.exe,国内服务
PROCESS-NAME,wpp.exe,国内服务
PROCESS-NAME,baidunetdisk.exe,国内服务
PROCESS-NAME,BaiduNetdisk.exe,国内服务
PROCESS-NAME,AliYunDrive.exe,国内服务
PROCESS-NAME,QuarkCloudDrive.exe,国内服务
PROCESS-NAME,TencentMeeting.exe,国内服务
PROCESS-NAME,WeMeetApp.exe,国内服务
PROCESS-NAME,NeteaseMailMaster.exe,国内服务
PROCESS-NAME,QQMail.exe,国内服务
PROCESS-NAME,cloudmusic.exe,国内服务
PROCESS-NAME,QQMusic.exe,国内服务
PROCESS-NAME,KuGou.exe,国内服务
PROCESS-NAME,KuwoMusic.exe,国内服务
PROCESS-NAME,iQIYI.exe,国内服务
PROCESS-NAME,Youku.exe,国内服务
PROCESS-NAME,QQLive.exe,国内服务
PROCESS-NAME,Douyin.exe,国内服务
PROCESS-NAME,JianyingPro.exe,国内服务
PROCESS-NAME,CapCut.exe,节点选择
PROCESS-NAME,SogouInput.exe,国内服务
PROCESS-NAME,SogouImeBroker.exe,国内服务
PROCESS-NAME,iFlyIME.exe,国内服务
PROCESS-NAME,LenovoVantage.exe,国内服务
PROCESS-NAME,Lenovo.Modern.ImController.exe,国内服务
PROCESS-NAME,HuaweiPCManager.exe,国内服务
PROCESS-NAME,MiService.exe,国内服务
PROCESS-NAME,MiPhoneManager.exe,国内服务
PROCESS-NAME,OPPOPCSuite.exe,国内服务
PROCESS-NAME,OnePlusPCSuite.exe,国内服务
PROCESS-NAME,Spotify.exe,Spotify
PROCESS-NAME,steam.exe,游戏平台
PROCESS-NAME,steamwebhelper.exe,游戏平台
PROCESS-NAME,GitHubDesktop.exe,GitHub
PROCESS-NAME,Cursor.exe,AI
PROCESS-NAME,Windsurf.exe,AI
PROCESS-NAME,Code.exe,节点选择
PROCESS-NAME,code.exe,节点选择
PROCESS-NAME,Postman.exe,节点选择
PROCESS-NAME,JetBrains Toolbox.exe,节点选择
PROCESS-NAME,idea64.exe,节点选择
PROCESS-NAME,pycharm64.exe,节点选择
PROCESS-NAME,webstorm64.exe,节点选择
PROCESS-NAME,EpicGamesLauncher.exe,游戏平台
PROCESS-NAME,EpicWebHelper.exe,游戏平台
PROCESS-NAME,Battle.net.exe,游戏平台
PROCESS-NAME,RiotClientServices.exe,游戏平台
PROCESS-NAME,UbisoftConnect.exe,游戏平台
PROCESS-NAME,EA app.exe,游戏平台
PROCESS-NAME,EADesktop.exe,游戏平台
PROCESS-NAME,ms-teams.exe,节点选择
PROCESS-NAME,Teams.exe,节点选择
PROCESS-NAME,Zoom.exe,节点选择
PROCESS-NAME,slack.exe,节点选择
PROCESS-NAME,NVIDIA App.exe,节点选择
PROCESS-NAME,NVIDIA GeForce Experience.exe,节点选择
PROCESS-NAME,NvContainer.exe,节点选择
PROCESS-NAME,AMDSoftware.exe,节点选择
PROCESS-NAME,AMDRSServ.exe,节点选择
PROCESS-NAME,Intel Driver & Support Assistant.exe,节点选择
PROCESS-NAME,aria2c,DIRECT
PROCESS-NAME,aria2c.exe,DIRECT
PROCESS-NAME,BitComet,DIRECT
PROCESS-NAME,BitComet.exe,DIRECT
PROCESS-NAME,qBittorrent,DIRECT
PROCESS-NAME,qbittorrent.exe,DIRECT
PROCESS-NAME,Transmission,DIRECT
PROCESS-NAME,transmission-daemon,DIRECT
PROCESS-NAME,utorrent,DIRECT
PROCESS-NAME,uTorrent.exe,DIRECT
PROCESS-NAME,Thunder,DIRECT
PROCESS-NAME,Xunlei,DIRECT
DOMAIN-SUFFIX,chatgpt.com,AI
DOMAIN-SUFFIX,openai.com,AI
DOMAIN-SUFFIX,oaistatic.com,AI
DOMAIN-SUFFIX,oaiusercontent.com,AI
DOMAIN-SUFFIX,auth0.com,AI
DOMAIN-SUFFIX,statsigapi.net,AI
DOMAIN-SUFFIX,intercom.io,AI
DOMAIN-SUFFIX,intercomcdn.com,AI
RULE-SET,openai,AI
DOMAIN,accounts.google.com,谷歌服务
DOMAIN-SUFFIX,accounts.google.com,谷歌服务
DOMAIN-SUFFIX,accounts.youtube.com,谷歌服务
DOMAIN,play.google.com,谷歌服务
DOMAIN,dl.google.com,谷歌服务
DOMAIN,dl-ssl.google.com,谷歌服务
DOMAIN,android.apis.google.com,谷歌服务
DOMAIN,android.clients.google.com,谷歌服务
DOMAIN,android.googleapis.com,谷歌服务
DOMAIN-SUFFIX,googleapis.cn,谷歌服务
DOMAIN-SUFFIX,gstatic.com,谷歌服务
DOMAIN-SUFFIX,googleusercontent.com,谷歌服务
DOMAIN-SUFFIX,gvt1.com,谷歌服务
DOMAIN-SUFFIX,gvt2.com,谷歌服务
DOMAIN-SUFFIX,gvt3.com,谷歌服务
DOMAIN-SUFFIX,ggpht.com,谷歌服务
DOMAIN-SUFFIX,xn--ngstr-lra8j.com,谷歌服务
DOMAIN,mtalk.google.com,谷歌服务
RULE-SET,youtube,YouTube
RULE-SET,google,谷歌服务
DOMAIN-SUFFIX,github.io,GitHub
DOMAIN,v2rayse.com,GitHub
RULE-SET,github,GitHub
DOMAIN-SUFFIX,displaycatalog.mp.microsoft.com,微软服务
DOMAIN-SUFFIX,delivery.mp.microsoft.com,微软服务
DOMAIN-SUFFIX,dl.delivery.mp.microsoft.com,微软服务
DOMAIN-SUFFIX,prod.do.dsp.mp.microsoft.com,微软服务
DOMAIN-SUFFIX,do.dsp.mp.microsoft.com,微软服务
DOMAIN-SUFFIX,windowsupdate.com,微软服务
DOMAIN-SUFFIX,update.microsoft.com,微软服务
DOMAIN-SUFFIX,download.windowsupdate.com,微软服务
DOMAIN-SUFFIX,mp.microsoft.com,微软服务
DOMAIN-SUFFIX,wns.windows.com,微软服务
DOMAIN-SUFFIX,windows.com,微软服务
DOMAIN-SUFFIX,msedge.net,微软服务
DOMAIN-SUFFIX,microsoft.com,微软服务
DOMAIN-SUFFIX,microsoftonline.com,微软服务
DOMAIN-SUFFIX,msauth.net,微软服务
DOMAIN-SUFFIX,live.com,微软服务
DOMAIN-SUFFIX,storecatalogrevocation.storequality.microsoft.com,微软服务
DOMAIN-SUFFIX,img-prod-cms-rt-microsoft-com.akamaized.net,微软服务
DOMAIN-SUFFIX,img-s-msn-com.akamaized.net,微软服务
DOMAIN-SUFFIX,manage.devcenter.microsoft.com,微软服务
DOMAIN-SUFFIX,share.microsoft.com,微软服务
DOMAIN-SUFFIX,pipe.aria.microsoft.com,微软服务
DOMAIN-SUFFIX,api.cdp.microsoft.com,微软服务
DOMAIN,storeedgefd.dsx.mp.microsoft.com,微软服务
DOMAIN,livetileedge.dsx.mp.microsoft.com,微软服务
DOMAIN,licensing.mp.microsoft.com,微软服务
DOMAIN,tsfe.trafficshaping.dsp.mp.microsoft.com,微软服务
DOMAIN,adl.windows.com,微软服务
DOMAIN,ctldl.windowsupdate.com,微软服务
DOMAIN,definitionupdates.microsoft.com,微软服务
DOMAIN,msedge.api.cdp.microsoft.com,微软服务
RULE-SET,microsoft,微软服务
RULE-SET,telegram,电报消息
RULE-SET,telegramcidr,电报消息,no-resolve
DOMAIN-SUFFIX,x.com,Meta / X
DOMAIN-SUFFIX,twitter.com,Meta / X
DOMAIN-SUFFIX,t.co,Meta / X
DOMAIN-SUFFIX,twimg.com,Meta / X
DOMAIN-SUFFIX,facebook.com,Meta / X
DOMAIN-SUFFIX,facebook.net,Meta / X
DOMAIN-SUFFIX,fbcdn.net,Meta / X
DOMAIN-SUFFIX,messenger.com,Meta / X
DOMAIN-SUFFIX,instagram.com,Meta / X
DOMAIN-SUFFIX,cdninstagram.com,Meta / X
DOMAIN-SUFFIX,threads.net,Meta / X
DOMAIN-SUFFIX,whatsapp.com,Meta / X
DOMAIN-SUFFIX,whatsapp.net,Meta / X
RULE-SET,twitter,Meta / X
RULE-SET,facebook,Meta / X
DOMAIN-SUFFIX,steampowered.com,游戏平台
DOMAIN-SUFFIX,steamcommunity.com,游戏平台
DOMAIN-SUFFIX,steamstatic.com,游戏平台
DOMAIN-SUFFIX,steamcontent.com,游戏平台
DOMAIN-SUFFIX,epicgames.com,游戏平台
DOMAIN-SUFFIX,epicgamescdn.com,游戏平台
DOMAIN-SUFFIX,battle.net,游戏平台
DOMAIN-SUFFIX,blizzard.com,游戏平台
DOMAIN-SUFFIX,riotgames.com,游戏平台
DOMAIN-SUFFIX,ubisoft.com,游戏平台
DOMAIN-SUFFIX,ea.com,游戏平台
RULE-SET,steam,游戏平台
RULE-SET,category-games,游戏平台
RULE-SET,netflix,Netflix
RULE-SET,tiktok,TikTok
RULE-SET,spotify,Spotify
RULE-SET,apple,苹果服务
RULE-SET,biliintl,哔哩哔哩港澳台
DOMAIN-KEYWORD,midea,DIRECT
DOMAIN-SUFFIX,zalo.me,越南服务
DOMAIN-SUFFIX,zaloapp.com,越南服务
DOMAIN-KEYWORD,zalo,越南服务
DOMAIN-SUFFIX,grab.com,越南服务
DOMAIN-KEYWORD,grab,越南服务
DOMAIN-SUFFIX,gojek.com,越南服务
DOMAIN-KEYWORD,gojek,越南服务
DOMAIN-KEYWORD,tiki,越南服务
DOMAIN-KEYWORD,zing,越南服务
DOMAIN-SUFFIX,nhaccuatui.com,越南服务
DOMAIN-SUFFIX,vnexpress.net,越南服务
DOMAIN-KEYWORD,momo,越南服务
DOMAIN-KEYWORD,zalopay,越南服务
DOMAIN-SUFFIX,vn,越南服务
DOMAIN-SUFFIX,com.vn,越南服务
DOMAIN-SUFFIX,net.vn,越南服务
DOMAIN-SUFFIX,org.vn,越南服务
DOMAIN-SUFFIX,edu.vn,越南服务
DOMAIN-SUFFIX,gov.vn,越南服务
DOMAIN-SUFFIX,biz.vn,越南服务
DOMAIN-SUFFIX,info.vn,越南服务
DOMAIN-SUFFIX,name.vn,越南服务
DOMAIN-SUFFIX,pro.vn,越南服务
DOMAIN-SUFFIX,baomoi.com,越南服务
DOMAIN-SUFFIX,thegioididong.com,越南服务
DOMAIN-SUFFIX,dienmayxanh.com,越南服务
DOMAIN-SUFFIX,bachhoaxanh.com,越南服务
DOMAIN-SUFFIX,gearvn.com,越南服务
DOMAIN-SUFFIX,nguyenkim.com,越南服务
DOMAIN-SUFFIX,hoanghamobile.com,越南服务
DOMAIN-SUFFIX,ahamove.com,越南服务
DOMAIN-KEYWORD,baemin,越南服务
DOMAIN-KEYWORD,shopeefood,越南服务
DOMAIN-SUFFIX,fpt.net,越南服务
DOMAIN-SUFFIX,ghnexpress.com,越南服务
DOMAIN-SUFFIX,vietnamairlines.com,越南服务
DOMAIN-SUFFIX,vietjetair.com,越南服务
DOMAIN-SUFFIX,bambooairways.com,越南服务
DOMAIN-SUFFIX,vexere.com,越南服务
DOMAIN-SUFFIX,traveloka.com,越南服务
DOMAIN-SUFFIX,chotot.com,越南服务
DOMAIN-SUFFIX,muaban.net,越南服务
DOMAIN-SUFFIX,vietnamworks.com,越南服务
GEOIP,VN,越南服务,no-resolve
DOMAIN-SUFFIX,yhglobal.com,国内服务
DOMAIN-SUFFIX,coolapk.com,国内服务
DOMAIN-SUFFIX,www.coolapk.com,国内服务
DOMAIN-SUFFIX,m.coolapk.com,国内服务
DOMAIN-KEYWORD,coolapk,国内服务
RULE-SET,cn,国内服务
GEOIP,CN,国内服务,no-resolve
RULE-SET,geolocation-!cn,漏网之鱼
MATCH,漏网之鱼
`;


// 将 RULES_TEXT 转为 rules 数组，过滤空行。
OVERRIDE.rules = RULES_TEXT
  .split("\n")
  .map((rule) => rule.trim())
  .filter(Boolean);


// 深拷贝，避免直接污染输入 config。
function deepClone(value) {
  return JSON.parse(JSON.stringify(value));
}


// 入口函数：客户端调用 main(config)，返回覆写后的配置。
function main(config) {
  const next = deepClone(OVERRIDE);
  Object.assign(config, next);
  return config;
}
