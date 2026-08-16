# nonebot-plugin-template

基于 [Copier](https://copier.readthedocs.io/) 的 NoneBot 插件模板，预置 uv、Ruff、BasedPyright、pytest、Prek、Commitizen、GitHub Actions 和 Renovate。

## 快速开始

需要安装 Just 1.56+、uv、Git、已登录的 GitHub CLI，以及可通过 `pwsh` 调用的 PowerShell 7。

```console
git clone https://github.com/Misty02600/nonebot-plugin-template.git
cd nonebot-plugin-template
just new nonebot-plugin-example
```

`just new` 会在模板仓库的同级目录生成插件、创建初始提交，并使用当前 GitHub CLI 账号创建和推送公开仓库。创建私有仓库时传入第二个参数：

```console
just new nonebot-plugin-example private
```

如果只需要生成本地文件，可以直接使用 Copier：

```console
uvx --from "copier>=9.17,<10" copier copy https://github.com/Misty02600/nonebot-plugin-template.git nonebot-plugin-example
```

## 模板内容

- 可安装的 `src/<module>/` 包布局和基础 NoneBot 插件代码；
- Ruff、BasedPyright、pytest 和 Prek 质量检查；
- Python 3.11–3.14 CI；
- 使用 Trusted Publishing 的 PyPI 发布和 GitHub Release；
- Copier 与 Renovate 模板更新。

生成项目后，不要手工编辑 `.copier-answers.yml`。它记录模板来源、版本和生成参数。

## 维护模板

首次进入控制仓库时同步依赖：

```console
uv sync --all-groups --locked
```

| 命令 | 用途 |
|---|---|
| `just test-fast` | 运行不依赖外部工具链的快速测试 |
| `just test` | 运行完整模板、生成和更新测试 |
| `just lint` | 检查 Ruff lint 与格式 |
| `just format` | 自动修复并格式化 |
| `just check` | 运行 BasedPyright |
| `just lock` | 更新控制仓库的 `uv.lock` |
| `just bump` | 创建版本提交和 annotated tag，并原子推送到 `origin` |

发布新模板版本前应确保 `main` 上的完整测试和 CI 已通过。`just bump` 经确认后会立即推送提交和 tag。

## 更新生成项目

Hosted Renovate 可以根据 `.copier-answers.yml` 创建模板更新 PR。需要手工更新时，在生成项目的干净工作树中运行：

```console
just update-template
```

遇到 Copier 冲突时，解决冲突并删除 `.rej` 文件，然后运行 `just finish-template-update` 完成检查。

## License

本模板采用 [MIT License](LICENSE)。
