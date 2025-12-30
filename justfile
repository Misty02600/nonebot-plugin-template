set windows-shell := ["powershell", "-NoProfile", "-Command"]

# 默认任务列表
default:
    @just --list

# 运行测试
test:
    uv run pytest --cov=src --cov-report xml --junitxml=./junit.xml -n auto

# 版本发布（更新版本号、生成 changelog、更新 lock 文件）
bump:
    uv run cz bump --changelog
    uv lock

# 生成 changelog
changelog:
    uv run cz changelog

# 安装 pre-commit hooks
hooks:
    uv run prek install
