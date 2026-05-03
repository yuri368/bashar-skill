param(
    [Parameter(Mandatory = $true)]
    [string]$Message,

    [string]$Version,

    [string]$Remote = "origin",

    [string]$Branch,

    [switch]$SkipIndex,

    [switch]$SkipUtf8Check,

    [switch]$SkipSearchSmoke,

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Run {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [string[]]$Arguments = @()
    )

    $display = @($Command) + $Arguments
    Write-Host ">> $($display -join ' ')"

    if ($DryRun) {
        return
    }

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $($display -join ' ')"
    }
}

function GitOutput {
    param([string[]]$Arguments)
    $output = & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed"
    }
    return $output
}

function RequireCleanConflictState {
    $unmerged = GitOutput @("diff", "--name-only", "--diff-filter=U")
    if ($unmerged) {
        throw "Unresolved merge conflicts exist. Resolve them before publishing:`n$($unmerged -join "`n")"
    }
}

function UpdateVersionFiles {
    param([string]$RequestedVersion)

    if (-not $RequestedVersion) {
        return $null
    }

    $plainVersion = $RequestedVersion.Trim()
    if ($plainVersion.StartsWith("v")) {
        $plainVersion = $plainVersion.Substring(1)
    }

    if ($plainVersion -notmatch "^\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$") {
        throw "Version must look like 0.2.1 or v0.2.1. Got: $RequestedVersion"
    }

    $tagName = "v$plainVersion"

    if (-not $DryRun) {
        $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::WriteAllText((Join-Path (Get-Location) "VERSION"), $plainVersion, $utf8NoBom)

        if (Test-Path -LiteralPath "README.md") {
            $readme = Get-Content -LiteralPath "README.md" -Raw
            $updated = $readme -replace '当前版本：`v[^`]+`', "当前版本：``$tagName``"
            if ($updated -ne $readme) {
                [System.IO.File]::WriteAllText((Join-Path (Get-Location) "README.md"), $updated, $utf8NoBom)
            }
        }
    }

    Write-Host "Version target: $tagName"
    return $tagName
}

function TestUtf8Sources {
    $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $total = 0
    $bad = New-Object System.Collections.Generic.List[string]

    Get-ChildItem -LiteralPath ".\sources" -Recurse -File |
        Where-Object { $_.Extension -in @(".txt", ".md") } |
        Where-Object { $_.FullName -notmatch "\\sources\\_(indexes|meta)\\" } |
        ForEach-Object {
            $total++
            try {
                [void]$utf8.GetString([System.IO.File]::ReadAllBytes($_.FullName))
            }
            catch {
                $bad.Add($_.FullName)
            }
        }

    if ($bad.Count -gt 0) {
        $sample = $bad | Select-Object -First 10
        throw "UTF-8 check failed: $($bad.Count) / $total source files are invalid.`n$($sample -join "`n")"
    }

    Write-Host "UTF-8 check passed: $total source files."
}

function EnsureRemoteIsSafe {
    param(
        [string]$RemoteName,
        [string]$BranchName
    )

    Run "git" @("fetch", $RemoteName)

    $local = GitOutput @("rev-parse", "HEAD")
    $remoteRef = "$RemoteName/$BranchName"
    $remoteCommit = GitOutput @("rev-parse", "--verify", $remoteRef)
    $mergeBase = GitOutput @("merge-base", "HEAD", $remoteRef)

    if ($local -eq $remoteCommit) {
        Write-Host "Remote is aligned with local HEAD."
        return
    }

    if ($mergeBase -eq $remoteCommit) {
        Write-Host "Local branch is ahead of $remoteRef."
        return
    }

    if ($mergeBase -eq $local) {
        throw "Remote branch $remoteRef has new commits. Pull/rebase before publishing."
    }

    throw "Local and remote branches have diverged. Resolve before publishing."
}

$repoRoot = GitOutput @("rev-parse", "--show-toplevel")
Set-Location $repoRoot

if (-not $Branch) {
    $Branch = (GitOutput @("branch", "--show-current")).Trim()
}

if (-not $Branch) {
    throw "Cannot determine current branch. Pass -Branch explicitly."
}

RequireCleanConflictState
EnsureRemoteIsSafe -RemoteName $Remote -BranchName $Branch

$tagName = UpdateVersionFiles -RequestedVersion $Version

if (-not $SkipIndex) {
    Run "python" @("scripts/build_search_index.py")
}

if (-not $SkipUtf8Check) {
    if ($DryRun) {
        Write-Host ">> UTF-8 source check"
    }
    else {
        TestUtf8Sources
    }
}

if (-not $SkipSearchSmoke) {
    Run "python" @("scripts/search_sources.py", "Bashar", "--limit", "1")
}

Run "git" @("add", "-A")

$staged = GitOutput @("diff", "--cached", "--name-only")
if ($staged) {
    $status = GitOutput @("status", "--short")
    Write-Host "Files staged for publish:"
    $status | Select-Object -First 80 | ForEach-Object { Write-Host $_ }
    if ($status.Count -gt 80) {
        Write-Host "... ($($status.Count - 80) more)"
    }

    $commitBody = @"
Automated publish from scripts/publish_to_github.ps1.

Constraint: Publish must verify index, source encoding, and remote branch state before pushing
Confidence: medium
Scope-risk: moderate
Directive: Keep this script conservative; do not push when remote history has moved unexpectedly
Tested: build_search_index.py
Tested: strict UTF-8 source scan
Tested: search_sources.py Bashar --limit 1
"@

    Run "git" @("commit", "-m", $Message, "-m", $commitBody)
}
else {
    Write-Host "No staged changes to commit."
}

if ($tagName) {
    $existingTag = GitOutput @("tag", "--list", $tagName)
    if ($existingTag) {
        Write-Host "Tag already exists locally: $tagName"
    }
    else {
        Run "git" @("tag", "-a", $tagName, "-m", "Bashar 资料库 $tagName 发布")
    }
}

Run "git" @("push", $Remote, $Branch)

if ($tagName) {
    Run "git" @("push", $Remote, $tagName)
}

Write-Host "Publish complete."
