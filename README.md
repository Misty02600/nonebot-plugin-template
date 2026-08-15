# nonebot-plugin-template

NoneBot 插件的中央 Copier 模板与维护控制仓库。

新插件从 `template/` 生成；每个插件拥有并运行自己的完整 CI；模板升级设计为由 Hosted Renovate 以逐仓库 PR 交付。仓库内的 `docs/` 只记录中央维护知识，不会进入生成的插件。

本仓库不依赖或组合 `python-project-template`。二者可以借鉴相同的维护设计，但本仓库独立拥有全部 NoneBot 配置，生成插件也只跟随这一条 Copier 更新链。

## 创建新插件

推荐入口需要 Just 1.56.0 或更高版本、uv/uvx、Git、已登录的 GitHub CLI，以及可通过 `pwsh` 调用的 PowerShell 7。`just new` 在 Windows、Linux 和 macOS 上都使用同一个 PowerShell 入口。

在本仓库运行一个命令即可创建公开插件仓库：

```console
just new nonebot-plugin-example
```

该命令让 Copier 从远端按默认规则选择模板版本，在本仓库的同级目录生成项目，然后创建初始 Git 提交，并使用当前 `gh` 登录账号作为 `repo_owner` 创建和推送 GitHub 仓库。第二个可选参数是可见性，例如 `just new nonebot-plugin-example private`。

`just new` 从根 `justfile` 所在 Git 仓库的 fetch `origin` 自动确定 Copier 模板来源，并把受支持的 GitHub HTTPS/SSH 地址规范成公开 HTTPS 地址。该来源会写入生成项目的 `.copier-answers.yml`，决定以后从哪里取得模板更新；它与 `repo_owner` 独立，后者只决定插件仓库创建到哪个 GitHub 用户或组织下。

标准 clone 会让官方仓库的生成项目跟随官方模板，也会让 Fork clone 中的生成项目跟随该 Fork。Fork 的本地未推送修改不会进入生成结果；把 Fork 作为独立模板使用前，必须先推送修改，并通过自己的 `bump` 流程发布和永久保留新版本。无论模板来自官方仓库还是 Fork，生成仓库都归当前 `gh` 登录账号所有。

模板来源不接受命令参数，也不会在读取失败时回退到官方地址。Git、模板仓库根目录、`origin` 或可公开读取的 GitHub 远端任一缺失时，`just new` 都会在创建目标目录前停止。版本发现和排序由 Copier 负责。

`just new` 需要已经登录的 GitHub CLI，因为它负责创建和推送远端仓库。没有 `gh` 时仍可直接运行 Copier 生成本地项目；Copier 会询问 `repo_owner`，远端仓库和首次推送由调用者自行完成。当前入口不提供组织或其他账号 owner 参数。

`just new` 不收集项目简介，也不会为生成项目的包元数据或 GitHub 仓库写入占位描述；这些内容由插件维护者在明确项目用途后补充。创建入口不重复实现平台与 Python 命名规则，Copier 会验证 GitHub owner、1 到 100 字符的仓库名、模块名、作者名和邮箱，并拒绝 Python 关键字及支持版本中的标准库顶层模块名。`gh` 可见性等平台参数仍由对应工具验证；失败时保留本地目录供调用者检查、修正或清理。

Ruff、BasedPyright 和 pytest 由推送及所有 pull request 的 GitHub CI 检查，不在创建流程中重复运行。模板发布版本由根目录的 `just bump` 统一推进；正式使用前必须先完成当前改动的审查和 CI 验证。

本机 Codex 的 `bootstrap-nonebot-plugin-repo` Skill 后续只作为这个命令的对话入口，不再维护另一套创建逻辑。

不要手工编辑生成仓库中的 `.copier-answers.yml`。该文件记录模板来源、版本和生成参数，也是 Renovate 识别模板更新的入口。

## 仓库结构

```text
.
├── .cz.toml                           # 根模板仓库的版本与 tag 规则
├── copier.yml                         # Copier 问题、默认值与模板子目录
├── pyproject.toml、uv.lock            # 非打包控制项目及其锁定工具环境
├── tests/                             # Copier、Just、真实更新、构建和 workflow 契约
├── template/                          # 唯一的插件脚手架源码
│   ├── .github/
│   │   ├── renovate.json              # 插件的 Renovate 配置
│   │   └── workflows/
│   │       ├── ci.yml                 # 插件自有的 Ruff、BasedPyright、pytest CI
│   │       └── release.yml            # 分阶段验证并发布 PyPI 与 GitHub Release
│   ├── src/{{ module_name }}/         # 动态 Python 包目录
│   ├── tests/                         # 插件测试骨架
│   ├── README.md.jinja                # 插件 README
│   └── pyproject.toml.jinja           # 插件项目元数据
├── .github/workflows/
│   └── ci.yml                         # 渲染插件并执行同等质量检查的模板自测
├── .github/renovate.json              # 控制仓库依赖和 workflow 版本更新
└── docs/                              # 仅中央仓库使用的架构与计划
```

生成后的插件包含以下独立工具配置：

| 文件 | 作用 |
|---|---|
| `.cz.toml` | Commitizen 版本与 tag 规则 |
| `ruff.toml` | Ruff lint 与 format 规则 |
| `pyrightconfig.json` | BasedPyright 检查范围和模式 |
| `pytest.ini` | pytest 与 asyncio 默认行为 |
| `.pre-commit-config.yaml` | prek/pre-commit hooks |
| `cliff.toml` | git-cliff changelog 规则 |
| `justfile` | 常用本地开发命令 |

Coverage、Codecov 和 `pytest-cov` 不属于模板。

## 维护控制仓库

根目录是 `package = false` 的 uv 控制项目，不会构建或发布 Python 包。首次同步依赖后，可以使用与 `python-project-template` 一致的质量入口：

```console
uv sync --all-groups --locked
just test
just test-fast
just lint
just check
```

`just test` 会尝试运行全部控制层契约测试，包括非法答案、`just new` 外部命令编排、真实 Copier 版本更新、分发包许可证和生成 workflow 契约；缺少 Just 或 PowerShell 时，对应的本地集成测试会跳过。`just test-fast` 跳过会执行 Copier、Git、Just 或生成项目工具链的全部 integration 测试。它只是本地快速反馈命令，不是提交钩子。`just format` 应用 Ruff 修复和格式化，`just lock` 刷新根 `uv.lock`。

本地 uv 按仓库命令实际使用的功能执行。GitHub workflows 独立安装精确 uv 版本；Renovate 继续自动合并 uv patch 更新，并把 minor 与 major 更新留给人工审查。

根 CI 检查控制仓库，并真实渲染插件后运行 Ruff、BasedPyright 和 Python 版本矩阵。契约测试继续保护生成 CI 的触发范围，以及发布 workflow 的权限和 artifact 传递顺序；根 Renovate 维护控制依赖和模板源码中的依赖，生成项目的 active workflows 继续由各插件自己的 Renovate 维护。

生成插件发布时，`release.yml` 先在只读 job 中验证 tag、源码和 wheel/sdist，再把同一份 artifact
交给仅有 PyPI OIDC 权限和仅有 GitHub 内容写权限的独立 jobs；发布阶段不会重新 checkout 或构建。

## 发布模板版本

模板改动合并到 `main` 且 CI 通过后，在仓库根目录运行：

```console
just bump
```

根 `.cz.toml` 保存当前模板版本。该命令会先要求确认并验证当前分支是 `main`，再通过 `uvx` 临时运行 Commitizen，创建版本提交和 `vX.Y.Z` annotated tag，最后把当前 `HEAD` 与所有可达且尚未存在于远端的 annotated tags 原子推送到 `origin`。根仓库不发布 Python 包；远端 tag 就是 Copier 发现和选择的模板版本。已经公开的 tag 不应移动，发布错误应通过更高版本修复。

## 模板升级

中央模板升级流程：

1. 修改 `template/`、`copier.yml` 或生成项目的 CI 结构。
2. 本仓库 CI 先运行根控制项目的契约与质量检查，再渲染默认插件并运行 Ruff、BasedPyright 和 Python 3.11–3.14 的 pytest。
3. 合并后运行 `just bump`，发布新的 PEP 440 兼容 tag。
4. Hosted Renovate 从各插件的 `.copier-answers.yml` 发现新版本。
5. Renovate 运行 Copier update，并创建普通 PR。
6. 维护者检查配置、README 和可能的合并冲突后再合并。

模板刻意不使用 Copier tasks、migrations 或自定义 Jinja extensions。这样更新不需要执行模板脚本，适合 Hosted Renovate 的安全模型。

需要本地复现更新时，在生成插件的干净工作树中运行 `just update-template`。它使用 Copier 的默认版本选择，并自动调用 `just finish-template-update` 检查 whitespace、`.rej`、lock、hooks、Ruff、BasedPyright 和 pytest。若 Copier 因冲突中断，先解决冲突，再单独运行 `just finish-template-update`；不要重新运行更新覆盖已经完成的冲突处理。

## 文档

- [Architecture overview](docs/architecture/overview.md)
- [模板创建与升级 flow](docs/architecture/flows/template-lifecycle.md)
- [ADR-0001: 使用 Copier 与托管 Renovate](docs/adr/0001-use-copier-and-renovate.md)
- [ADR-0002: 保持 NoneBot 模板独立](docs/adr/0002-keep-the-nonebot-template-independent.md)
- [ADR-0003: 使用显式模板来源常量](docs/adr/0003-use-an-explicit-template-source-constant.md)
- [ADR-0004: 从 Git origin 推导模板来源](docs/adr/0004-derive-template-source-from-origin.md)
- [ADR-0005: 生成插件独立拥有完整 CI](docs/adr/0005-generated-plugins-own-ci.md)
- [ADR-0006: 使用 Copier 默认模板版本选择](docs/adr/0006-use-copier-default-version-selection.md)
- [ADR-0007: 使用当前 GitHub CLI 账号作为生成仓库 owner](docs/adr/0007-use-current-gh-account-as-repository-owner.md)
- [ADR-0008: 根创建入口统一使用跨平台 PowerShell](docs/adr/0008-use-cross-platform-powershell-for-creation.md)
- [ADR-0009: 根仓库与生成插件统一使用现代 Just PowerShell 配置](docs/adr/0009-align-modern-just-powershell-configuration.md)
- [ADR-0010: 创建时不采集项目简介](docs/adr/0010-defer-project-description.md)
- [ADR-0011: 根模板通过 Commitizen 发布版本](docs/adr/0011-use-root-commitizen-bump.md)
- [ADR-0012: 根仓库使用独立的 Python 控制项目](docs/adr/0012-use-a-python-controller-project.md)
- [ADR-0013: 为生成插件提供可恢复的手工模板更新入口](docs/adr/0013-provide-manual-template-update-recovery.md)
- [ADR-0014: 静态检查真实渲染后的 GitHub Actions](docs/adr/0014-statically-validate-rendered-workflows.md)
- [ADR-0015: 插件发布使用分阶段最小权限链](docs/adr/0015-stage-least-privilege-plugin-releases.md)
- [ADR-0016: Just 相关控制层测试保留为本地集成测试](docs/adr/0016-keep-just-dependent-controller-tests-local.md)
- [ADR-0017: 生成插件的所有 pull request 都运行 CI](docs/adr/0017-run-generated-ci-for-every-pull-request.md)
- [ADR-0018: 根模板与生成插件使用单步 bump 整体发布](docs/adr/0018-use-single-step-whole-bump-push.md)
- [ADR-0019: 使用可读 Action 版本并移除专用 workflow 扫描器](docs/adr/0019-use-readable-action-tags-without-dedicated-scanners.md)
- [ADR-0020: 只在 GitHub workflows 固定 uv CLI 版本](docs/adr/0020-pin-uv-only-in-github-workflows.md)
- [未完成计划概览](docs/plans/todo/README.md)
