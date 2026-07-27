<#
.SYNOPSIS
Captures an immutable, redacted baseline inventory for the top-skills-agents-review track.

.DESCRIPTION
Enumerates ONLY names, paths, sizes, timestamps, and SHA-256 hashes. It never
reads or records file bodies, tokens, secrets, or message content. Roots are
resolved with Resolve-Path -LiteralPath. Output is a deterministic sorted JSON
document. Records UTC captured_at, canonical resolved paths, Codex junction
link_path/target_path, per-root file lists/counts with SHA-256, redacted
git_status, and redaction_applied: true.

.PARAMETER RepoRoot
Repository root (C:\development\opencode).

.PARAMETER VaultRoot
Lazy vault root (C:\Users\DaveWitkin\.opencode-lazy-vault).

.PARAMETER SkillRoot
Always-on OpenCode skill root.

.PARAMETER AgentRoot
OpenCode agent root.

.PARAMETER CodexSkillRoot
Codex skills path (expected junction to vault).

.PARAMETER OutFile
Absolute output JSON path.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [Parameter(Mandatory=$true)][string]$VaultRoot,
    [Parameter(Mandatory=$true)][string]$SkillRoot,
    [Parameter(Mandatory=$true)][string]$AgentRoot,
    [Parameter(Mandatory=$true)][string]$CodexSkillRoot,
    [Parameter(Mandatory=$true)][string]$OutFile
)

$ErrorActionPreference = "Stop"

function Resolve-RootPath {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return @{ resolved = $null; exists = $false; error = "path not found" }
    }
    $rp = (Resolve-Path -LiteralPath $Path).ProviderPath
    return @{ resolved = $rp; exists = $true }
}

function Get-FileSHA256 {
    param([string]$Path)
    try {
        # Use .NET directly (Get-FileHash cmdlet is not available in all shells).
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            $stream = [System.IO.File]::OpenRead($Path)
            try {
                $bytes = $sha.ComputeHash($stream)
            } finally {
                $stream.Close()
            }
        } finally {
            $sha.Dispose()
        }
        $sb = New-Object System.Text.StringBuilder
        foreach ($b in $bytes) { $sb.Append($b.ToString("x2")) | Out-Null }
        return $sb.ToString()
    } catch {
        return $null
    }
}

function Get-CodexLinkInfo {
    param([string]$Path)
    $info = @{ link_path = $null; target_path = $null; is_junction = $false }
    if (-not (Test-Path -LiteralPath $Path)) { return $info }
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        $info.is_junction = $true
        $info.link_path = $item.FullName
        try {
            $info.target_path = $item.Target | Select-Object -First 1
        } catch {}
    } else {
        $info.link_path = $item.FullName
        $info.target_path = $item.FullName
    }
    return $info
}

# Inventory of skill/agent roots: enumerate files only (no bodies).
function New-Inventory {
    param([string]$Root, [int]$MaxDepth)
    $entries = @()
    if (-not (Test-Path -LiteralPath $Root)) {
        return @{ resolved = $null; exists = $false; file_count = 0; files = @() }
    }
    $resolved = (Resolve-Path -LiteralPath $Root).ProviderPath
    $files = @()
    try {
        if ($MaxDepth -gt 0) {
            $files = Get-ChildItem -LiteralPath $resolved -Recurse -File -Force -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notmatch '\\\.git\\' }
        } else {
            $files = Get-ChildItem -LiteralPath $resolved -File -Force -ErrorAction SilentlyContinue
        }
    } catch {
        $files = @()
    }
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($resolved.Length).TrimStart('\').Replace('\','/')
        $entries += [pscustomobject]@{
            path = $rel
            size = $f.Length
            sha256 = (Get-FileSHA256 -Path $f.FullName)
            modified_utc = $f.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
    }
    $entries = $entries | Sort-Object path
    return @{ resolved = $resolved; exists = $true; file_count = $entries.Count; files = $entries }
}

# --- Build inventory ---------------------------------------------------------
$capturedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$repo = Resolve-RootPath -Path $RepoRoot
$vault = Resolve-RootPath -Path $VaultRoot
$skill = Resolve-RootPath -Path $SkillRoot
$agent = Resolve-RootPath -Path $AgentRoot
$codex = Resolve-RootPath -Path $CodexSkillRoot
$codexInfo = Get-CodexLinkInfo -Path $CodexSkillRoot

# Skill and agent roots are inventories with hashes (names/paths/sizes/timestamps only).
$vaultInv = New-Inventory -Root $VaultRoot -MaxDepth 5
$skillInv = New-Inventory -Root $SkillRoot -MaxDepth 3
$agentInv = New-Inventory -Root $AgentRoot -MaxDepth 2

# Repo worktree top-level git status (redacted of body content).
$gitStatus = @()
try {
    $raw = & git -C $repo.resolved status --short --untracked-files=normal 2>$null
    foreach ($line in $raw) {
        if (-not [string]::IsNullOrWhiteSpace($line)) {
            # Keep only XY code + basename (no path leakage of sensitive content).
            $xy = $line.Substring(0, [Math]::Min(2,$line.Length))
            $rest = $line.Substring([Math]::Min(3,$line.Length))
            $base = Split-Path -Leaf $rest
            $gitStatus += ($xy + " " + $base)
        }
    }
} catch {
    $gitStatus = @("unavailable")
}

$baseline = [ordered]@{
    captured_at = $capturedAt
    redaction_applied = $true
    redaction_policy = "names, paths, sizes, timestamps, SHA-256 hashes only; no file bodies, tokens, or secrets; git status shows XY code + leaf basename only"
    paths = [ordered]@{
        repo_root = $repo.resolved
        vault_root = $vault.resolved
        skill_root = $skill.resolved
        agent_root = $agent.resolved
        codex_skill_root = $codex.resolved
    }
    codex_topology = [ordered]@{
        link_path = $codexInfo.link_path
        target_path = $codexInfo.target_path
        is_junction = $codexInfo.is_junction
        target_equals_vault_root = ($codexInfo.target_path -eq $vault.resolved)
    }
    inventories = [ordered]@{
        vault = [ordered]@{
            resolved = $vaultInv.resolved
            exists = $vaultInv.exists
            file_count = $vaultInv.file_count
            files = $vaultInv.files
        }
        skill = [ordered]@{
            resolved = $skillInv.resolved
            exists = $skillInv.exists
            file_count = $skillInv.file_count
            files = $skillInv.files
        }
        agent = [ordered]@{
            resolved = $agentInv.resolved
            exists = $agentInv.exists
            file_count = $agentInv.file_count
            files = $agentInv.files
        }
    }
    git_status_redacted = $gitStatus
    git_status_count = $gitStatus.Count
}

$json = $baseline | ConvertTo-Json -Depth 10 -Compress:$false
$outDir = Split-Path -Parent $OutFile
if (-not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
# Write UTF-8 without BOM (.NET default UTF8 encoding emits BOM; use the
# parameterless ctor which produces UTF-8 without BOM).
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($OutFile, $json, $utf8NoBom)
Write-Output ("BASELINE_WRITTEN=" + $OutFile)
Write-Output ("VAULT_FILES=" + $vaultInv.file_count)
Write-Output ("SKILL_FILES=" + $skillInv.file_count)
Write-Output ("AGENT_FILES=" + $agentInv.file_count)
Write-Output ("CODEX_TARGET_EQUALS_VAULT=" + ($codexInfo.target_path -eq $vault.resolved))
