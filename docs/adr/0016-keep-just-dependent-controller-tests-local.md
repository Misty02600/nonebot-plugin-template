# ADR-0016: Just 相关控制层测试保留为本地集成测试

- Status: Accepted
- Date: 2026-08-11

## Context

控制仓库 CI 只安装 uv 和 Python 维护依赖，不安装 Just。根 pytest 原有一个测试直接执行
`just --dry-run update-hooks`，但它只重复验证同文件中已经由静态断言保护的 prek 命令文本，导致整个
测试套件在没有 Just 的 CI 环境中以 `FileNotFoundError` 失败。

另一些测试会实际执行 `just new`，用于验证 Just 参数约束、PowerShell 参数导出和 Git、Copier、GitHub
CLI 编排。这些行为无法由静态文本断言等价替代，但为了它们给控制仓库 CI 增加一套非 Python 工具依赖，
也会扩大远端环境和维护面。

## Decision

- 控制仓库 CI 不安装或调用 Just。
- 只为重复确认静态 recipe 文本而执行 Just 的测试删除；命令文本继续由直接读取 Justfile 的契约测试保护。
- 真正验证 Just 解析、参数传递或 recipe 编排的测试保留为 `integration`，在 Just 或 PowerShell 不可用时
  明确跳过。
- `just test` 仍调用完整 pytest；在工具齐全的本地环境中运行全部测试，在 CI 中由 pytest 只跳过缺失工具
  所对应的测试。`just test-fast` 继续作为显式跳过所有 integration 测试的本地快速入口。
- 如果以后必须在不安装 Just 的 CI 中覆盖创建入口，应把 PowerShell 创建逻辑抽取成可直接执行和测试的
  独立脚本，不能用静态断言声称已经获得端到端覆盖。

## Consequences

- 控制仓库 CI 不会因 runner 未预装 Just 而失败，也不增加 Just 的安装和版本维护。
- CI 继续保护控制层静态契约、渲染、更新、构建与生成项目质量，但不证明 Just CLI 能实际解析并执行 recipe。
- 维护者在装有 Just 和 PowerShell 的环境运行 `just test`，才能获得创建入口的完整本地集成覆盖。
- 测试输出中的 skip 是有意的工具边界，不表示这些用例已由其他测试等价覆盖。

## Supersedes

- 部分替代 [ADR-0012: 根仓库使用独立的 Python 控制项目](0012-use-a-python-controller-project.md)
  中“根 CI 运行全部契约测试”的决定。

## Links

- [Architecture Overview](../architecture/overview.md)
- [ADR-0008: 根创建入口统一使用跨平台 PowerShell](0008-use-cross-platform-powershell-for-creation.md)
- [ADR-0009: 根仓库与生成插件统一使用现代 Just PowerShell 配置](0009-align-modern-just-powershell-configuration.md)
