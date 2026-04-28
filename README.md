# DNS 分流配置（防 DNS 泄露）

这个仓库提供一份可直接使用的 Clash Meta 配置，重点是：

- 防 DNS 泄露（Fake-IP + DoH + fallback 过滤）。
- 按地区与应用分流（YouTube / Netflix / AI / Telegram 等）。
- 细化越南与国内服务分流。

## 已做的可维护性优化

- 使用 YAML 锚点复用 `url-test` 公共参数，减少重复配置。
- 使用 YAML 锚点复用 `rule-providers` 的公共下载参数（`domain/ipcidr/classical`）。

这样在后续调整测速参数、更新间隔或协议行为时，只需要改一个地方即可同步全局生效。
