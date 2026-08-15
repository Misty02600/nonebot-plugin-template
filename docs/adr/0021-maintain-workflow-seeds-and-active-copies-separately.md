# ADR-0021: 分别维护 workflow 模板 seed 与 active 副本

## Status

Accepted

## Date

2026-08-14

## Context

根 Renovate 会更新 `template/.github/workflows/` 中的 Action 与 uv 版本，使新生成插件获得当前可用的
workflow seed。插件生成后，其 Renovate 也会更新仓库内的 active workflow，使日常版本升级不必等待模板
发布。

这两条链维护的是不同仓库中的模板 seed 与 active 副本，不是两个自动化同时写同一个文件。Copier 后续
同步 workflow 编排时，会通过三方合并处理模板变化和插件已有修改；两侧恰好修改同一行且目标不同可能产生
冲突，但该冲突会留在模板更新 PR 中供维护者处理。

## Decision

1. 根 Renovate 继续维护根 active workflow 和 `template/.github/workflows/` 中的版本字段，保证控制 CI 与
   新项目 seed 保持可用。
2. 生成插件的 Renovate 继续维护其 active workflow，使插件可以独立接收 Action 与 uv 更新。
3. Copier 继续同步完整 workflow，包括编排和模板中的版本变化；不为版本字段排除 workflow 文件，也不
   增加自定义字段拆分机制。
4. 两侧更新到相同版本时接受重复变化自然收敛；更新到不同版本并触发三方合并冲突时，在 Copier 更新 PR
   中选择适合插件的版本，再运行既有收尾检查。

## Consequences

- 新生成插件不会因为模板停止维护版本字段而从陈旧 seed 起步。
- 已生成插件不必等待模板新 tag，即可通过自己的 Renovate 接收日常版本更新。
- 模板更新可能包含插件已经收到的相同版本变化，通常不会产生实际差异。
- 模板与插件对同一版本行做出不同修改时可能需要人工解决冲突；这是既有 Copier 三方合并边界，不再作为
  独立所有权缺陷处理。

## Links

- [ADR-0001: 使用 Copier 与托管 Renovate](0001-use-copier-and-renovate.md)
- [ADR-0005: 生成插件独立拥有完整 CI](0005-generated-plugins-own-ci.md)
- [ADR-0019: 使用可读 Action 版本并移除专用 workflow 扫描器](0019-use-readable-action-tags-without-dedicated-scanners.md)
- [Architecture overview](../architecture/overview.md)
- [PLAN-0001: 推出 Copier 模板升级](../plans/todo/0001-roll-out-copier-template-updates.md)
