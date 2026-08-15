# ADR-0008: 根创建入口统一使用跨平台 PowerShell

## Status

Accepted; decision 5 partially superseded by [ADR-0009](0009-align-modern-just-powershell-configuration.md)

## Date

2026-08-10

## Context

根 `just new` 是官方仓库和第三方 Fork 共用的正式创建入口。它原先通过
`[script("powershell", ...)]` 固定调用 Windows PowerShell；标准 Linux 和 macOS 环境即使已经安装
Just、Git、uv 和 GitHub CLI，也没有名为 `powershell` 的跨平台 PowerShell 入口，因此无法启动创建脚本。

`python-project-template` 已使用 PowerShell 7 的 `pwsh` 作为跨平台脚本解释器。NoneBot 模板的创建脚本
同样只使用跨平台 PowerShell 能力，但当前不依赖某个 7.x 小版本特有的行为。

## Decision

1. 根 `justfile` 的 `just new` 在所有平台统一通过 `pwsh -NoProfile -File` 执行。
2. Windows 上根 `justfile` 的普通 recipe 也使用 `pwsh`，不再混用 Windows PowerShell。
3. 公开文档把 PowerShell 7 和 `pwsh` 列为正式创建入口的前置条件，并明确该入口支持 Windows、Linux 和
   macOS。
4. 当前只要求 PowerShell 7，不固定 7.x 小版本，也不增加脚本内版本校验；将来只有在实际使用特定版本
   能力时才收紧约束。
5. 生成插件中的 `template/justfile` 不属于根创建入口，其 `windows-shell` 只影响 Windows 本地 recipes，
   本决定不改变生成插件的开发命令。

## Alternatives Considered

- 继续使用 `powershell` 并声明仅支持 Windows：不会增加 Windows 维护者的安装要求，但会让公开模板和
  Fork 的标准 Linux/macOS 用户无法使用正式入口。
- 分别维护 Windows PowerShell 与 Unix PowerShell 两套 recipe：可以兼容更多本地环境，但会复制创建逻辑
  和错误处理。
- 把创建脚本重写为另一种语言：可以移除 PowerShell 依赖，但改动和维护成本明显超过当前问题所需。

## Consequences

- 安装 PowerShell 7 后，同一个 `just new` 入口可以在 Windows、Linux 和 macOS 上运行。
- Windows 用户不能只依赖系统内置的 Windows PowerShell，必须安装并在 PATH 中提供 `pwsh`。
- NoneBot 模板复用通用 Python 模板已经验证合理的跨平台入口设计，但仍独立维护自己的创建脚本和支持
  约束。

## Links

- [`justfile`](../../justfile)
- [`README.md`](../../README.md)
- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [Just script recipes](https://just.systems/man/en/script-recipes.html)
- [PowerShell executable changes](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell)
