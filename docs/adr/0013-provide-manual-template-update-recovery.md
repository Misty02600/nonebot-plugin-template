# ADR-0013: 为生成插件提供可恢复的手工模板更新入口

- Status: Accepted
- Date: 2026-08-11

## Context

Hosted Renovate 是模板升级进入插件仓库的主要入口，但维护者仍可能需要本地复现更新、接管冲突 PR，或在解决 Copier 产生的 `.rej` 文件后继续完成验证。仅在文档中列出 Copier、lock、hooks 和质量命令，会让恢复过程依赖个人记忆，也无法保证每次都检查暂存区 whitespace、冲突文件和完整工具链。

Python 模板已经把自动更新与可恢复的收尾验证拆成两个 Just recipes。NoneBot 模板可以采用同一边界，同时保持自己的依赖组和质量命令。

## Decision

- Hosted Renovate 继续作为常规模板升级入口；手工命令是本地维护和故障恢复路径，不取代升级 PR。
- 生成插件提供 `just update-template`。该命令要求包含未跟踪文件在内的干净工作树，使用官方 Copier 默认版本选择执行 `copier update --skip-answered`，然后调用 `just finish-template-update`。
- `just finish-template-update` 可以独立重跑，用于已经应用更新、解决 Copier 冲突或接管 Renovate PR 后继续验证。
- 收尾阶段依次检查工作树与暂存区 whitespace、拒绝残留 `.rej`，刷新被插件策略忽略的本地 `uv.lock`，同步全部依赖组，并运行 hooks、Ruff、BasedPyright 和 pytest。
- 更新命令不指定 `--vcs-ref`，不重写 `.copier-answers.yml`，仍由 Copier 根据其中的来源和当前版本管理更新身份。

## Consequences

- 维护者可以在失败步骤修正问题后只重跑收尾阶段，无需再次执行 Copier 合并。
- 干净工作树门禁避免模板更新与尚未提交的业务改动混在同一次三方合并中。
- 库模板继续不提交 `uv.lock`；收尾阶段生成 lock 只是为了在一次可复现的本地环境中执行全部检查。
- 本地更新不会绕过 PR 审查或改变 Hosted Renovate 的主要交付方式。

## Links

- [Architecture Overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [ADR-0001: 使用 Copier 与托管 Renovate](0001-use-copier-and-renovate.md)
- [ADR-0006: 使用 Copier 默认模板版本选择](0006-use-copier-default-version-selection.md)
