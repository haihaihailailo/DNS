# Mihomo DNS 防泄露配置

面向 Mihomo / Clash Meta / Clash Party / Mihomo Party / Stash / Shadowrocket 的个人 DNS 防泄露、fake-ip、TUN 接管、IPv6 与规则分流配置。

## 文件

- `防DNS泄露.yaml`：主配置，适合 Mihomo / Clash Meta / Clash Party / Mihomo Party 的 YAML 覆写或配置片段使用。
- `防DNS泄露.js`：JavaScript 覆写版本，适合 Clash Party / Mihomo Party 的 JS 覆写功能使用。
- `stash.stoverride`：Stash 覆写配置，适合 Stash 的 override 导入使用。
- `shadowrocket.conf`：Shadowrocket 专用配置，策略组、回国节点关键词和测速端点单独按其语法维护。

## 功能

- DNS 防泄露：Mihomo 启用 `respect-rules`，国内域名使用国内 DoH，外部域名的公共 DoH 跟随 `节点选择`，代理节点域名另走加密启动 DNS，避免递归。Stash 使用 `follow-rule` 与独立的代理节点 DNS；Shadowrocket 主、备用 DNS 均使用 DoH，备用公共 DoH 强制经代理。
- IPv6：覆写不强制开启或关闭 IPv6，跟随客户端/软件自身设置。
- fake-ip：显式使用 `fake-ip-filter-mode: blacklist`，对局域网、路由器、NTP、推送等域名返回真实 IP，降低局域网和系统服务异常概率。
- TUN 接管：主配置启用 TUN DNS 劫持，并绕过局域网地址；国内应用由包名和域名规则精确分流。
- Stash 适配：提供 `stash.stoverride`，保留 DNS、Sniffer、策略组、规则集和分流规则。
- Sniffer 稳定性：对局域网、路由器、NTP、Apple Push、QQ/微信本地登录等域名配置 `skip-domain`，避免被嗅探误改写目标。
- 规则分流：覆盖大量国内 App 包名、中国域名库、微信/支付宝专属规则，以及越南、AI、Google、YouTube、GitHub、微软、Telegram、Netflix、TikTok、Spotify、Apple、哔哩哔哩港澳台等常见场景。
- 两地使用：`国内服务` 和 `越南服务` 均默认 `DIRECT`，在中国或越南按所在地手动切换需要的跨境策略，选择会由 `profile.store-selected` 保留。
- 分组测速：Mihomo / JS 与 Shadowrocket 的手动业务组使用对应服务的小型 HTTPS 端点，地区手动组与自动组使用对应地区端点；中国组使用百度 200。Mihomo 的 `select` 组不设置 `interval`，只提供按需测速，不改变手动选路逻辑；含 `REJECT` 的广告组不测速。
- Stash 测速边界：自动组继续使用各自的地区端点；手动 `select` 组保留 `interval: -1`。Stash 对同一代理在多个组间共享测速结果，若要真正使用不同测试参数需要复制代理，因此本覆写不写入无效的“每组独立 URL”。
- 节点归类：支持 `HK/HKG`、`TW/TWN/TPE`、`JP/NRT/HND/KIX`、`SG/SGP/SIN`、`US/USA`、`KR/ICN/SEL`、`VN/HCM/HCMC/SGN/HAN`、`CN/China` 等常见代码或机场名，并使用英文字母边界避免误命中普通英文单词。
- 回国节点隔离：`回国`、`港广`、`港沪`、`港深`、`沪港`、`深港`、`广中` 在地区分类中只进入中国组，并从全局 `自动选择` 和所有非中国地区组排除；仍可在 `全部节点` 中手动选择。
- 空组保护：Mihomo 的所有订阅筛选组使用 `empty-fallback: REJECT`，筛选不到节点时不会静默直连。

## 使用方法

### YAML 覆写

适合使用 Mihomo v1.19.27 或更新内核、并支持 YAML 覆写、配置片段或 merge/override 的客户端。`empty-fallback` 从 v1.19.27 起可用。

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

适合 Stash iOS/tvOS 3.6+ 或 macOS 4.3+；这些版本支持加密启动 DNS 与独立的代理节点 DNS。

1. 使用 `stash.stoverride`。
2. 在 Stash 的 Override / 覆写配置中导入。
3. 更新订阅后检查 DNS、Sniffer、策略组、规则集和分流规则是否生效。

## 使用注意

- 本配置默认启用 fake-ip；IPv6 跟随客户端/软件设置。主配置包含 TUN DNS 劫持参数，建议先备份原客户端配置。
- Android 场景下，微信和支付宝通过包名固定到 `国内服务`，因此应用内请求、小程序和 H5 都随整个应用进入该组；桌面微信也有独立进程规则。微信、支付宝的维护中远程域名规则同时覆盖 Stash 等不支持 Android 包名匹配的客户端。
- Stash iOS/tvOS 与 Shadowrocket 不能按 Android 包名实现“整个 App”分流；这两类客户端通过维护中的微信/支付宝域名、User-Agent 和 IP/ASN 规则覆盖已知流量，但未来出现的全新第三方内嵌域名仍需按连接日志补充。
- Stash 版本不建议直接照搬主配置的 `tun` 段，应交给客户端管理隧道。
- Stash 官方语义会把“筛选后没有任何节点”的策略组当作 `DIRECT`，且没有 Mihomo `empty-fallback` 的等价字段；导入订阅后必须确认 `中国节点/中国-自动`、`越南节点/越南-自动` 等准备使用的地区组非空。
- 在中国使用：保持 `国内服务 = DIRECT`；如需访问越南本地服务，可将 `越南服务` 切换为 `越南-自动`。
- 在越南或其他境外地区使用：将 `国内服务` 切换为 `中国-自动` 或 `中国节点`；`越南服务` 保持 `DIRECT`。
- 配置无法可靠判断当前公网所在地，因此不硬编码自动切换；`profile.store-selected` 会记住手动选择，跨境后只需切换一次对应策略组。
- 系统更新、局域网、NTP、推送等既有直连规则保持不变。
- `midea` 相关域名固定直连，避免客户/工作相关系统误走代理。
- 如修改策略组名称，必须同步修改 `rules`、`nameserver-policy`、JS 覆写版本和 Stash 覆写版本。

## 维护口径

- `防DNS泄露.yaml` 是主配置。
- `防DNS泄露.js` 与主 YAML 保持功能同步。
- `stash.stoverride` 是 Stash 专用版本，保留 DNS、Sniffer、策略组、规则集和规则分流；IPv6 跟随 Stash 自身设置。
- `shadowrocket.conf` 使用 Shadowrocket 原生语法；地区组筛选、双地默认策略和测速端点与主配置保持语义同步。
- 以后修改主配置时，需要同步检查 JS、Stash 和 Shadowrocket 三类版本。
- CI 会自动校验主 YAML 解析、主 JS 语法、主 YAML/JS 全配置同步、规则引用完整性、Stash 覆写解析、Shadowrocket 关键策略语义和 mihomo 加载测试。
- CI 会检查 `unified-delay`、`profile`、`geo-auto-update`、`geo-update-interval`、`tcp-concurrent`、`sniffer`、`tun`、`dns`、`proxy-groups`、`rule-providers`、`rules` 是否在主 YAML 和主 JS 中保持一致。
- CI 每天自动运行一次，用于尽早发现 Mihomo 最新版本、远程规则集或下载链路变化导致的问题。
- Dependabot 会每周检查 GitHub Actions 依赖更新。
