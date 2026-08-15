# ADR-0014: 静态检查真实渲染后的 GitHub Actions

- Status: Superseded
- Date: 2026-08-11
- Superseded by: [ADR-0019](0019-use-readable-action-tags-without-dedicated-scanners.md)

## Context

模板控制仓库可以用 Copier 渲染插件并实际运行 Ruff、BasedPyright 和 pytest，但这些检查不会执行 release workflow，也不能完整验证 GitHub Actions 表达式、权限边界和常见供应链风险。直接检查 `template/` 源文件也可能漏掉渲染或条件生成后的实际内容。

生成插件独立拥有 active workflow，中央模板仍需要在发布新 tag 前证明它交付的 workflow 至少通过稳定、可复现的静态检查。

## Decision

- 根控制项目从当前工作树的无 Git 快照渲染一个默认 NoneBot 插件，递归枚举其中全部 `.yml` 和 `.yaml` workflow，并写出供 CI 消费的 manifest。
- manifest 必须包含生成项目的 `ci.yml` 与 `release.yml` 基线；缺失、空清单、重复路径或非 UTF-8 文件都使渲染步骤失败。
- 根 CI 对自身 workflow 与 manifest 中的真实生成文件运行 actionlint 和 zizmor。
- actionlint 与 zizmor 版本固定在根 workflow 环境变量中，并由根 Renovate 配置维护；actionlint 在无网络容器中运行，zizmor 使用离线、严格收集和常规 persona。
- 已知安全的 checkout 与 setup-uv Actions 固定到 immutable SHA。根 Renovate 维护模板源码中的依赖，生成后的 active workflow 继续由各插件自己的 Renovate 维护。

## Consequences

- workflow 结构、表达式和安全策略问题能在模板 tag 发布前暴露，而不是等到插件 CI 或 release 首次触发。
- 验证对象是 Copier 的真实输出；新增嵌套 workflow 会自动进入清单，不需要手工维护文件列表。
- CI 增加一次渲染、一个 actionlint 容器和一次 zizmor 执行；固定版本保证本地与远端结果可复现。
- 静态检查不等价于真实 GitHub Actions 执行，发布和权限行为仍需由试点仓库验证。

## Links

- [Architecture Overview](../architecture/overview.md)
- [ADR-0005: 生成插件独立拥有完整 CI](0005-generated-plugins-own-ci.md)
- [ADR-0012: 根仓库使用独立的 Python 控制项目](0012-use-a-python-controller-project.md)
