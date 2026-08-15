# ADR-0001: 使用 Copier 与托管 Renovate

## Status

Accepted

其中“Ruff、BasedPyright 和 pytest 集中在中央 reusable workflow”的决定已由
[ADR-0005](0005-generated-plugins-own-ci.md) 部分替代；Copier、Hosted Renovate 和其他模板生命周期决定保持有效。

## Date

2026-07-18

## Context

维护者拥有多个 NoneBot 插件仓库。它们共享 CI、Ruff、BasedPyright、pytest、Commitizen、预提交钩子和部分 README 结构，但各自保留业务代码、说明和发布身份。

GitHub 原生模板适合创建仓库，却不提供后续同步，也会原样复制默认分支中的 `docs/` 等中央内容。仅使用可复用工作流只能集中 CI 实现，无法更新工具配置和文档。自研跨仓库同步器则需要长期维护仓库发现、认证、文件所有权和 PR 逻辑。

## Decision

采用以下模板生命周期：

1. 根目录的 `just new` 是新插件的正式创建入口；它调用 Copier，Copier 也是共享文件升级的合并引擎。
2. 仓库根目录作为控制面，插件脚手架只保存在 `template/`，并由 `_subdirectory: template` 选择。
3. 模板只使用静态文件和 Jinja；不使用 Copier tasks、migrations 或自定义 extensions。
4. 模板使用 PEP 440 兼容 Git tag 发布；生成仓库提交 `.copier-answers.yml`。
5. Hosted Renovate 识别 Copier 模板版本并为每个插件创建升级 PR。
6. Ruff、BasedPyright 和 pytest 的实现继续集中在 `nb-plugin-ci.yml`；插件只保存调用入口。
7. `release.yml` 保留在每个插件仓库中，不改为可复用发布工作流。
8. `docs/` 只属于中央仓库，不进入 `template/`。
9. GitHub 原生 Template repository 只作为迁移期设置；验证新路径后关闭，不再作为正式入口。

## Alternatives Considered

- 自研 GitHub App/PAT 同步器：控制力强，但认证、发现、冲突和 PR 生命周期均由本项目维护。
- 专用文件同步 Action：能复制文件，但采用和维护情况参差，仍不能自然处理项目骨架的三方合并。
- 只使用 reusable workflow：最简单，但不能覆盖工具配置和 README 更新。
- 同时长期支持 GitHub Template 与 Copier：动态目录需要 Jinja，而 GitHub Template 只会原样复制；同一份脚手架无法同时满足两者，最终会产生重复真源。

## Consequences

- 新建仓库不再需要 LICENSE 触发器、初始化 workflow 或 Actions 写权限。
- `gh` 使用维护者当前登录身份创建远端并推送，不需要 GitHub App、PAT 或中央跨仓库写入。
- 新仓库的 Ruff、BasedPyright 和 pytest 由首次推送后的 GitHub CI 检查，不在创建命令中重复运行。
- 模板更新天然以 Renovate PR 交付，维护者仍能检查和拒绝变更。
- 既有插件必须逐个建立 Copier 基线；不能手工伪造 `.copier-answers.yml`。
- 模板 tag 变成发布接口，需要保持单调、可追踪，并在发布前验证默认生成结果。

## Risks

- 模板与插件对同一区域的修改可能产生 Copier 冲突，需要人工处理。
- Hosted Renovate 对 unsafe Copier 功能有限制，因此未来不能随意加入执行脚本的模板特性。
- 在关闭 GitHub Template repository 设置前，用户仍可能误用原生按钮生成控制仓库副本。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [ADR-0005: 生成插件独立拥有完整 CI](0005-generated-plugins-own-ci.md)
- [PLAN-0001: 推出 Copier 模板升级](../plans/todo/0001-roll-out-copier-template-updates.md)
