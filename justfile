set minimum-version := "1.56.0"

[windows]
set shell := ["pwsh", "-NoProfile", "-Command"]

set default-list
set export
set lazy

uv := require("uv")

# 在 main 上创建模板版本提交和 annotated tag，并整体原子推送到 origin
[group("release")]
bump:
    {{ if shell("git branch --show-current") == "main" { "" } else { error("bump 只能在 main 分支执行") } }}uvx --from 'commitizen>=4.16,<5' cz bump --yes
    git push --atomic --follow-tags origin HEAD

# 从模板仓库默认版本创建并发布插件仓库
[script("pwsh", "-NoProfile", "-File")]
new name visibility="public":
    $ErrorActionPreference = "Stop"

    function ConvertTo-PublicGitHubTemplateSource([string] $RemoteUrl) {
        $candidate = $RemoteUrl.Trim()
        $owner = $null
        $repository = $null

        if ($candidate -match '(?i)^https://github\.com/(?<Owner>[^/]+)/(?<Repository>[^/]+)/?$') {
            $owner = $Matches.Owner
            $repository = $Matches.Repository
        }
        elseif ($candidate -match '(?i)^git@github\.com:(?<Owner>[^/]+)/(?<Repository>[^/]+)$') {
            $owner = $Matches.Owner
            $repository = $Matches.Repository
        }
        elseif ($candidate -match '(?i)^ssh://git@github\.com/(?<Owner>[^/]+)/(?<Repository>[^/]+)$') {
            $owner = $Matches.Owner
            $repository = $Matches.Repository
        }
        else {
            throw "无法确定可公开更新的模板来源：origin 必须是 github.com 的 HTTPS 或 SSH 仓库地址；当前值：$candidate"
        }

        if ($repository.EndsWith(".git", [StringComparison]::OrdinalIgnoreCase)) {
            $repository = $repository.Substring(0, $repository.Length - 4)
        }
        if ($owner -notmatch '^(?=.{1,39}$)[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$' -or $repository -notmatch '^[A-Za-z0-9._-]+$') {
            throw "无法确定可公开更新的模板来源：origin 中的 GitHub owner 或仓库名无效；当前值：$candidate"
        }

        return "https://github.com/$owner/$repository.git"
    }

    foreach ($command in @("git", "uvx", "gh")) {
        if ($null -eq (Get-Command $command -ErrorAction SilentlyContinue)) {
            throw "just new 需要 $command，请安装并确保该命令位于 PATH 中。"
        }
    }

    $templateRoot = [System.IO.Path]::GetFullPath("{{ justfile_directory() }}")
    $repositoryRoot = [string](& git -C $templateRoot rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repositoryRoot)) {
        throw "无法确定模板来源：justfile 所在目录不是 Git 仓库。请在模板仓库中运行 just new。"
    }
    if (-not [System.IO.Path]::GetFullPath($repositoryRoot.Trim()).Equals($templateRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "无法确定模板来源：justfile 必须位于模板 Git 仓库根目录。"
    }

    $origin = [string](& git -C $templateRoot remote get-url origin 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($origin)) {
        throw "无法确定模板来源：当前模板仓库没有 origin 远端。请先配置持久的 GitHub origin。"
    }
    $templateSource = ConvertTo-PublicGitHubTemplateSource $origin

    $env:GIT_TERMINAL_PROMPT = "0"
    & git ls-remote $templateSource HEAD 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "无法访问模板远端：$templateSource。请确认仓库已推送且可以通过公开 HTTPS 读取。"
    }

    $repoOwner = [string](& gh api user --jq ".login" 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoOwner)) {
        throw "无法读取当前 GitHub CLI 登录账号。请先运行 gh auth login。"
    }
    $repoOwner = $repoOwner.Trim()

    $target = Join-Path (Split-Path -Parent $templateRoot) $env:name
    if (Test-Path -LiteralPath $target) {
        throw "目标目录已存在：$target"
    }

    & uvx --from "copier>=9.17,<10" copier copy --defaults --data ("repo_owner=" + $repoOwner) --data ("repo_name=" + $env:name) $templateSource $target
    if ($LASTEXITCODE -ne 0) { throw "Copier 生成失败：$templateSource" }
    & git -C $target init -b main
    if ($LASTEXITCODE -ne 0) { throw "无法初始化生成仓库：$target" }
    & git -C $target add .
    if ($LASTEXITCODE -ne 0) { throw "无法暂存生成文件：$target" }
    & git -C $target commit -m "chore: initialize repository"
    if ($LASTEXITCODE -ne 0) { throw "无法创建初始提交：$target" }
    & gh repo create ("$repoOwner/$($env:name)") ("--" + $env:visibility) --source $target --remote origin --push
    if ($LASTEXITCODE -ne 0) { throw "无法创建或推送 GitHub 仓库；本地生成目录保留在：$target" }

# 运行模板控制仓库的全部契约测试
[group("quality")]
test:
    {{ assert(uv != "") }}uv run pytest

# 跳过会执行 Copier、Git、Just 或生成项目工具链的集成测试
[group("quality")]
test-fast:
    {{ assert(uv != "") }}uv run pytest -m "not integration"

# 检查控制仓库的 Ruff lint 和格式
[group("quality")]
lint:
    {{ assert(uv != "") }}uv run ruff check .
    uv run ruff format --check .

# 应用 Ruff 可修复规则并格式化控制仓库
[group("quality")]
format:
    {{ assert(uv != "") }}uv run ruff check --fix .
    uv run ruff format .

# 运行控制仓库的 BasedPyright 类型检查
[group("quality")]
check:
    {{ assert(uv != "") }}uv run basedpyright

# 刷新模板控制仓库的 uv lock
[group("maintenance")]
lock:
    {{ assert(uv != "") }}uv lock
