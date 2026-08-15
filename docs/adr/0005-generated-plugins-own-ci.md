# ADR-0005: 生成插件独立拥有完整 CI

## Status

Accepted；部分替代 [ADR-0001](0001-use-copier-and-renovate.md) 中集中维护 reusable CI 的决定。

## Date

2026-08-10

## Context

ADR-0001 原先把 Ruff、BasedPyright 和 pytest 集中在根仓库的 `nb-plugin-ci.yml`，生成插件只保存一个
指向 `Misty02600/nonebot-plugin-template@main` 的调用入口。这能让维护者一次修改所有自有插件的 CI，
但也让生成项目在 Copier 更新链之外持续依赖中央仓库。

模板现已支持第三方直接 Fork，并从该 Fork 的 Git `origin` 推导 Copier 来源。若 CI 调用仍固定指向原仓库，
Fork 即使修改自己的工作流，生成项目也不会采用；`@main` 的变化还会绕过 Copier/Renovate 模板更新 PR，
直接改变所有调用者的检查行为。

`python-project-template` 已采用由最终项目拥有完整 CI、由模板控制仓库渲染并验证工作流的边界。NoneBot
模板可以采用同一所有权原则，同时保留自身既有依赖、测试矩阵和检查命令。

## Decision

1. `template/.github/workflows/ci.yml` 直接保存 Ruff、BasedPyright 和 pytest 的完整 jobs；生成插件不再调用
   本模板或其他仓库中的 reusable CI。
2. 根仓库删除 `nb-plugin-ci.yml`。根 `.github/workflows/ci.yml` 从当前 checkout 渲染一个插件，并在
   渲染结果中执行与生成 CI 相同的质量检查。
3. 模板通过 Copier 拥有 workflow 的结构、权限、jobs、steps 和检查范围；相关结构变化通过稳定模板 tag
   和 Renovate 创建的 Copier 更新 PR 进入插件。
4. 生成后的 active workflow 由插件仓库拥有。插件维护者可以独立修改，Action 版本由该插件自己的
   Renovate 例行维护，不再由中央 `@main` 在仓库外即时改变。
5. 保留当前 NoneBot 配置、Ruff/BasedPyright/pytest 命令和 Python 3.11–3.14 测试矩阵；本决定只调整
   CI 所有权和传播路径。

## Alternatives Considered

- 继续固定调用原仓库 `@main`：中央修改传播最快，但 Fork 不独立，且 CI 行为绕过模板更新 PR。
- 根据模板 `origin` 动态生成 reusable workflow 地址：Fork 可以调用自己的中央工作流，但每个生成项目
  仍依赖另一个仓库在线，且 `@main` 变化仍不经过 Copier 审查。
- 把 reusable workflow 固定到模板 tag：行为可复现，但每次模板版本仍需在 workflow 引用和 answers 中
  维护两条关联版本链，没有比直接生成完整 CI 更简单。

## Consequences

- 每个插件在其仓库中就能完整审查和修改 CI，不再依赖模板仓库的运行时可用性。
- Fork 修改 `template/.github/workflows/ci.yml` 后，其新项目自然采用 Fork 的工作流。
- CI 结构更新需要发布模板 tag，并由各插件逐个审查 Copier 更新 PR，不再即时影响全部插件。
- 根模板和生成项目会保存相似的检查步骤；根 CI 通过真实渲染验证生成结果，减少两边无意漂移。

## Implementation and Verification

- 生成源码：[`template/.github/workflows/ci.yml`](../../template/.github/workflows/ci.yml)。
- 模板自测：[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)。
- 根 CI 验证生成结果不包含 `nb-plugin-ci.yml`，也不再引用原仓库的 reusable workflow。

## Links

- [ADR-0001: 使用 Copier 与托管 Renovate](0001-use-copier-and-renovate.md)
- [ADR-0002: 保持 NoneBot 模板独立](0002-keep-the-nonebot-template-independent.md)
- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
