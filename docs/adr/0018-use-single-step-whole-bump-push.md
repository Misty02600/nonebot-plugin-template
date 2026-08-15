# ADR-0018: 根模板与生成插件使用单步 bump 整体发布

- Status: Accepted
- Date: 2026-08-11

## Context

根模板和生成插件的 `just bump` 都需要完成版本提交、annotated tag 和远端发布触发。动态查询本次精确 tag
可以缩小推送范围，不过会增加跨平台 shell 求值。把本地 bump 与远端推送拆成两个 recipes 可以提供中间
检查点，但维护者不会在两步之间执行检查；日常流程只需要一个清楚、直接的发布入口。

生成插件原 recipe 已经使用 `git push --follow-tags`，但没有限制分支、明确远端或保证分支与 tags 原子
更新；根 recipe 则动态查询精确 tag。两层表达同一发布意图，不需要保留不同推送形状。

## Decision

1. 根模板与生成插件都只提供单步 `just bump`，不增加独立的 `push-release`。
2. Just 在执行前显示一次明确确认，并且只允许从 `main` 分支运行。
3. Commitizen 创建版本提交和 annotated tag；生成插件 recipe 随后刷新本地忽略的 `uv.lock`。
4. 两层都使用 `git push --atomic --follow-tags origin HEAD`，把当前提交和所有可达、远端尚不存在的
   annotated tags 作为一个原子操作推送到 `origin`。
5. 接受 `--follow-tags` 可能同时携带本地其他可达 annotated tags 的范围；不动态查询本次精确 tag，
   也不要求维护者手工填写 tag。
6. bump 不在本地重复质量检查、构建或发布职责；维护者在运行前确认 `main` 已通过 CI。

## Consequences

- 两层日常发布都只有一个命令和一次确认，不需要 PowerShell 专用脚本或额外的 tag 参数。
- 分支与 tags 要么全部推送成功，要么都不更新远端。
- 本地遗留且可达的 annotated tags 也可能被推送；匹配 release workflow 触发条件的 tag 会启动远端验证。
- 生成插件 workflow 会拒绝版本不匹配、轻量或不属于 `main` 历史的 tag，但已经推到远端的多余 tag
  需要维护者自行判断是否保留。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级 Flow](../architecture/flows/template-lifecycle.md)
- [ADR-0009: 根仓库与生成插件统一使用现代 Just PowerShell 配置](0009-align-modern-just-powershell-configuration.md)
- [ADR-0011: 根模板通过 Commitizen 发布版本](0011-use-root-commitizen-bump.md)
- [ADR-0015: 插件发布使用分阶段最小权限链](0015-stage-least-privilege-plugin-releases.md)
