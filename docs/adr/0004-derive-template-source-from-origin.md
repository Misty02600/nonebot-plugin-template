# ADR-0004: 从 Git origin 推导模板来源

## Status

部分替代；来源推导决定继续有效，严格 tag 预检与显式选版由
[ADR-0006](0006-use-copier-default-version-selection.md) 替代。本 ADR 替代
[ADR-0003](0003-use-an-explicit-template-source-constant.md)。

## Date

2026-08-10

## Context

ADR-0003 要求 Fork 维护者手工修改 `template_source` 常量。进一步讨论后确认，标准 GitHub
clone 已经用 fetch `origin` 表达当前模板仓库的发布身份：官方 clone 指向官方仓库，Fork clone
指向 Fork。继续维护第二份来源常量会形成重复配置，漏改时还会让 Fork 中的 `just new` 静默跟随
官方模板。

模板来源会进入生成项目的 `.copier-answers.yml`，因此必须是可重放的持久远端，不能由本地路径、
临时 fallback 或未推送工作树决定。

## Decision

1. `just new` 从根 `justfile` 所在 Git 仓库的 fetch `origin` 自动推导 Copier 来源；不读取调用者
   当前目录的仓库状态。
2. 不保留硬编码 `template_source`，不增加来源参数，也不在失败时回退到官方仓库。
3. 当前只支持公开 `github.com` HTTPS、scp 风格 SSH 和 `ssh://git@github.com/` 来源，并统一规范成
   `https://github.com/<owner>/<repo>.git`。这是公开模板的可移植性政策，不是 Renovate 的功能限制。
4. Git 不可用、`justfile` 不在 Git 根目录、缺少 `origin`、URL 不受支持、远端不可公开访问或远端
   没有严格 `vX.Y.Z` 稳定 tag 时，必须在创建目标目录前失败并说明原因。
5. Copier 继续从远端选择最新稳定 release；本地未推送修改不进入生成结果。Fork 要独立维护时必须
   先推送修改并发布自己的更高稳定 tag。
6. 模板来源只决定 Copier 更新链；生成插件的 `repo_owner` 和作者身份继续独立维护。

## Alternatives Considered

- 固定来源常量：来源最显式，但与标准 `origin` 重复，Fork 容易漏改。
- 增加命令参数：能单次覆盖，但同一 clone 可能生成来源不一致的项目。
- 失败后回退到官方源：提高表面成功率，却会把环境错误变成错误的长期更新身份。
- 原样保存所有 Git URL：灵活性最高，但会接受本地路径、临时镜像或依赖个人凭据的来源，不符合当前
  公开 GitHub 模板边界。

## Consequences

- 官方 clone 与 Fork clone 都不再维护额外来源常量，标准 Fork 可以自然形成自己的更新链。
- `origin` 成为 `just new` 的公开前置契约；改变它会改变之后生成项目的模板来源，但不修改既有项目。
- 首次远端和稳定 tag 发布前，创建命令会有意失败，避免把未发布工作树误当成正式模板。
- 私有 GitHub 仓库、GitHub Enterprise、GitLab、本地路径和自定义镜像当前不受支持；需要时另做来源与
  认证决策。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [Repository README](../../README.md)
- [Copier vcs_ref](https://copier.readthedocs.io/en/stable/configuring/#vcs-ref)
- [Renovate Copier private authentication](https://docs.renovatebot.com/modules/manager/copier/#private-modules-authentication)
- [ADR-0006：使用 Copier 默认模板版本选择](0006-use-copier-default-version-selection.md)
