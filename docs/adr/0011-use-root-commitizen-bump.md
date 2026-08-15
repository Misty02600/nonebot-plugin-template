# ADR-0011: 根模板通过 Commitizen 发布版本

- Status: Accepted
- Date: 2026-08-10
- Push scope superseded by: [ADR-0018](0018-use-single-step-whole-bump-push.md)。

## Context

仓库根目录已经从可发布的 NoneBot 插件项目变成 Copier 模板控制面。旧的根 `pyproject.toml` 和 Python 环境不再描述真实产物，但模板仍需要一种明确、可复现的方式推进版本并发布 Copier 可发现的 tag。仅依赖手工修改 tag 容易让版本来源、tag 类型和分支推送产生偏差。

## Decision

- 根目录新增 `.cz.toml`，使用 Commitizen 自身的 version provider 保存模板版本；不为了发布模板恢复根 Python 项目。
- 版本遵循 PEP 440，tag 使用 `v$version`，并创建 annotated tag。
- 根 `justfile` 提供带确认的 `just bump`；该命令只允许在 `main` 运行。
- Commitizen 通过 `uvx --from 'commitizen>=4.16,<5'` 临时执行，不写入根依赖或 lock。
- bump 成功后，命令只把当前 `HEAD` 和本次精确 tag 通过 `git push --atomic` 推送到 `origin`。
- 根模板发布不执行 PyPI 发布，也不在 bump 内重复本仓库 CI；维护者在调用前确认 `main` 已通过检查。
- 该配置只管理模板控制仓库版本，与生成插件自己的 `.cz.toml` 和发布流程相互独立。

## Alternatives Considered

- 恢复旧根 `pyproject.toml`：会重新把模板控制面伪装成 NoneBot 插件项目。
- 新建仅供控制面的 Python 项目与 lock：能固定 Commitizen，但为一个临时 CLI 增加了持续依赖维护。
- 完全手工创建 tag：步骤少，但无法统一版本提交、annotated tag 和原子推送语义。
- 使用 `git push --follow-tags`：会隐式携带其他本地 annotated tags，范围大于本次发布。

## Consequences

- 根版本的唯一可编辑来源是 `.cz.toml`，公开版本由远端不可移动的 Git tag 表达。
- `uvx` 首次执行需要能取得约束范围内的 Commitizen 4.x。
- atomic push 失败时，本地版本提交和 tag 会保留，远端 branch 与 tag 都不会部分更新。
- 模板维护者需要先在 `main` 完成审查和 CI，再确认执行 bump。

## Links

- [Architecture Overview](../architecture/overview.md)
- [模板创建与升级 Flow](../architecture/flows/template-lifecycle.md)
