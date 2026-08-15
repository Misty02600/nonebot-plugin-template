# ADR-0022: 不使用 Twine 重复检查发行包元数据

- Status: Accepted
- Date: 2026-08-16
- Partially supersedes: [ADR-0015](0015-stage-least-privilege-plugin-releases.md) Decision 3 中的 Twine
  metadata 检查

## Context

生成插件的 release workflow 在 `uv build --no-sources` 后临时下载固定版本 Twine，执行
`twine check --strict`。这为发行包元数据增加一次独立检查，但同时引入版本变量、根 Renovate custom
manager 和生成插件持续维护责任。模板已经在无发布权限的 `validate` job 中运行项目质量检查和构建，
并用 Python 标准库确认发行包数量、wheel 压缩完整性以及 sdist 路径安全。

对于当前小型插件模板，额外 Twine 工具链的维护成本高于它提供的重复 metadata 检查价值。

## Decision

1. 生成插件的 release workflow 不设置 `TWINE_VERSION`，也不运行 `twine check`。
2. `validate` 继续要求 `uv build --no-sources` 成功，并确认发行目录恰好包含一个 wheel 和一个 sdist。
3. `validate` 继续使用 Python 标准库检查 wheel 压缩成员、sdist 非空以及归档路径不存在绝对路径或
   `..` 逃逸。
4. 根和生成插件 Renovate 不为 Twine 配置 custom manager；测试只保护保留的构建、归档与权限边界。

## Consequences

- 通用模板不再提前运行 Twine 的 metadata/README 渲染检查；构建后仍由现有归档检查和最终发布端验证产物。
- 发布 job 的权限、artifact 传递、PyPI Trusted Publishing 与 GitHub Release 顺序不变。
- 具体插件如需要更强的元数据或安装后验证，可以按自身包契约增加检查。

## Rejected alternatives

- 给根和生成插件都增加 Twine custom manager：可以持续更新工具，但保留了当前不需要的额外检查链。
- 不做任何产物检查：会失去数量、压缩损坏和 sdist 路径安全门禁。

## Implementation

- workflow 删除 Twine 变量与命令，保留 `uv build` 和 Python 归档检查。
- 根 Renovate 删除 Twine custom manager。
- 契约测试验证 Twine 不存在且构建、归档和发布顺序保持不变。

## Links

- [ADR-0015: 插件发布使用分阶段最小权限链](0015-stage-least-privilege-plugin-releases.md)
- [Architecture overview](../architecture/overview.md)
