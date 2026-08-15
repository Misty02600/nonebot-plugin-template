# ADR-0009: 根仓库与生成插件统一使用现代 Just PowerShell 配置

## Status

Accepted

## Date

2026-08-10

## Context

根仓库和生成插件原先分别使用 `windows-shell`，其中生成插件还固定调用 Windows PowerShell 的
`powershell`。Just 1.56 已弃用 `windows-shell`，并允许把 `[windows]` 条件属性应用到 `set shell`；
`python-project-template` 已采用这一配置，避免 Windows 专用设置影响 Unix recipes。

ADR-0008 只把根创建入口切换到 `pwsh`，明确没有改变生成插件的开发命令。继续维持两套写法会让生成插件
保留旧 PowerShell 依赖，也会使两个模板对 Just 的最低版本和 shell 配置形成不必要差异。

## Decision

1. 根仓库和生成插件都要求 Just 1.56 或更高版本。
2. 两层 `justfile` 都使用 `[windows]` 修饰 `set shell := ["pwsh", "-NoProfile", "-Command"]`，不再使用
   `windows-shell` 或 Windows PowerShell。
3. 两层都使用 `set default-list` 提供默认任务列表，不再维护等价的手写 `default` recipe。
4. Windows 用户运行普通 recipes 需要 PowerShell 7；Linux 和 macOS 的普通 recipes 保留 Just 的平台默认
   shell。根 `just new` 仍在所有平台显式使用 `pwsh -NoProfile -File`。
5. 当前脚本不使用要求特定 PowerShell 7.x 小版本的能力，因此不跟随 `python-project-template` 把最低
   PowerShell 版本提高到 7.4。

本决定部分替代 [ADR-0008](0008-use-cross-platform-powershell-for-creation.md) 的决定 5；ADR-0008 关于根
创建入口、跨平台支持和 PowerShell 小版本边界的其他决定继续有效。

## Consequences

- NoneBot 模板与 `python-project-template` 对现代 Just shell 配置和最低 Just 版本保持一致。
- 生成插件的 Windows 开发环境必须提供 `pwsh`，不能只依赖系统内置的 Windows PowerShell。
- Unix 上普通 recipes 不会因为 Windows 的 shell 选择而改用 PowerShell；只有显式声明的脚本入口使用
  `pwsh`。
- PowerShell 7.0 至 7.3 仍属于当前支持范围；如果以后采用 `-CommandWithArgs` 等更高版本能力，再单独
  收紧要求。

## Links

- [`justfile`](../../justfile)
- [生成插件 `justfile`](../../template/justfile)
- [生成插件 README](../../template/README.md.jinja)
- [Architecture overview](../architecture/overview.md)
- [ADR-0008](0008-use-cross-platform-powershell-for-creation.md)
- [Just 1.56.0 changelog](https://github.com/casey/just/blob/1.56.0/CHANGELOG.md)
