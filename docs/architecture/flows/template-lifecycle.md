# Flow: 模板创建与升级

## 目的

说明新插件如何从中央模板生成，以及中央模板升级如何以可审查 PR 进入插件仓库。

## 触发方式

- 新建：维护者在中央仓库运行 `just new`；Codex Skill 只作为该命令的对话入口。
- 升级：维护者在中央仓库运行 `just bump`，发布新的 PEP 440 兼容 Git tag。
- 模板来源：生成和升级都只使用本仓库，不执行嵌套模板更新。

## 参与者

- 本地 bootstrap Skill
- Copier
- Commitizen
- 根 uv 控制项目与 pytest 契约测试
- Just 1.56+ 与 PowerShell 7
- git 与 GitHub CLI
- Hosted Renovate
- 插件维护者
- 插件自有 CI
- 插件自有 release workflow 与 PyPI Trusted Publishing

本地 uv 按仓库命令实际使用的功能执行。GitHub workflows 通过 setup-uv 的 `version` 输入安装精确 uv CLI
版本；Renovate 对 workflow 中的 uv patch 更新可以在门禁通过后自动合并，minor 与 major 更新仍需人工审查。

## Happy Path

### 新建插件

1. 维护者在 Windows、Linux 或 macOS 上通过 `pwsh` 运行 `just new <仓库名> [可见性]`。
2. `just` 从模板仓库根目录的 fetch `origin` 推导并验证公开 HTTPS 来源。
3. Copier 按默认规则选择远端模板版本，渲染 `template/` 并写入 `.copier-answers.yml`。
4. `just` 初始化 `main` 分支并创建初始提交。
5. `gh repo create --source . --push` 使用当前 GitHub CLI 登录账号创建远端仓库并推送。
6. 插件仓库自己的 GitHub CI 运行 Ruff、BasedPyright 和 pytest。

### 发布模板

1. 模板变更通过根控制项目的 Ruff、BasedPyright、pytest 契约测试，以及生成插件的 Ruff、BasedPyright 和 Python 版本矩阵验证后合并到 `main`。
2. 维护者运行 `just bump`，确认发布意图；该入口只允许在 `main` 执行。
3. Commitizen 更新根 `.cz.toml` 中的版本，创建版本提交和 `vX.Y.Z` annotated tag。
4. `git push --atomic --follow-tags origin HEAD` 同时推送当前 `HEAD` 与可达的 annotated tags；远端版本 tag 随即成为 Copier 可选择的模板版本。

### 发布插件

1. 维护者从 `main` 的发布提交推送与项目版本一致的 annotated `vX.Y.Z` tag。
2. 插件 release workflow 的只读 `validate` job 验证版本、tag 类型和 `main` 祖先关系，重跑质量检查，
   构建并严格检查 wheel 与 sdist。
3. workflow 上传包含发行包与 release notes 的 reviewed artifact。
4. 只具有 OIDC 权限的 `publish-pypi` job 通过 Trusted Publishing 发布该 artifact。
5. PyPI 成功后，只具有 GitHub 内容写权限的 `github-release` job 使用同一 artifact 创建 Release。

### 升级插件

1. 中央模板通过 `just bump` 发布新 tag。
2. Hosted Renovate 从插件的 `.copier-answers.yml` 识别模板依赖和当前版本。
3. Renovate 执行安全模式下的 Copier update，并创建普通升级 PR。
4. 插件 CI 检查生成结果；维护者检查配置、README 和可能的冲突。
5. 维护者合并 PR，插件采用新的模板版本。

### 手工接管升级

1. 维护者在生成插件的干净工作树运行 `just update-template`；Copier 根据 answers 中的来源和版本执行默认更新。
2. 命令自动调用 `just finish-template-update`，检查工作树和暂存区 whitespace、残留 `.rej`、本地 lock、hooks、Ruff、BasedPyright 和 pytest。
3. 若 Copier 因冲突中断，维护者解决冲突后直接运行 `just finish-template-update`，不重复应用模板更新。

## 数据或状态变化

- 新建时产生 `.copier-answers.yml`、本地 Git 历史和 GitHub 仓库。
- 发布模板时根 `.cz.toml`、版本提交和本地 tag 一起推进；atomic push 成功后远端分支与 tag 同时可见。
- 升级时 `.copier-answers.yml` 的 `_commit` 更新为新 tag。
- 最终插件不保存第二个模板的 answers；其他模板的版本不会直接进入插件更新链。
- 所有模板差异先进入 PR，不由中央仓库直接写入插件默认分支；CI 结构也遵循这条路径，不再通过中央
  `@main` 在 Copier 更新之外改变。

## Error Paths

- 目标目录已存在：`just` 在生成前停止。
- `pwsh` 不可用：Just 无法启动创建脚本，不会进入 Copier 或创建目标目录。
- Git、模板仓库根目录或 `origin` 缺失：`just` 在创建目标目录前停止，不回退到其他模板来源。
- `origin` 不是受支持的公开 GitHub 地址或远端不可读取：`just` 在创建目标目录前停止。
- 模板无法渲染：Copier 失败，不创建远端仓库。
- 远端仓库已存在或推送失败：`gh` 报错，并保留本地生成目录。
- 生成结果检查失败：GitHub CI 失败，由维护者修正或删除新仓库。
- 非 `main` 分支运行 `just bump`：入口在创建版本提交前停止。
- Commitizen bump 失败：不推送任何远端引用。
- atomic push 失败：本地版本提交和 tag 保留，远端分支与 tag 都不更新。
- Copier 合并冲突：Renovate PR 保持未合并，由维护者解决或关闭。
- 模板包含 unsafe 功能：Hosted Renovate 无法安全运行；该变更不得发布。
- 手工更新时工作树不干净：`update-template` 在 Copier 启动前停止，避免业务修改进入三方合并。
- Copier 留下 `.rej`：`finish-template-update` 停止；维护者解决后可以重跑收尾阶段。
- 插件 tag 不是 annotated tag、不属于 `main` 历史或与项目版本不一致：release 在只读验证阶段停止。
- 插件发行包数量、元数据或归档检查失败：不上传 PyPI，也不创建 GitHub Release。
- PyPI 发布失败：GitHub Release 不创建；修复 Trusted Publisher 配置后重跑。
- GitHub Release 创建失败：PyPI 文件保持不变；维护者可以针对同一 tag 重跑 workflow。

## 相关代码

- `copier.yml`
- `.cz.toml`
- `template/`
- `justfile`
- `.github/workflows/ci.yml`
- `template/.github/workflows/ci.yml`
- `template/.github/workflows/release.yml`
- 本机 Codex personal plugin 中的 `bootstrap-nonebot-plugin-repo` Skill

## 相关 ADR

- [ADR-0001: 使用 Copier 与托管 Renovate](../../adr/0001-use-copier-and-renovate.md)
- [ADR-0002: 保持 NoneBot 模板独立](../../adr/0002-keep-the-nonebot-template-independent.md)
- [ADR-0004: 从 Git origin 推导模板来源](../../adr/0004-derive-template-source-from-origin.md)
- [ADR-0005: 生成插件独立拥有完整 CI](../../adr/0005-generated-plugins-own-ci.md)
- [ADR-0006: 使用 Copier 默认模板版本选择](../../adr/0006-use-copier-default-version-selection.md)
- [ADR-0008: 根创建入口统一使用跨平台 PowerShell](../../adr/0008-use-cross-platform-powershell-for-creation.md)
- [ADR-0009: 根仓库与生成插件统一使用现代 Just PowerShell 配置](../../adr/0009-align-modern-just-powershell-configuration.md)
- [ADR-0010: 创建时不采集项目简介](../../adr/0010-defer-project-description.md)
- [ADR-0011: 根模板通过 Commitizen 发布版本](../../adr/0011-use-root-commitizen-bump.md)
- [ADR-0013: 为生成插件提供可恢复的手工模板更新入口](../../adr/0013-provide-manual-template-update-recovery.md)
- [ADR-0014: 静态检查真实渲染后的 GitHub Actions](../../adr/0014-statically-validate-rendered-workflows.md)
- [ADR-0015: 插件发布使用分阶段最小权限链](../../adr/0015-stage-least-privilege-plugin-releases.md)
- [ADR-0018: 根模板与生成插件使用单步 bump 整体发布](../../adr/0018-use-single-step-whole-bump-push.md)
- [ADR-0019: 使用可读 Action 版本并移除专用 workflow 扫描器](../../adr/0019-use-readable-action-tags-without-dedicated-scanners.md)
- [ADR-0020: 只在 GitHub workflows 固定 uv CLI 版本](../../adr/0020-pin-uv-only-in-github-workflows.md)
- [ADR-0017: 生成插件的所有 pull request 都运行 CI](../../adr/0017-run-generated-ci-for-every-pull-request.md)
