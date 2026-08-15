# ADR-0020: 只在 GitHub workflows 固定 uv CLI 版本

- Status: Accepted
- Date: 2026-08-12

## Context

根控制项目和生成插件原先都在 `pyproject.toml` 中设置 `[tool.uv].required-version = ">=0.11,<0.12"`。
该字段会让本地 uv 在执行项目命令前拒绝范围外版本，把所有本地使用者绑定到模板指定的 uv minor 版本。

根控制项目已经提交 `uv.lock` 来固定维护依赖；生成插件有意不提交 lock。两层 GitHub workflows 又通过
setup-uv 的 `version` 输入安装精确 uv CLI 版本，因此远端质量检查和发布不依赖项目元数据中的宽范围
限制。workflow 里的 uv 版本也已经由 Renovate 按 patch 自动合并、minor/major 人工审查的策略维护。

## Decision

1. 根控制项目和生成插件都不设置 `[tool.uv].required-version`。
2. 根控制项目继续使用 `[tool.uv].package = false`，并继续提交 `uv.lock`；生成插件继续使用
   `[tool.uv.build-backend]` 配置构建模块，且不提交 lock。
3. 本地运行不因模板声明的 uv minor 范围被预先拒绝，但这不承诺任意旧版或未来版本都兼容；实际命令若
   使用了当前 uv 才支持的功能，仍由 uv 自身报告错误。
4. 根 CI、生成插件 CI 和 release workflow 继续安装精确 uv CLI 版本。setup-uv Action 本身仍使用
   精确 semver tag。
5. Renovate 现有 uv 更新策略保持不变：patch 更新在门禁通过后自动合并，minor 与 major 更新需要人工
   审查。

## Consequences

- 维护者可以使用能够执行仓库现有命令的本地 uv，不会仅因其版本落在模板预设 minor 范围之外而被拒绝。
- 远端检查和发布仍使用明确、可更新的精确 uv 版本，不因移除项目元数据约束而漂移。
- 根控制依赖仍由已提交的 `uv.lock` 固定；生成插件继续接受无 lock 库项目的本地解析差异。
- 如果本地 uv 与仓库使用的功能不兼容，失败信息来自实际命令，而不是额外维护一条工具版本范围。

## Relationship to Existing Decisions

- 本决定不替代 [ADR-0012](0012-use-a-python-controller-project.md)：根控制项目、`package = false` 和提交
  `uv.lock` 的决定继续有效。
- 本决定不替代 [ADR-0019](0019-use-readable-action-tags-without-dedicated-scanners.md)：setup-uv Action
  使用精确 semver tag 的决定继续有效；本 ADR 另行确定 uv CLI 的项目元数据与 workflow 边界。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [ADR-0013: 为生成插件提供可恢复的手工模板更新入口](0013-provide-manual-template-update-recovery.md)
