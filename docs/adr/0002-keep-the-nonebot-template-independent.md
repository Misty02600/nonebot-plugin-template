# ADR-0002: 保持 NoneBot 模板独立

## Status

Accepted

## Date

2026-08-10

## Context

本仓库曾评估让 `python-project-template` 输出一层通用配置，再由本仓库把该输出组合进
`template/`。这种方案可以减少少量重复文件，但会让最终插件的生命周期同时受到两个
Copier 模板、两份 answers、两套发布节奏和重叠文件所有权影响。

两个仓库也具有不同的产品边界：`python-project-template` 是通用 Python 项目模板；本仓库
需要长期表达 NoneBot 插件的依赖、测试、CI、发布和 Renovate 政策。二者都可能被第三方
直接使用或 Fork，不能假定永远由同一维护者、同一节奏发布。

## Decision

1. 本仓库继续作为完整、独立的 Copier 模板来源，不依赖或组合
   `python-project-template` 的生成结果。
2. 最终插件只提交本仓库生成的 `.copier-answers.yml`，只沿本仓库的 tag 和模板来源更新。
3. `template/` 中的 NoneBot 配置全部由本仓库拥有。Ruff、BasedPyright、pytest、Prek、
   Renovate、CI、release、依赖和 lockfile 政策不会因通用模板的变化自动改变。
4. `python-project-template` 只作为设计参考。可复用的维护原则通过单独审查、独立实现和
   本仓库测试吸收，不通过文件同步、嵌套 Copier 或第二份 answers 传播。
5. 任何第三方都可以 Fork 本仓库并自行修改其模板和工作流。该 Fork 是否继续跟随本仓库，
   以及其生成项目应记录原仓库还是 Fork 为模板来源，由 Fork 的维护者明确选择，而不是由
   隐含的共享层决定。

## Alternatives Considered

- 把通用模板作为父模板：通用模板无法自然拥有 NoneBot 特有骨架，反而要求父模板了解专用领域。
- 把通用配置作为嵌套 Copier 子模板：会引入第二份 answers、两阶段发布和同路径文件所有权冲突。
- 定期复制通用仓库中的配置文件：仍形成未声明的双重真源，漂移和覆盖风险无法通过 Copier 表达。
- 仅选择性借鉴设计原则：保留一个模板来源和清晰的文件所有权，同时接受两仓库会有少量重复
  实现。这是本次采用的方案。

## Consequences

- 最终插件只有一条模板更新链，`.copier-answers.yml` 不会因上游拆分而冗余或失效。
- 本仓库可以按 NoneBot 的兼容性和发布节奏演进，第三方 Fork 也不必跟随通用模板。
- 两个仓库可能重复实现输入校验、创建命令和测试工具；这些重复由各自的契约测试维护。
- 从 `python-project-template` 借鉴设计时，需要明确区分“方法适用”和“配置值相同”；现有
  NoneBot 配置默认保持不变。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建与升级](../architecture/flows/template-lifecycle.md)
- [ADR-0001: 使用 Copier 与托管 Renovate](0001-use-copier-and-renovate.md)
