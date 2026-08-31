# Architecture Overview

## 目的

本仓库统一维护 NoneBot 插件项目的脚手架、CI 初始结构和模板生命周期说明。新插件由 Copier 生成，模板生命周期设计为由 Renovate 提交逐仓库升级 PR。

## 系统形态

仓库分为控制面与生成面：

- 仓库根目录是非打包的 Python 控制项目，保存 Copier 配置、契约测试、模板自测工作流和维护文档。
- `template/` 是唯一的插件脚手架源码。
- 本仓库不组合其他 Copier 模板；通用模板只作为设计参考，不形成生成或更新依赖。
- 生成后的插件仓库保存 `.copier-answers.yml`，用于追踪模板来源和版本。
- 生成插件保存完整 CI，并在自己的仓库中运行 Ruff、BasedPyright 和 pytest。
- `release.yml` 由各插件本地保存，以配合逐仓库的 PyPI Trusted Publishing 配置；发布前先在只读 job
  验证 tag、源码与发行包，再由两个最小权限 job 复用同一份 artifact。

## 主要模块

| Module | Responsibility | Important Dependencies |
|---|---|---|
| `.cz.toml` | 保存根模板仓库当前版本与 tag 规则 | Commitizen |
| `pyproject.toml`、`uv.lock` | 固定非打包控制项目的维护工具与可复现环境 | uv、Python 3.11+ |
| `tests/` | 验证 Copier answers、输入边界、Just 编排、真实版本更新、分发构建与生成 workflow 契约 | pytest、Copier、Git、Just、uv |
| `copier.yml` | 定义模板问题、默认值与 `template/` 生成根目录 | Copier 9.17+ |
| `template/` | 保存插件仓库的完整可更新脚手架 | Jinja、NoneBot、uv |
| `justfile` | 创建和发布模板，并运行控制项目的测试、lint、格式与类型检查 | Just 1.56+、PowerShell 7、uv、Copier、Commitizen、git、GitHub CLI |
| `template/.github/workflows/ci.yml` | 生成插件自有的 Ruff、BasedPyright 和 pytest CI | GitHub Actions、uv |
| `template/.github/workflows/release.yml` | 验证精确 tag 与发行包，并分阶段发布 PyPI 和 GitHub Release | GitHub Actions、uv、Python 标准库、git-cliff |
| `.github/workflows/ci.yml` | 验证控制项目，并真实渲染和检查生成插件 | Copier、GitHub Actions、uv |
| `.github/renovate.json` | 维护控制依赖和模板源码中的依赖版本 | Hosted Renovate |
| `docs/` | 保存架构、决策和迁移计划；不进入生成结果 | repo-docs |
| bootstrap Skill | 将自然语言创建请求转交给 `just new` | Codex、just |
| Hosted Renovate | 发现模板新 tag，并为插件创建 Copier 更新 PR | `.copier-answers.yml`、Git tags |

## 核心运行机制

Copier 只渲染 `template/`。模板不使用 tasks、migrations 或自定义 Jinja extensions，因此无需执行受信任脚本，并可由托管 Renovate 安全更新。

根控制项目通过 `[tool.uv].package = false` 明确不构建或发布 Python 包。根 `uv.lock` 固定 Copier、pytest、Ruff 和 BasedPyright 的维护依赖；本地 uv 按仓库命令实际使用的功能执行。根测试保护输入验证、创建命令、真实 Copier 更新、分发构建和默认渲染契约，生成插件自己的质量检查继续保护最终运行项目。`just test-fast` 只跳过标记为 integration 的外部工具链测试；完整 `just test` 会尝试运行全部测试，但依赖 Just 或 PowerShell 的测试只在对应工具可用时执行。控制仓库 CI 不安装 Just，远端门禁保护不依赖 Just 的契约，实际 recipe 执行由具备工具的本地完整测试保护。

`template/` 中的工具配置、依赖和工作流都由本仓库独立拥有。生成插件不跟踪 `uv.lock`，因此模板为 Commitizen、prek 和 BasedPyright 等维护工具保留当前主版本上界，避免模板未变化时由新主版本改变 fresh resolve。借鉴其他模板时只吸收经过审查的维护原则，不同步文件，也不向最终插件写入第二份 Copier answers。

生成后的插件独立拥有 active CI。模板维护 workflow 结构并通过 Copier 更新 PR 传播变化；插件自己的
Renovate 例行维护 Action 版本，插件维护者也可以按项目需要独立调整。CI 不再运行时调用模板仓库的
`@main`，因此 Fork 的工作流修改不会被原仓库覆盖。生成插件的每个 pull request 都运行完整 CI，不使用
路径过滤跳过维护配置或模板升级 PR。

根仓库和生成插件都要求 Just 1.56+；Windows 上的普通 recipes 通过条件化 `set shell` 使用 PowerShell 7 的 `pwsh`，Unix 上保留平台默认 shell。根 `justfile` 的 `just new` 在 Windows、Linux 和 macOS 上都显式通过 `pwsh` 执行，当前脚本不固定 7.x 小版本。它从所在 Git 仓库的 fetch `origin` 自动推导 Copier 来源，并把受支持的公开 GitHub URL 规范成 HTTPS。它验证 Git、仓库根目录、`origin` 和远端可访问性，但不自行枚举或筛选 tag；模板版本由 Copier 的默认规则选择。来源解析失败时不回退。生成插件的 `repo_owner` 来自当前 GitHub CLI 登录账号，与模板来源分别维护；直接调用 Copier 时由调用者回答该问题。正式创建入口不提供组织或其他账号 owner 参数。

创建入口只保护模板来源、目标已存在等会改变更新身份或覆盖已有目录的边界。入口不重复实现平台与 Python 命名规则；Copier 统一验证 GitHub owner、1 到 100 字符的仓库名、Python 模块名、作者名和邮箱，并排除关键字及 Python 3.11–3.14 标准库顶层模块。可见性等平台参数由 `gh` 验证，失败时允许保留本地目录或仓库供调用者检查、修正或清理。创建入口和 Copier 问答都不收集项目简介，生成项目的包元数据与 GitHub 仓库描述由插件维护者后续补充。Jinja 中进入 TOML 或 Python 字面量的问答值按数据序列化，不作为源码片段拼接。

根 `.cz.toml` 使用 Commitizen 自身的 version provider 保存当前模板版本。维护者在 `main` 上运行 `just bump`，随后通过 `uvx` 临时运行 Commitizen，创建版本提交和 PEP 440 兼容的 annotated tag，再使用 `git push --atomic --follow-tags origin HEAD` 整体推送当前提交与可达 annotated tags。根仓库不发布 Python 包；远端 tag 就是 Copier 可发现的模板版本。插件仓库中的 `.copier-answers.yml` 记录来源、版本和生成参数；该文件由 Copier 管理，不应手工编辑。

Hosted Renovate 是插件采用模板升级的主要入口。生成项目同时提供 `update-template` 和可独立重跑的 `finish-template-update`，用于本地复现、解决 `.rej` 冲突或接管 Renovate PR；收尾阶段统一检查 diff、lock、hooks 和全部质量命令。

根 CI 检查控制项目，并真实渲染默认插件后运行 Ruff、BasedPyright 和 Python 版本矩阵；契约测试保护所有 pull request 都触发生成 CI，以及 release workflow 的最小权限和 artifact 顺序。BasedPyright 仍只检查 `src`，其生成 CI job 和根 CI 的渲染项目 job 会同时安装 `type` group 与全部 extras，使源码中的可选依赖导入在完整环境中解析。生成插件的 release 验证、本地 `just sync` 与 `just finish-template-update` 则安装全部 groups 和全部 extras；这一默认策略只覆盖可共同安装的 extras，定义互斥 extras 的叶子项目必须显式选择自己的兼容组合。

生成 CI 会取消同一 PR 中已被新提交取代的旧运行，但保留不同 PR 与每次 `main` push 的完整检查。根 CI 不再维护 actionlint、zizmor 或 workflow manifest 扫描链。

GitHub 官方 Actions 使用可读 major tag，setup-uv Action 使用精确 semver tag，workflow 的 `version` 输入也固定精确 uv CLI 版本；根 Renovate 维护控制依赖和模板 seed 中的 Action 引用，生成后的 active workflow 由插件仓库自己的 Renovate 独立维护。两条更新链维护不同仓库中的 seed 与 active 副本，Copier 更新时按三方合并处理重叠变化。根仓库和生成插件中获准自动合并的 Renovate PR 统一使用 rebase，不产生额外 merge commit；uv patch 更新可以在门禁通过后自动合并，minor/major 更新仍需人工审查。

插件 release workflow 在无发布权限的 `validate` job 中确认版本、annotated tag 与 `main` 祖先关系，
重跑 Ruff、BasedPyright 和 pytest，构建一个 wheel 与一个 sdist，并检查归档数量、完整性和安全路径。通过后，reviewed artifact
依次交给仅有 PyPI OIDC 权限的发布 job 和仅有 GitHub 内容写权限的 Release job；高权限阶段不重新
checkout 或构建。

生成 README 只说明仓库内的发布入口，不承担 PyPI 或 GitHub 的一次性外部配置教程。若新插件尚未在
PyPI 配置匹配的 Trusted Publisher，发布 job 会明确失败，依赖它的 GitHub Release job 不会运行；
维护者完成配置后重跑失败的 workflow 即可，不需要重新创建版本提交或 tag。这个可恢复的首次配置失败
是有意接受的维护边界。

插件维护者在已通过 CI 的 `main` 上运行单步 `just bump`。Commitizen 创建版本提交和 annotated
tag，recipe 使用 `git push --atomic --follow-tags origin HEAD` 将当前提交及其可达的 annotated tags
整体推送并触发远端 release workflow。该入口有意接受 `--follow-tags` 可能携带其他本地 annotated tags
的范围，以保持无需中间检查或动态 tag 查询的单步流程。

## 数据与状态

- 待发布模板版本：根 `.cz.toml`。
- 已发布模板版本：中央仓库不可移动的 Git tag。
- 插件采用的版本和参数：插件仓库 `.copier-answers.yml`。
- 插件自己的业务改动：保留在各插件仓库中，由 Copier 的三方差异合并处理。
- 未解决的模板冲突：只存在于 Renovate PR，合并前由维护者处理。

## 外部系统或 Reference Models

- [Copier template configuration](https://copier.readthedocs.io/en/stable/configuring/)
- [Copier project updates](https://copier.readthedocs.io/en/stable/updating/)
- [Renovate Copier manager](https://docs.renovatebot.com/modules/manager/copier/)
- [GitHub CLI repository creation](https://cli.github.com/manual/gh_repo_create)

## 重要 Flows

- [模板创建与升级](flows/template-lifecycle.md)

## Architecture Decisions

- [ADR-0001: 使用 Copier 与托管 Renovate](../adr/0001-use-copier-and-renovate.md)
- [ADR-0002: 保持 NoneBot 模板独立](../adr/0002-keep-the-nonebot-template-independent.md)
- [ADR-0003: 使用显式模板来源常量](../adr/0003-use-an-explicit-template-source-constant.md)
- [ADR-0004: 从 Git origin 推导模板来源](../adr/0004-derive-template-source-from-origin.md)
- [ADR-0005: 生成插件独立拥有完整 CI](../adr/0005-generated-plugins-own-ci.md)
- [ADR-0006: 使用 Copier 默认模板版本选择](../adr/0006-use-copier-default-version-selection.md)
- [ADR-0007: 使用当前 GitHub CLI 账号作为生成仓库 owner](../adr/0007-use-current-gh-account-as-repository-owner.md)
- [ADR-0008: 根创建入口统一使用跨平台 PowerShell](../adr/0008-use-cross-platform-powershell-for-creation.md)
- [ADR-0009: 根仓库与生成插件统一使用现代 Just PowerShell 配置](../adr/0009-align-modern-just-powershell-configuration.md)
- [ADR-0010: 创建时不采集项目简介](../adr/0010-defer-project-description.md)
- [ADR-0011: 根模板通过 Commitizen 发布版本](../adr/0011-use-root-commitizen-bump.md)
- [ADR-0012: 根仓库使用独立的 Python 控制项目](../adr/0012-use-a-python-controller-project.md)
- [ADR-0013: 为生成插件提供可恢复的手工模板更新入口](../adr/0013-provide-manual-template-update-recovery.md)
- [ADR-0014: 静态检查真实渲染后的 GitHub Actions](../adr/0014-statically-validate-rendered-workflows.md)
- [ADR-0015: 插件发布使用分阶段最小权限链](../adr/0015-stage-least-privilege-plugin-releases.md)
- [ADR-0016: Just 相关控制层测试保留为本地集成测试](../adr/0016-keep-just-dependent-controller-tests-local.md)
- [ADR-0017: 生成插件的所有 pull request 都运行 CI](../adr/0017-run-generated-ci-for-every-pull-request.md)
- [ADR-0018: 根模板与生成插件使用单步 bump 整体发布](../adr/0018-use-single-step-whole-bump-push.md)
- [ADR-0019: 使用可读 Action 版本并移除专用 workflow 扫描器](../adr/0019-use-readable-action-tags-without-dedicated-scanners.md)
- [ADR-0020: 只在 GitHub workflows 固定 uv CLI 版本](../adr/0020-pin-uv-only-in-github-workflows.md)
- [ADR-0021: 分别维护 workflow 模板 seed 与 active 副本](../adr/0021-maintain-workflow-seeds-and-active-copies-separately.md)
- [ADR-0022: 不使用 Twine 重复检查发行包元数据](../adr/0022-validate-distributions-without-twine.md)
- [ADR-0023: 类型检查与全量验证安装所有可共同安装的 extras](../adr/0023-install-compatible-extras-for-type-and-full-validation.md)

## 已知风险或不清楚区域

- 既有插件需要逐仓库建立可信的 Copier 基线，不能仅补写 answers 文件。
- Hosted Renovate 的首次安装、权限和 PR 行为仍需在一个低风险插件上验证。
