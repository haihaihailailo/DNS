# Mihomo DNS 防泄露配置

面向 Mihomo / Clash Meta / Clash Party / Mihomo Party / Stash 的个人 DNS 防泄露、fake-ip、TUN 接管、IPv6 与规则分流配置。

## 文件

- `防DNS泄露.yaml`：主配置，适合 Mihomo / Clash Meta / Clash Party / Mihomo Party 的 YAML 覆写或配置片段使用。
- `防DNS泄露.js`：JavaScript 覆写版本，适合 Clash Party / Mihomo Party 的 JS 覆写功能使用。
- `stash.stoverride`：Stash 覆写配置，适合 Stash 的 override 导入使用。

## 功能

- DNS 防泄露：启用 `respect-rules`，按规则分流 DNS 请求。
- IPv6：各版本均保持 IPv6 开启，适合需要 IPv6 可用性的网络环境。
- fake-ip：显式使用 `fake-ip-filter-mode: blacklist`，对局域网、路由器、NTP、推送等域名返回真实 IP，降低局域网和系统服务异常概率。
- TUN 接管：主配置启用 TUN DNS 劫持，并绕过局域网地址、微信、支付宝等关键国内应用。
- Stash 适配：提供 `stash.stoverride`，保留 DNS、Sniffer、策略组、规则集和分流规则。
- Sniffer 稳定性：对局域网、路由器、NTP、Apple Push、QQ/微信本地登录等域名配置 `skip-domain`，避免被嗅探误改写目标。
- 规则分流：覆盖国内、越南、AI、Google、YouTube、GitHub、微软、Telegram、Netflix、TikTok、Spotify、Apple、哔哩哔哩港澳台等常见场景。
- 国内服务保护：国内应用、小程序、支付、系统服务优先直连，避免进入漏网之鱼导致加载异常。

## 使用方法

### YAML 覆写

适合支持 YAML 覆写、配置片段或 merge/override 的客户端。

1. 复制 `防DNS泄露.yaml` 的内容。
2. 在客户端的覆写/扩展配置中粘贴或引用该文件。
3. 更新订阅后检查策略组是否出现 `节点选择`、`漏网之鱼`、`国内服务`、`越南服务`、`AI`、`谷歌服务` 等分组。
4. 运行一次配置测试，确认无 YAML 解析错误和规则引用错误。

### JavaScript 覆写

适合支持 JavaScript override 的 Clash Party / Mihomo Party 客户端。

1. 复制 `防DNS泄露.js` 的内容。
2. 在客户端中新建 JavaScript 覆写。
3. 确认入口函数为 `main(config)`，并返回修改后的 `config`。
4. 更新订阅后检查 DNS、TUN、Sniffer、策略组和规则是否生效。

### Stash 覆写

适合 Stash 客户端。

1. 使用 `stash.stoverride`。
2. 在 Stash 的 Override / 覆写配置中导入。
3. 更新订阅后检查 DNS、Sniffer、策略组、规则集和分流规则是否生效。

## 使用注意

- 本配置默认启用 fake-ip 和 IPv6；主配置还启用 TUN DNS 劫持，建议先备份原客户端配置。
- Android 场景下，微信和支付宝已通过 `tun.exclude-package` 绕过 TUN，减少支付、小程序、扫码登录异常。
- Stash 版本不建议直接照搬主配置的 `tun` 段，应交给客户端管理隧道。
- 国内服务、系统更新、局域网、NTP、推送等规则优先直连，避免误入代理导致加载异常。
- 越南服务独立分组，适合 Zalo、Grab、Shopee 越南、越南航空/票务/本地站点等场景。
- `midea` 相关域名固定直连，避免客户/工作相关系统误走代理。
- 如修改策略组名称，必须同步修改 `rules`、`nameserver-policy`、JS 覆写版本和 Stash 覆写版本。

## 维护口径

- `防DNS泄露.yaml` 是主配置。
- `防DNS泄露.js` 与主 YAML 保持功能同步。
- `stash.stoverride` 是 Stash 专用版本，保留 DNS、Sniffer、策略组、规则集和规则分流，并保持 IPv6 开启。
- 以后修改主配置时，需要同步检查 JS 和 Stash 两类覆写文件。
- CI 会自动校验主 YAML 解析、主 JS 语法、主 YAML/JS 关键配置同步、规则引用完整性、Stash 覆写解析和 mihomo 加载测试。
- CI 会检查 `unified-delay`、`profile`、`geo-auto-update`、`geo-update-interval`、`tcp-concurrent`、`sniffer`、`tun`、`dns`、`proxy-groups`、`rule-providers`、`rules` 是否在主 YAML 和主 JS 中保持一致。
- CI 每周自动运行一次，用于提前发现 mihomo 最新版本、远程规则集或下载链路变化导致的问题。
- Dependabot 会每周检查 GitHub Actions 依赖更新。
