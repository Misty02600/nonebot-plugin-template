# PLAN-0001: 推出 Copier 模板升级

| 状态 | 最后更新 |
|---|---|
| 讨论中 | 2026-08-12 |

## 背景

控制器、Copier 模板和本地契约已经集中到当前仓库，但仓库现在只有本地 `main` 分支，没有初始提交、
`origin` 或公开 tag。`just new` 必须从可公开读取的 GitHub `origin` 获取已发布模板，Hosted Renovate 也
必须在真实生成仓库中读取 `.copier-answers.yml`，所以本地渲染通过不等于升级链已经上线。

## 当前设计与缺陷

- `justfile::new` 从当前仓库的 fetch `origin` 推导模板来源；没有远端时会在创建目标目录前停止。
- `justfile::bump` 只允许从 `main` 创建版本提交和 annotated tag，并原子推送当前提交与可达 tags。
- `template/.github/renovate.json` 为生成仓库提供 Renovate 配置，`.copier-answers.yml` 是 Copier manager 的
  版本入口。
- 当前缺少真实 GitHub 仓库、模板 tag、试点插件和一次完整 Renovate 更新 PR，因此远端权限、版本发现、
  三方合并和恢复路径都尚未经过端到端验证。

## 技术路线

1. 根仓库的 [MIT 许可证](../done/0002-establish-root-license-and-provenance.md) 已就绪；完成适合作为全新
   历史根节点的初始提交。
2. 创建新的 GitHub 仓库，配置为 `origin`，推送 `main`，确认根 CI 对控制项目和真实渲染插件全部通过。
3. 运行 `just bump` 发布首个不可移动的模板 tag。根与生成插件的 Renovate 按
   [ADR-0021](../../adr/0021-maintain-workflow-seeds-and-active-copies-separately.md) 分别维护 workflow seed 与
   active 副本。
4. 使用 `just new` 创建一个低风险插件，确认生成仓库只包含 `template/` 的渲染结果，并运行自己的 CI。
5. 在试点仓库启用 Hosted Renovate；发布第二个只含可识别模板变化的 tag，验证 Renovate 能创建普通
   Copier 更新 PR，插件 CI 能检查更新，冲突时可由 `just finish-template-update` 接管。
6. 对既有插件逐个建立可信 Copier 基线；不手工伪造 `_commit`，也不引入自研同步器、GitHub App 或 PAT。

## 完成标准与验证

| 验收项 | 覆盖条件或输入 | 预期结果 | 验证方式 |
|---|---|---|---|
| 初始公开基线 | 新仓库 `main` 与首个模板 tag | 根 CI 通过，tag 可被 Copier 默认版本选择发现 | GitHub checks；在空目录执行一次 `copier copy` |
| 新插件创建 | 从新仓库运行 `just new` | 创建独立仓库；生成结果不含 `docs/` 或控制面文件 | 检查生成文件与插件 CI |
| 自动升级 | 试点插件处于首个 tag，再发布第二个 tag | Renovate 创建包含 `_commit` 更新的普通 PR | Hosted Renovate 日志、PR diff 与 checks |
| 冲突恢复 | 试点插件修改一个模板也维护的区域 | 冲突不会直接进入默认分支；解决后收尾检查通过 | PR 演练并运行 `just finish-template-update` |
| 既有插件迁移 | 选择一个已有插件建立基线 | 业务改动保留，后续模板更新可形成可审查 PR | 对比迁移前后 diff，并演练一次更新 |

## 相关文档

- [ADR-0001: 使用 Copier 与托管 Renovate](../../adr/0001-use-copier-and-renovate.md)
- [ADR-0005: 生成插件独立拥有完整 CI](../../adr/0005-generated-plugins-own-ci.md)
- [ADR-0021: 分别维护 workflow 模板 seed 与 active 副本](../../adr/0021-maintain-workflow-seeds-and-active-copies-separately.md)
- [Architecture overview](../../architecture/overview.md)
- [模板创建与升级](../../architecture/flows/template-lifecycle.md)
