# ADR-0015: 插件发布使用分阶段最小权限链

- Status: Accepted
- Date: 2026-08-11
- Partially superseded by: [ADR-0019](0019-use-readable-action-tags-without-dedicated-scanners.md)（Decision 7–8）；
  [ADR-0022](0022-validate-distributions-without-twine.md)（Decision 3 中的 Twine metadata 检查）

## Context

生成插件原先在一个 GitHub Actions job 中校验版本、生成 changelog、构建发行包、发布 PyPI 并创建
GitHub Release。该 job 同时拥有 PyPI Trusted Publishing 所需的 OIDC 权限和 GitHub 内容写权限，
源码、依赖与第三方 Action 也在这一高权限上下文中执行。workflow 只比较项目版本与 tag 文本，没有确认
annotated tag、`main` 祖先关系，也没有在实际 tag 上重跑质量检查或验证 wheel/sdist。

Python 通用模板已经采用无发布权限预检、artifact 传递与独立发布 jobs。NoneBot 模板保持独立，
但插件包的交付风险和权限边界相同，适合收敛到同一维护原则。

## Decision

1. 生成插件的 release workflow 顶层使用 `permissions: {}`。
2. `validate` job 只授予 `contents: read`，确认项目版本、annotated tag 和 `main` 祖先关系，并在精确
   tag 上运行 Ruff、BasedPyright 与 pytest。
3. `validate` 使用 `uv build --no-sources` 构建一个 wheel 和一个 sdist，再以固定版本 Twine 检查元数据，
   验证 wheel 完整性以及 sdist 路径安全。
4. changelog 与发行包组成同一份 reviewed artifact。后续 jobs 只下载该 artifact，不重新 checkout、
   安装项目依赖或构建。
5. `publish-pypi` 只授予 `id-token: write`，通过 PyPI Trusted Publishing 发布 reviewed artifact。
6. `github-release` 等待 PyPI 成功，只授予 `contents: write`，使用同一 artifact 创建 GitHub Release。
7. 所有 GitHub Actions 固定到完整 commit SHA；模板根 Renovate 维护 seed 版本，生成插件 Renovate
   对 active workflow 保持 `pinDigests: true`。
8. 根 actionlint 与 zizmor 继续静态检查真实渲染 workflow；结构契约测试保护权限、校验和 artifact
   顺序。

## Consequences

- 读取和执行项目源码时不再同时持有 PyPI OIDC 与 GitHub 内容写权限。
- 被发布到 PyPI 和 GitHub Release 的文件与无发布权限阶段验证的文件完全相同。
- 轻量 tag、版本不匹配 tag 或不属于 `main` 历史的 tag 会在取得发布权限前失败。
- 正式发布会在 tag 上重复质量检查和构建；耗时增加，但检查对象与最终发行包一致。
- PyPI 发布成功后 GitHub Release 才创建；若最后一步失败，可以针对同一 tag 重跑 workflow。

## Links

- [Architecture overview](../architecture/overview.md)
- [模板创建、发布与升级](../architecture/flows/template-lifecycle.md)
- [ADR-0001: 使用 Copier 与托管 Renovate](0001-use-copier-and-renovate.md)
- [ADR-0005: 生成插件独立拥有完整 CI](0005-generated-plugins-own-ci.md)
- [ADR-0014: 静态检查真实渲染后的 GitHub Actions](0014-statically-validate-rendered-workflows.md)
- [ADR-0022: 不使用 Twine 重复检查发行包元数据](0022-validate-distributions-without-twine.md)
