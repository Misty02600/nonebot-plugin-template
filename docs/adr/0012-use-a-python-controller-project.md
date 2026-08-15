# ADR-0012: 根仓库使用独立的 Python 控制项目

- Status: Accepted
- Date: 2026-08-10

其中“根 CI 运行全部契约测试”的决定由
[ADR-0016](0016-keep-just-dependent-controller-tests-local.md) 部分替代；其他决定保持有效。

## Context

仓库根目录已经不再是一个 NoneBot 插件，但模板维护仍需要稳定执行 Copier 渲染、配置契约检查和控制层质量检查。迁移过程中旧插件的 `pyproject.toml` 被删除，而根 `uv.lock` 仍然保留，导致锁文件没有声明它所对应的控制依赖；根 `justfile` 也只有创建和发布命令，无法通过统一入口运行模板测试。

`python-project-template` 已使用非打包的 uv 控制项目承载同类职责。NoneBot 模板保持独立生成链，但可以采用同一种控制层边界。

## Decision

- 根目录建立独立的 Python 控制项目，`[tool.uv].package = false`；它不是生成插件，也不发布 Python 包。
- 根 `pyproject.toml` 声明 Copier、pytest、Ruff 和 BasedPyright 等维护依赖，根 `uv.lock` 随仓库维护。
- 根 `tests/` 验证 Copier answers、Just 命令、控制仓库配置和默认渲染结果；会执行外部工具链的测试标记为 `integration`。
- 根 `justfile` 提供 `test`、`test-fast`、`lint`、`format`、`check` 和 `lock`。`test-fast` 只是跳过 integration 测试的手动快捷入口，不作为提交钩子。
- 根 CI 先在锁定的控制环境中运行 Ruff、BasedPyright 和全部契约测试，同时继续验证生成插件的 Ruff、BasedPyright 与 Python 版本矩阵。
- 根模板版本仍由 `.cz.toml` 和 `just bump` 管理；控制项目的 PEP 621 版本不用于发布模板或 Python 包。

## Consequences

- 根 `uv.lock` 重新拥有明确来源，模板维护者可以用同一组 Just recipes 在本地复现 CI 的控制层检查。
- 控制层测试不会替代生成项目测试；两者分别保护模板契约和最终插件行为。
- 新增维护依赖需要刷新并提交根 lock。
- PowerShell 最低要求保持 7；该决定不引入 Python 模板使用的 PowerShell 7.4 约束。

## Links

- [Architecture Overview](../architecture/overview.md)
- [ADR-0002: 保持 NoneBot 模板独立](0002-keep-the-nonebot-template-independent.md)
- [ADR-0011: 根模板通过 Commitizen 发布版本](0011-use-root-commitizen-bump.md)
