# ADR-0007: 使用当前 GitHub CLI 账号作为生成仓库 owner

## Status

Accepted

## Date

2026-08-10

## Context

Copier 模板来源和生成插件仓库的 GitHub owner 是两个独立身份。模板来源决定生成项目以后从哪里更新，
`repo_owner` 则进入项目主页、Issues、安装地址和 NoneBot 插件元数据，并决定 `gh repo create` 在哪个账号
下创建仓库。

根 `just new` 原先固定使用 `Misty02600`。模板维护者本人可以正常运行，但其他用户直接使用官方模板时会
生成指向模板维护者账号的链接，并尝试在无权限的账号下创建仓库。

## Decision

1. 根 `just new` 通过 `gh api user --jq .login` 读取当前 GitHub CLI 登录账号，并把它同时作为 Copier
   的 `repo_owner` 和 `gh repo create` 的目标 owner。
2. `just new` 不增加 owner 参数，只支持向当前登录账号创建仓库；组织或其他账号不是当前正式入口的支持
   范围。
3. `copier.yml` 不为 `repo_owner` 设置模板维护者默认值。直接交互调用 Copier 时由调用者回答；自动调用者
   必须显式传入。
4. 没有 GitHub CLI 的调用者不能使用包含远端创建和首次 push 的 `just new`，但仍可直接使用 Copier 生成
   本地项目，并自行创建和推送远端仓库。
5. 读取登录账号失败时停止，不回退到模板维护者账号。模板来源继续只由模板仓库的 fetch `origin` 决定。

## Consequences

- 其他用户可以直接从官方模板仓库创建归自己所有的插件仓库，不需要先修改维护者常量。
- 模板维护者本人仍得到与原来相同的 owner，只是来源改为当前 `gh` 登录会话。
- 组织仓库需要调用者直接使用 Copier 并自行完成远端操作，或在自己的 Fork 中扩展创建入口。
- 直接 Copier 调用多一个没有默认值的问题，避免静默生成指向错误账号的项目链接。

## Implementation

- 根 [`justfile`](../../justfile) 在创建目标目录前读取 GitHub CLI 登录账号，并把结果传给 Copier 和
  `gh repo create`。
- [`copier.yml`](../../copier.yml) 的 `repo_owner` 不再包含 `Misty02600` 默认值。
- [`README.md`](../../README.md) 说明 `just new` 与直接 Copier 调用的依赖和支持边界。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [ADR-0004: 从 Git origin 推导模板来源](0004-derive-template-source-from-origin.md)
