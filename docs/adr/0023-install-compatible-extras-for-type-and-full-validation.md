# ADR-0023: 类型检查与全量验证安装所有可共同安装的 extras

## Status

Accepted

## Date

2026-08-31

## Context

生成插件的 BasedPyright 配置只检查 `src`，但插件源码可以导入声明在
`[project.optional-dependencies]` 中的可选依赖。若类型检查环境只安装基础依赖和 `type` group，
这些合法导入仍可能因为对应 extra 没有安装而被报告为缺失。发布验证、本地完整同步和模板更新收尾也应
覆盖项目声明的完整、可共同安装的依赖表面，而不是只验证基础依赖。

`uv sync --all-extras` 会同时选择项目声明的全部 extras。这适合默认模板及可以共同解析的 extras，
但不能替叶子项目决定互斥功能应采用哪一种组合。若项目的 extras 天生不能同时安装，模板也无法在不了解
项目契约的前提下安全猜测应排除哪一项。

## Decision

1. BasedPyright 继续只检查 `src`；安装更多 extras 不用于扩大静态检查范围，也不把 `tests` 纳入
   BasedPyright 默认入口。
2. 生成插件 CI 的 BasedPyright job，以及根仓库对真实渲染项目运行的对应 job，安装基础项目、`type`
   group 和全部 extras。
3. 生成插件的 release 验证、本地 `just sync` 和 `just finish-template-update` 安装全部 dependency
   groups 与全部 extras；模板更新收尾仍使用 lockfile 锁定的环境。
4. `--all-extras` 只代表“安装所有可共同安装的 extras”。定义互斥 extras、或无法让全部 extras
   同时解析的叶子项目，必须按自身支持契约显式选择兼容组合，并相应调整自己的 CI、发布或本地 recipe；
   模板不维护通用的隐式排除清单。
5. 本决定由本仓库独立拥有。`python-project-template` 可以作为设计参考，但不成为运行依赖、Copier
   父模板、同步源或第二条更新链。

## Consequences

- `src` 中面向可选功能的合法导入会在 BasedPyright 运行前获得对应依赖，减少由环境不完整造成的缺失
  import 报告。
- CI 类型检查、发布验证、本地完整同步和模板更新收尾对 extras 的默认覆盖保持一致；发布前也会更早发现
  可共同安装 extras 之间的解析冲突。
- 默认同步和全量验证可能下载更多依赖并增加解析、安装时间。
- 不能共同安装全部 extras 的叶子项目必须显式维护受支持组合；这类领域选择不能由通用模板自动推导。
- BasedPyright 仍不检查 `tests`，测试矩阵也继续只安装自己的测试依赖边界。
- 本仓库可以独立调整这项策略，不要求通用 Python 模板同步发布或保持相同文件内容。

## Rejected alternatives

- 类型检查只安装基础依赖与 `type` group：无法覆盖 `src` 中由 extras 提供的合法导入。
- 扩大 BasedPyright 范围或屏蔽可选依赖的缺失 import：前者改变了独立的检查范围决策，后者会隐藏真实的
  依赖声明错误，都没有解决检查环境不完整的问题。
- 在模板中枚举具体 extra：模板无法预知叶子项目后续增加的功能，也不能替项目决定互斥组合。
- 从 `python-project-template` 同步配置或在运行时组合其输出：会重新引入第二真源和更新依赖，违反模板
  独立性。

## Implementation

- `template/pyrightconfig.json` 保持 `include: ["src"]`。
- `template/.github/workflows/ci.yml` 和根 `.github/workflows/ci.yml` 的渲染项目类型检查安装
  `--all-extras`。
- `template/.github/workflows/release.yml` 与 `template/justfile` 的全量验证入口安装 `--all-extras`，
  生成 README 同步说明明确这一范围。
- 契约测试保护 CI、release、Just 与生成说明中的命令保持一致。

## Links

- [ADR-0002: 保持 NoneBot 模板独立](0002-keep-the-nonebot-template-independent.md)
- [ADR-0005: 生成插件独立拥有完整 CI](0005-generated-plugins-own-ci.md)
- [ADR-0013: 为生成插件提供可恢复的手工模板更新入口](0013-provide-manual-template-update-recovery.md)
- [ADR-0015: 插件发布使用分阶段最小权限链](0015-stage-least-privilege-plugin-releases.md)
- [Architecture overview](../architecture/overview.md)
