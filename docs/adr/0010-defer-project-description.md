# ADR-0010：创建时不采集项目简介

## 状态

已采纳

## 日期

2026-08-10

## 当时遇到了什么

根 `just new` 和 Copier 原本都接收项目简介，并把它同时写入生成包的 `pyproject.toml` 和 GitHub
仓库描述。新建阶段通常还没有足够信息写出稳定、准确的简介，默认占位文本也容易被直接保留并发布。
这项输入不影响模板身份、生成目录、包名或后续 Copier 更新。

首个 Copier 稳定版本尚未发布，因此 `project_description` 还不是下游 answers 的兼容契约，可以在公开
基线形成前直接移除。

## 最后决定

1. 根 `just new` 不接收项目简介，也不向 `gh repo create` 传递 `--description`。
2. `copier.yml` 不询问或保存 `project_description`。
3. 生成的 `pyproject.toml` 不预置 `project.description`；GitHub 仓库也保持无描述。
4. 插件维护者在明确项目用途后，自行补充包元数据、GitHub 仓库描述和其他面向用户的简介。
5. NoneBot `PluginMetadata.description` 属于插件运行时元数据，不由建仓参数自动填充。

## 为什么这样选

- 简介不是生成项目所需的身份或结构输入。
- 省略字段比发布通用占位文本更诚实，也减少创建命令的参数数量。
- 维护者可以在理解插件行为后分别为不同展示位置写出合适内容。

## 没有采用的方案

- 强制创建时填写：能立即得到完整元数据，但会把尚未成熟的文案变成建仓前置条件。
- 保留默认占位文本：命令最短，但占位内容可能进入包元数据和公开仓库后长期未被发现。
- 用同一参数填充所有描述字段：减少重复输入，但包摘要、GitHub About 与 NoneBot 运行时元数据的受众和
  语义并不完全相同。

## 带来的影响

- `just new` 只需要仓库名，可见性仍是可选参数。
- 直接调用 Copier 时少一个问题，`.copier-answers.yml` 也不再保存简介。
- 新仓库和构建出的包在维护者补充前没有项目摘要；模板不会把占位文本伪装成正式说明。

## 落实与确认

- 实施情况：已落实（2026-08-10）。
- 代码：根 `justfile`、`copier.yml`、`template/pyproject.toml.jinja`。
- 验证：模板 CI 检查渲染后的 `pyproject.toml` 不包含 `description` 字段。

## 相关文档

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级 flow](../architecture/flows/template-lifecycle.md)
