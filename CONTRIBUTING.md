# 贡献与验证

修改 `防DNS泄露.yaml` 后，请至少做一次 YAML 解析检查：

```sh
ruby -e 'require "yaml"; YAML.safe_load_file("防DNS泄露.yaml", aliases: true); puts "YAML OK"'
```

仓库的 GitHub Actions 会在 push 和 pull request 中自动执行同样的检查，避免配置语法或 YAML alias 用法被意外改坏。
