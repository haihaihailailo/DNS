# 贡献与验证

修改 `防DNS泄露.yaml` 后，请至少做一次 YAML 解析检查：

```sh
ruby -e 'require "yaml"; YAML.safe_load_file("防DNS泄露.yaml", aliases: true); puts "YAML OK"'
```

如果本地装有 `mihomo`，再做一次配置加载检查：

```sh
mihomo -t -f "防DNS泄露.yaml"
```

仓库的 GitHub Actions 会在 push 和 pull request 中自动执行 YAML 解析检查，并下载 `mihomo` 进行配置加载检查，避免配置语法、YAML alias 用法或 Mihomo 兼容性被意外改坏。
