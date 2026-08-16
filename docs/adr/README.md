# 架构决策

## 当前有效

- [ADR-0001：使用 Copier 与托管 Renovate](0001-use-copier-and-renovate.md)
- [ADR-0002：保持 NoneBot 模板独立](0002-keep-the-nonebot-template-independent.md)
- [ADR-0004：从 Git origin 推导模板来源](0004-derive-template-source-from-origin.md)
- [ADR-0005：生成插件独立拥有完整 CI](0005-generated-plugins-own-ci.md)
- [ADR-0006：使用 Copier 默认模板版本选择](0006-use-copier-default-version-selection.md)
- [ADR-0007：使用当前 GitHub CLI 账号作为生成仓库 owner](0007-use-current-gh-account-as-repository-owner.md)
- [ADR-0008：根创建入口统一使用跨平台 PowerShell](0008-use-cross-platform-powershell-for-creation.md)
- [ADR-0009：根仓库与生成插件统一使用现代 Just PowerShell 配置](0009-align-modern-just-powershell-configuration.md)
- [ADR-0010：创建时不采集项目简介](0010-defer-project-description.md)
- [ADR-0011：根模板通过 Commitizen 发布版本](0011-use-root-commitizen-bump.md)
- [ADR-0012：根仓库使用独立的 Python 控制项目](0012-use-a-python-controller-project.md)
- [ADR-0013：为生成插件提供可恢复的手工模板更新入口](0013-provide-manual-template-update-recovery.md)
- [ADR-0015：插件发布使用分阶段最小权限链](0015-stage-least-privilege-plugin-releases.md)
- [ADR-0016：Just 相关控制层测试保留为本地集成测试](0016-keep-just-dependent-controller-tests-local.md)
- [ADR-0017：生成插件的所有 pull request 都运行 CI](0017-run-generated-ci-for-every-pull-request.md)
- [ADR-0018：根模板与生成插件使用单步 bump 整体发布](0018-use-single-step-whole-bump-push.md)
- [ADR-0019：使用可读 Action 版本并移除专用 workflow 扫描器](0019-use-readable-action-tags-without-dedicated-scanners.md)
- [ADR-0020：只在 GitHub workflows 固定 uv CLI 版本](0020-pin-uv-only-in-github-workflows.md)
- [ADR-0021：分别维护 workflow 模板 seed 与 active 副本](0021-maintain-workflow-seeds-and-active-copies-separately.md)
- [ADR-0022：不使用 Twine 重复检查发行包元数据](0022-validate-distributions-without-twine.md)

## 已替代

- [ADR-0003：使用显式模板来源常量](0003-use-an-explicit-template-source-constant.md)
- [ADR-0014：静态检查真实渲染后的 GitHub Actions](0014-statically-validate-rendered-workflows.md)
