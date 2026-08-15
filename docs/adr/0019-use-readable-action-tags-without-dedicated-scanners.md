# ADR-0019: 使用可读 Action 版本并移除专用 workflow 扫描器

- Status: Accepted
- Date: 2026-08-12

## Context

根 CI 为了用 actionlint 和 zizmor 检查真实渲染后的 workflows，维护了额外的渲染入口、workflow manifest、
扫描器配置、固定工具版本、Renovate 规则和专属测试。仓库的 workflows 数量少且结构稳定，这条扫描链的
维护成本超过当前收益。

完整 commit SHA 也降低了 Action 引用的可读性，并要求 Renovate 和契约测试继续维护相应固定策略。当前
项目选择让版本意图直接体现在 workflow 中，同时保留真正约束生成与发布行为的测试。

## Decision

1. 根 CI 不再运行 actionlint 或 zizmor，也不再为扫描器生成 workflow manifest。
2. 控制项目继续真实渲染默认插件并运行 Ruff、BasedPyright 和 Python 版本矩阵；契约测试继续保护所有
   pull request 都触发 CI、发布权限边界和 reviewed artifact 的传递顺序。
3. GitHub 官方 Actions 使用可读的 major tag，例如 `actions/checkout@v7`；`astral-sh/setup-uv` 使用精确
   semver tag，例如 `astral-sh/setup-uv@v9.0.0`。
4. 根和生成项目的 Renovate 不再设置 `pinDigests`，也不再维护 actionlint、zizmor 或其专属配置。

## Consequences

- 根 CI 少一次额外渲染、一个 Docker 扫描器和一个 `uvx` 扫描器，配置与版本维护明显减少。
- workflow 的 Action 版本可以直接阅读，Renovate 仍可按 GitHub Actions manager 提交版本更新。
- 项目不再提前获得 actionlint 的 schema/表达式检查或 zizmor 的额外安全审计；相关错误可能要到契约测试、
  生成项目 CI 或实际发布 workflow 执行时暴露。
- 可读 tag 不是 immutable commit；项目明确接受这一供应链取舍，并继续以最小权限 jobs、关闭 checkout
  凭据持久化和结构契约测试限制影响。

## Supersession

- Supersedes [ADR-0014](0014-statically-validate-rendered-workflows.md)。
- Supersedes Decision 7–8 of [ADR-0015](0015-stage-least-privilege-plugin-releases.md)；ADR-0015 的分阶段
  最小权限发布链继续有效。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
