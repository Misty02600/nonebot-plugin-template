# ADR-0003: 使用显式模板来源常量

## Status

Superseded by [ADR-0004](0004-derive-template-source-from-origin.md)

## Date

2026-08-10

## Context

Fork 本仓库不会影响原仓库，但 Fork 中保留的 `just new` 仍需要知道从哪个远端取得 Copier
模板。这个来源会写入生成项目的 `.copier-answers.yml`，成为以后更新时需要长期可用的地址。

如果创建命令自动读取 Git `origin`，临时 remote 或错误 clone 可能在没有明显提示的情况下成为
长期模板来源；如果每次通过命令参数覆盖，同一 Fork 又可能生成来源不一致的项目。

## Decision

1. 根 `justfile` 只用一个顶部 `template_source` 常量表示 Copier 模板来源。
2. `just new` 不提供模板来源参数，也不自动读取 Git `origin`。
3. Fork 默认保留本仓库为来源。要把 Fork 作为独立模板使用，Fork 维护者必须修改
   `template_source`，并在自己的远端发布和永久保留稳定 tag。
4. `template_source` 与生成插件的 `repo_owner` 分开；前者决定模板更新链，后者决定插件仓库归属。
5. README 明确说明上述行为，不为 Fork 的工作流、兼容性或发布承担额外保证。

## Alternatives Considered

- 增加模板来源参数：支持单次覆盖，但容易让同一 Fork 生成多条不一致的更新链。
- 自动读取 Git `origin`：Fork 开箱即用，但长期来源被本地 Git 状态隐式决定。
- 始终禁止修改官方来源：更新链最集中，但无法让 Fork 作为独立模板产品使用。

## Consequences

- 官方使用路径保持简单，生成项目默认只跟随本仓库。
- Fork 可以独立维护模板，但需要有意识地修改一处常量并承担自己的 tag 生命周期。
- 仓库所有者、作者身份和模板来源不再因为当前值相同而共用同一变量。

## Links

- [Architecture overview](../architecture/overview.md)
- [ADR-0002: 保持 NoneBot 模板独立](0002-keep-the-nonebot-template-independent.md)
- [Repository README](../../README.md)
