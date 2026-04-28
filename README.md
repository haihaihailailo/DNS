# DNS 分流配置（防 DNS 泄露）

这个仓库提供一份可直接使用的 Clash Meta 配置，重点是：

- 防 DNS 泄露（Fake-IP + DoH + fallback 过滤）。
- 按地区与应用分流（YouTube / Netflix / AI / Telegram 等）。
- 细化越南与国内服务分流。

## 已做的可维护性优化

- `url-test` 增加测速 URL 与 `lazy`，并将测速间隔调大，降低后台测速开销。
- DNS 增加 `ipv6: false` 与 `geosite:geolocation-!cn` 的解析策略，减少跨区误解析并提升分流一致性。
- 将 `private/direct/applications` 直连规则前移，减少无意义规则匹配，提升命中效率。
- 复用应用分流与“漏网之鱼”的全地区代理列表锚点，避免重复维护同一长列表。
- 使用 YAML 锚点复用 `url-test` 公共参数，减少重复配置。
- 使用 YAML 锚点复用 `rule-providers` 的公共下载参数（`domain/ipcidr/classical`）。

这样在后续调整测速参数、更新间隔或协议行为时，只需要改一个地方即可同步全局生效。
