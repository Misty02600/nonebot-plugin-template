# ADR-0017: 生成插件的所有 pull request 都运行 CI

- Status: Accepted
- Date: 2026-08-11

## Context

生成插件的 CI 原先为 `pull_request` 配置路径白名单，只在源码、测试、Python 配置、Copier answers 或
workflow 变化时运行。`.pre-commit-config.yaml`、`justfile`、`cliff.toml` 和 Renovate 配置等维护文件
不在白名单内，因此只修改这些文件的 PR 会跳过 CI。若 CI 是 required check，被路径过滤跳过的 workflow
还可能使合并一直等待检查；不设 required check 时，这类维护变更又会失去质量门禁。

Hosted Renovate 通过普通 pull request 交付模板升级，生成插件也独立拥有 active CI。PR 是否运行检查
属于生成仓库自己的合并门禁，不应由不完整的文件枚举推断变更是否安全。

## Decision

- 生成插件的 CI 对所有目标为 `main` 的 pull request 运行，不配置 `pull_request.paths` 或
  `pull_request.paths-ignore`。
- `push` 事件继续只忽略单独的 `LICENSE` 变化；该策略不影响 pull request required check。
- 根控制项目真实渲染生成 workflow，并以契约测试确认 pull request 触发器没有恢复路径过滤。
- Ruff、BasedPyright 和 pytest 的 jobs、Python 版本矩阵及生成项目对 active workflow 的所有权保持不变。

## Consequences

- 维护配置、依赖更新和 Copier 升级 PR 与源码 PR 使用同一组质量门禁。
- required check 不会因为模板的路径过滤而保持等待状态。
- 仅修改文档或其他低风险文件的 PR 也会消耗完整 CI 资源；模板接受这项成本以换取稳定、可预测的合并门禁。
- 插件维护者仍可在自己的仓库修改 active workflow，但模板后续更新可能再次提出这一默认策略。

## Links

- [ADR-0005: 生成插件独立拥有完整 CI](0005-generated-plugins-own-ci.md)
- [Architecture Overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
