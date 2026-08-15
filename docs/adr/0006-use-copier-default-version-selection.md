# ADR-0006: 使用 Copier 默认模板版本选择

## Status

Accepted；替代 [ADR-0004](0004-derive-template-source-from-origin.md) 中严格 tag 预检和显式
`--vcs-ref` 选版部分。ADR-0004 的 fetch `origin` 来源推导、URL 规范化和失败不回退决定继续有效。

## Date

2026-08-10

## Context

根 `just new` 曾自行枚举远端 tag，只接受严格 `vX.Y.Z`，再把选中值通过 `--vcs-ref` 交给 Copier。
这重复实现了 Copier 和 Renovate 已有的版本发现与排序，并把 Fork 的版本格式也固定进本仓库脚本。
模板维护者已经通过 `bump` 生成约定版本，因此不需要在每个消费入口再次实现同一限制。

## Decision

1. `just new` 继续验证 Git 仓库根目录、fetch `origin`、受支持 URL 和规范化 HTTPS 远端可访问性。
2. `just new` 不枚举或筛选 tag，也不传 `--vcs-ref`；Copier 按默认规则选择版本。
3. 生成插件的 Renovate 配置不增加 Copier `allowedVersions`，由 Copier manager 使用默认版本规则。
4. 模板维护者继续通过 `bump` 发布约定版本，并永久保留已经公开的版本 tag。

## Consequences

- 新建和自动更新使用同一套上游默认语义，减少自定义脚本和 Fork 约束。
- 非约定 tag 不再由消费入口主动拒绝；发布者负责只公开可供 Copier 使用的正式版本。
- 需要固定 tag、branch 或 commit 的特殊调用者仍可直接使用 Copier 的 `--vcs-ref`，但这不是正式
  `just new` 的默认行为。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [Copier vcs_ref](https://copier.readthedocs.io/en/stable/configuring/#vcs-ref)
