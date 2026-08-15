# PLAN-0005：取消被新提交取代的生成 CI

| 状态 | 最后更新 |
|---|---|
| 进行中 | 2026-08-16 |

## 背景

生成插件对所有目标为 `main` 的 pull request 运行完整 CI，并对 Python 3.11–3.14 执行测试矩阵。同一分支或
PR 短时间连续 push 时，旧提交的检查已经不能代表最新代码，但当前仍会与新运行并行占用 runner。

## 当前设计与缺陷

`template/.github/workflows/ci.yml` 已配置 workflow-level `concurrency`：同一 PR 的 group 使用 workflow
名称与 PR number，新提交会取消该 PR 的旧运行；非 PR 事件使用唯一 `github.run_id`，因此不同 PR 与每次
`main` push 不会互相取消。release workflow 不在本计划范围内。当前实现和契约测试已经完成，但尚未在
真实 GitHub Actions 中观察取消记录和保留运行。

## 技术路线

1. 在生成 CI 顶层按 workflow 与 PR number 建立 concurrency group；非 PR 事件使用唯一的 `github.run_id`
   作为后备值。
2. 只在 `pull_request` 事件设置 `cancel-in-progress`；同一 PR 的新提交取消旧运行，不同 PR 与每次
   `main` push 都完整运行。
3. 在 `tests/test_rendered_project.py` 对真实渲染 workflow 断言 group 表达式和取消策略。

## 实施进度

- 已完成：生成 CI 的 concurrency 配置、PR-only 取消策略和真实渲染契约测试。
- 下一步：在 PLAN-0001 的试点插件中连续推送同一 PR，并核对不同 PR 与 `main` push 的 Actions 记录。
- 当前阻塞：模板仓库尚未建立公开远端和试点插件，无法完成线上行为验证。

## 完成标准与验证

| 验收项 | 覆盖条件或输入 | 预期结果 | 验证方式 |
|---|---|---|---|
| 同一 PR 连续提交 | PR ref 先运行 A，再 push B | B 启动后 A 被取消，B 完整运行 | 试点仓库 Actions 记录 |
| 不同 PR | 两个 PR 同时运行 | 两轮互不取消 | 试点仓库 Actions 记录 |
| `main` 连续 push | 两个提交先后进入 `main` | 两轮都完整运行 | 试点仓库 Actions 记录 |
| 检查内容 | 任一保留的最新运行 | Ruff、BasedPyright 与四版本 pytest 不变 | workflow 契约测试与 GitHub checks |
| YAML 与表达式 | 默认模板渲染 | concurrency 字段和 GitHub 表达式原样保留 | `tests/test_rendered_project.py`，并在试点仓库核对 Actions 运行 |

## 相关文档

- [ADR-0005：生成插件独立拥有完整 CI](../../adr/0005-generated-plugins-own-ci.md)
- [ADR-0017：生成插件的所有 pull request 都运行 CI](../../adr/0017-run-generated-ci-for-every-pull-request.md)
- [ADR-0019：使用可读 Action 版本并移除专用 workflow 扫描器](../../adr/0019-use-readable-action-tags-without-dedicated-scanners.md)
