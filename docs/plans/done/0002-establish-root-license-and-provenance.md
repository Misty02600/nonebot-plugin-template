# PLAN-0002：为根仓库添加 MIT 许可证

| 状态 | 完成时间 |
|---|---|
| 已完成 | 2026-08-14 |

## 问题与最终结果

根控制仓库原本没有自己的许可证，生成插件的 `template/LICENSE.jinja` 不能替代根授权。现在根仓库采用
MIT License；生成插件继续渲染自己的 MIT 许可证和作者信息。

## 关键改动

| 模块或路径 | 最终改动 |
|---|---|
| `LICENSE` | 添加标准 MIT License 文本。 |
| `pyproject.toml` | 声明 `license = "MIT"` 和 `license-files = ["LICENSE"]`。 |
| `tests/test_repository_contracts.py` | 验证根许可证文件和项目元数据。 |

## 验证结果

| 成功标准 | 证据或结果 |
|---|---|
| 根仓库明确使用 MIT | 根 `LICENSE` 与项目元数据一致。 |
| 生成项目许可证不退化 | `template/LICENSE.jinja` 和生成项目许可证契约保持不变。 |
| 控制仓库配置有效 | `uv lock --check`、许可证契约测试和 Ruff 检查通过。 |

## 相关文档

- [PLAN-0001：推出 Copier 模板升级](../todo/0001-roll-out-copier-template-updates.md)
