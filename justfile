set windows-shell := ["powershell", "-NoProfile", "-Command"]

# 默认任务列表
default:
    @just --list

# 运行测试
test:
    uv run pytest --cov=src --cov-report xml --junitxml=./junit.xml -n auto

# 版本发布（更新版本号、生成 changelog、更新 lock 文件）
bump:
    uv run cz bump
    uv lock

# 生成 changelog
changelog:
    uv run git-cliff --latest

# 安装 pre-commit hooks
hooks:
    uv run prek install

# 代码检查与格式化
lint:
    uv run ruff check . --fix
    uv run ruff format .

# 类型检查
check:
    uv run basedpyright

# 更新 pre-commit hooks
update:
    uv run prek auto-update

# 创建用于向上游提交 PR 的临时分支
# 用法: just pr <分支名> <提交信息>
# 示例: just pr my-feature "feat: add new feature"
pr branch msg:
    git fetch upstream
    git switch -c pr/{{branch}} upstream/main
    git restore --source dev --staged --worktree -- . ':(exclude)tools/' ':(exclude)dev_tools/'
    git commit -m "{{msg}}"
