[CmdletBinding()]
param(
    [ValidateSet('SelfTest','InstructionWiring','AgentFrontmatter','SkillReferences','StandardsOwnership','EnvReference','ProjectAdapters','ConductorState','All')]
    [string]$Mode = 'All',
    [string]$ReportPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$configRoot = 'C:\Users\DaveWitkin\.config\opencode'
$codexRoot = 'C:\Users\DaveWitkin\.codex'
$lazyVault = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
$opencodeRepo = 'C:\development\opencode'
$trackRoot = Join-Path $opencodeRepo '.conductor\tracks\20260731-agents-md-cross-harness-remediation'
$results = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][bool]$Passed,
        [Parameter(Mandatory)][string]$Details
    )
    $results.Add([ordered]@{ name = $Name; pass = $Passed; details = $Details })
}

function Read-Text {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return [System.IO.File]::ReadAllText($Path)
}

function Resolve-ReferencePath {
    param(
        [Parameter(Mandatory)][string]$Reference,
        [Parameter(Mandatory)][string]$BaseDirectory
    )
    if ($Reference.StartsWith('~/')) {
        return (Join-Path $env:USERPROFILE ($Reference.Substring(2) -replace '/', '\'))
    }
    if ([System.IO.Path]::IsPathRooted($Reference)) { return $Reference }
    return (Join-Path $BaseDirectory ($Reference -replace '/', '\'))
}

function Test-FrontmatterText {
    param([Parameter(Mandatory)][string]$Text)
    $hasDescription = $Text -match '(?m)^description:\s*\S+'
    $hasMode = $Text -match '(?m)^mode:\s*(primary|subagent|all)\s*$'
    $hasPermission = $Text -match '(?m)^permission:\s*$'
    $hasEdit = $Text -match '(?m)^\s+edit:\s*(allow|ask|deny)'
    $hasBash = $Text -match '(?m)^\s+bash:\s*(allow|ask|deny)'
    $hasTask = $Text -match '(?m)^\s+task:\s*(allow|ask|deny|\s*$)'
    $legacyTools = $Text -match '(?m)^\s*tools:\s*$' -or $Text -match '(?m)^\s+(write|edit|bash):\s*(true|false)\s*(#.*)?$'
    $pluralPermissions = $Text -match '(?m)^\s*permissions:\s*$'
    $writePermission = $Text -match '(?m)^\s+write:\s*(allow|ask|deny)\s*(#.*)?$'
    [ordered]@{
        pass = ($hasDescription -and $hasMode -and $hasPermission -and $hasEdit -and $hasBash -and $hasTask -and -not $legacyTools -and -not $pluralPermissions -and -not $writePermission)
        description = $hasDescription
        mode = $hasMode
        permission = $hasPermission
        edit = $hasEdit
        bash = $hasBash
        task = $hasTask
        legacyTools = $legacyTools
        pluralPermissions = $pluralPermissions
        writePermission = $writePermission
    }
}

function Test-SelfTest {
    $clean = @'
---
description: Review a bounded document
mode: subagent
permission:
  edit: deny
  bash: allow
  task:
    "*": deny
---
'@
    $badTools = @'
---
description: Legacy agent
mode: subagent
tools:
  write: false
permission:
  edit: deny
  bash: allow
  task: deny
---
'@
    $badPlural = @'
---
description: Plural agent
mode: subagent
permissions:
  edit: deny
  bash: allow
  task: deny
---
'@
    $cleanResult = Test-FrontmatterText -Text $clean
    $toolsResult = Test-FrontmatterText -Text $badTools
    $pluralResult = Test-FrontmatterText -Text $badPlural
    Add-Check -Name 'SelfTest.clean-frontmatter' -Passed ([bool]$cleanResult.pass) -Details 'clean fixture accepted'
    Add-Check -Name 'SelfTest.legacy-tools-rejected' -Passed (-not [bool]$toolsResult.pass) -Details 'legacy capability fixture rejected'
    Add-Check -Name 'SelfTest.plural-permissions-rejected' -Passed (-not [bool]$pluralResult.pass) -Details 'plural permission fixture rejected'
}

function Test-InstructionWiring {
    $configPath = Join-Path $configRoot 'opencode.jsonc'
    $config = Read-Text -Path $configPath
    $corePath = Join-Path $configRoot 'agent-rules\common-core.md'
    $modulePaths = @(
        'authority-boundaries.md','filesystem-and-git.md','research-and-evidence.md',
        'agent-authoring.md','reference-index.md','RULES-MANIFEST.md'
    ) | ForEach-Object { Join-Path $configRoot ('agent-rules\' + $_) }
    $exact = if ($null -ne $config) { ([regex]::Matches($config, '(?m)"instructions"\s*:\s*\[\s*"agent-rules/common-core\.md"\s*\]')).Count } else { 0 }
    $specialized = if ($null -ne $config) { ([regex]::Matches($config, '(?i)agent-rules/(?!common-core\.md)[^"\s]+')).Count } else { 0 }
    $coreExists = Test-Path -LiteralPath $corePath -PathType Leaf
    $modulesExist = (@($modulePaths | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) }).Count -eq 0)
    Add-Check -Name 'InstructionWiring.single-shared-core' -Passed ($exact -eq 1 -and $coreExists -and $modulesExist -and $specialized -eq 0) -Details ("exact=$exact; specialized=$specialized; coreExists=$coreExists; modulesExist=$modulesExist")
}

function Test-AgentFrontmatter {
    $templatePath = Join-Path $lazyVault 'agent-writer\references\agent-templates.md'
    $text = Read-Text -Path $templatePath
    $sections = if ($null -ne $text) { [regex]::Matches($text, '(?ms)^## .*?\n.*?(?=^## |\z)') } else { @() }
    $sectionCount = @($sections).Count
    $validCount = 0
    foreach ($section in $sections) {
        if ((Test-FrontmatterText -Text $section.Value).pass) { $validCount++ }
    }
    $noLegacy = $null -ne $text -and $text -notmatch '(?m)^\s*tools:\s*$' -and $text -notmatch '(?m)^\s*(write|edit|bash):\s*(true|false)\s*(#.*)?$'
    $noPlural = $null -ne $text -and $text -notmatch '(?m)^\s*permissions:\s*$'
    $noWritePermission = $null -ne $text -and $text -notmatch '(?m)^\s+write:\s*(allow|ask|deny)\s*(#.*)?$'
    $skillsExist = @('perplexity-search','notebooklm-cli','content-trend-researcher') | ForEach-Object { Test-Path -LiteralPath (Join-Path $lazyVault $_) -PathType Container } | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count
    Add-Check -Name 'AgentFrontmatter.templates' -Passed ($sectionCount -eq 3 -and $validCount -eq 3 -and $noLegacy -and $noPlural -and $noWritePermission -and $skillsExist -eq 0) -Details ("sections=$sectionCount; valid=$validCount; legacy=$(-not $noLegacy); plural=$(-not $noPlural); writePermission=$(-not $noWritePermission); missingSkills=$skillsExist")
}

function Test-SkillReferences {
    $skillRoot = Join-Path $lazyVault 'agent-writer'
    $skillPath = Join-Path $skillRoot 'SKILL.md'
    $text = Read-Text -Path $skillPath
    $references = @(
        (Join-Path $skillRoot 'references\agent-templates.md'),
        (Join-Path $skillRoot 'references\validation.md'),
        (Join-Path $configRoot 'AGENTS.md'),
        (Join-Path $configRoot 'agent-rules\agent-authoring.md'),
        (Join-Path $configRoot 'agent-development-standards.md'),
        (Join-Path $configRoot 'command-development-standards.md'),
        (Join-Path $configRoot 'opencode-standards-reference.md')
    )
    $missing = @($references | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) }).Count
    $retired = $null -ne $text -and $text -match '(?i)skill-guidelines[\\/]'
    Add-Check -Name 'SkillReferences.agent-writer' -Passed ($null -ne $text -and $missing -eq 0 -and -not $retired) -Details ("references=$($references.Count); missing=$missing; retiredPath=$retired")
}

function Test-StandardsOwnership {
    $paths = @(
        (Join-Path $configRoot 'agent-development-standards.md'),
        (Join-Path $configRoot 'command-development-standards.md'),
        (Join-Path $configRoot 'opencode-standards-reference.md'),
        (Join-Path $configRoot 'agent-rules\agent-authoring.md'),
        (Join-Path $lazyVault 'agent-writer\references\agent-templates.md')
    )
    $texts = @($paths | ForEach-Object { Read-Text -Path $_ })
    $legacyMaps = @($texts | Where-Object { $_ -match '(?m)^\s*tools:\s*$' }).Count
    $pluralMaps = @($texts | Where-Object { $_ -match '(?m)^\s*permissions:\s*$' }).Count
    $writeKeys = @($texts | Where-Object { $_ -match '(?m)^\s+write:\s*(allow|ask|deny)\s*(#.*)?$' }).Count
    $staleSkill = @($texts | Where-Object { $_ -match '(?i)(?<![-\w])notebooklm(?![-\w])' }).Count
    $owners = ($texts[0] -match 'Canonical permission syntax') -and ($texts[1] -match 'Command Structure') -and ($texts[2] -match 'Canonical owners') -and ($texts[3] -match 'singular OpenCode frontmatter')
    Add-Check -Name 'StandardsOwnership.single-owners' -Passed ($legacyMaps -eq 0 -and $pluralMaps -eq 0 -and $writeKeys -eq 0 -and $staleSkill -eq 0 -and $owners) -Details ("legacyMaps=$legacyMaps; pluralMaps=$pluralMaps; writeKeys=$writeKeys; staleSkillNames=$staleSkill; owners=$owners")
}

function Test-EnvReference {
    $configPath = Join-Path $configRoot 'opencode.jsonc'
    $envPath = Join-Path $configRoot '.env'
    $manifestPath = Join-Path $trackRoot 'backup-manifest.json'
    $config = Read-Text -Path $configPath
    $env = Read-Text -Path $envPath
    $refCount = if ($null -ne $config) { ([regex]::Matches($config, '(?m)"SLACK_MCP_XOXP_TOKEN"\s*:\s*"\{env:SLACK_USER_TOKEN\}"')).Count } else { 0 }
    $literalCount = if ($null -ne $config) { ([regex]::Matches($config, '(?m)"SLACK_MCP_XOXP_TOKEN"\s*:\s*"(?!\{env:)[^"]+"')).Count } else { 0 }
    $envName = $null -ne $env -and $env -match '(?m)^\s*SLACK_USER_TOKEN\s*='
    $comments = $null -ne $env -and $env -match '(?m)^\s*#'
    $hashUnchanged = $false
    if ($null -ne $env -and (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        $entry = @($manifest.entries | Where-Object id -eq 'M04') | Select-Object -First 1
        if ($null -ne $entry -and $entry.preSha256) {
            $hash = (Get-FileHash -LiteralPath $envPath -Algorithm SHA256).Hash.ToLowerInvariant()
            $hashUnchanged = $hash -eq $entry.preSha256.ToLowerInvariant()
        }
    }
    Add-Check -Name 'EnvReference.central-source' -Passed ($refCount -eq 1 -and $literalCount -eq 0 -and $envName -and $comments -and $hashUnchanged) -Details ("envRef=$refCount; inlineScalar=$literalCount; variableNamePresent=$envName; commentsPresent=$comments; envHashUnchanged=$hashUnchanged")
}

function Test-ProjectAdapters {
    $projects = [ordered]@{
        'chief-of-staff' = @{ path = 'C:\development\chief-of-staff\AGENTS.md'; markers = @('OUTLOOK_CALENDAR_REMOVAL_PLAYBOOK','agent-rules') }
        '02-Kx-to-process' = @{ path = 'C:\development\02-Kx-to-process\AGENTS.md'; markers = @('knowledge-base','Conductor','agent-rules') }
        'command-center' = @{ path = 'C:\development\command-center\AGENTS.md'; markers = @('Next.js','pnpm','agent-rules') }
        'marketing' = @{ path = 'C:\development\marketing\AGENTS.md'; markers = @('.gemini/GEMINI.md','agent-rules') }
    }
    $missing = [System.Collections.Generic.List[string]]::new()
    foreach ($name in $projects.Keys) {
        $item = $projects[$name]
        $text = Read-Text -Path $item.path
        if ($null -eq $text) { $missing.Add("${name}:file") ; continue }
        foreach ($marker in $item.markers) { if ($text -notmatch [regex]::Escape($marker)) { $missing.Add("${name}:$marker") } }
    }
    Add-Check -Name 'ProjectAdapters.local-constraints' -Passed ($missing.Count -eq 0) -Details ("projects=$($projects.Count); missingMarkers=$($missing.Count)")
}

function Test-ConductorState {
    $planPath = Join-Path $trackRoot 'plan.md'
    $metadataPath = Join-Path $trackRoot 'metadata.json'
    $tracksPath = Join-Path $opencodeRepo '.conductor\tracks.md'
    $ledgerPath = Join-Path $opencodeRepo '.conductor\tracks-ledger.md'
    $plan = Read-Text -Path $planPath
    $metadata = if (Test-Path -LiteralPath $metadataPath -PathType Leaf) { Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json } else { $null }
    $tracks = Read-Text -Path $tracksPath
    $ledger = Read-Text -Path $ledgerPath
    $taskLines = if ($null -ne $plan) { @($plan -split "`r?`n" | Where-Object { $_ -match '^\d+\. - \[[x ]\] ' }) } else { @() }
    $completed = @($taskLines | Where-Object { $_ -match '^\d+\. - \[x\] ' }).Count
    $planComplete = ($taskLines.Count -eq 15 -and $completed -eq 15)
    $metadataComplete = ($null -ne $metadata -and $metadata.status -eq 'complete' -and $metadata.progress.totalTasks -eq 15 -and $metadata.progress.completedTasks -eq 15 -and [double]$metadata.progress.percentage -eq 100.0)
    $ledgersComplete = ($null -ne $tracks -and $tracks -match '20260731-agents-md-cross-harness-remediation.*\| complete \|.*15/15' -and $null -ne $ledger -and $ledger -match '20260731-agents-md-cross-harness-remediation.*complete.*15/15')
    Add-Check -Name 'ConductorState.15-of-15' -Passed ($planComplete -and $metadataComplete -and $ledgersComplete) -Details ("planTasks=$($taskLines.Count); planCompleted=$completed; metadataComplete=$metadataComplete; ledgersComplete=$ledgersComplete")
}

switch ($Mode) {
    'SelfTest' { Test-SelfTest }
    'InstructionWiring' { Test-InstructionWiring }
    'AgentFrontmatter' { Test-AgentFrontmatter }
    'SkillReferences' { Test-SkillReferences }
    'StandardsOwnership' { Test-StandardsOwnership }
    'EnvReference' { Test-EnvReference }
    'ProjectAdapters' { Test-ProjectAdapters }
    'ConductorState' { Test-ConductorState }
    'All' {
        Test-SelfTest
        Test-InstructionWiring
        Test-AgentFrontmatter
        Test-SkillReferences
        Test-StandardsOwnership
        Test-EnvReference
        Test-ProjectAdapters
        Test-ConductorState
    }
}

$failed = @($results | Where-Object { -not $_.pass })
$report = [ordered]@{
    mode = $Mode
    generated = [DateTime]::UtcNow.ToString('o')
    pass = ($failed.Count -eq 0)
    checkCount = $results.Count
    failureCount = $failed.Count
    checks = @($results)
}

if ($ReportPath) {
    $parent = Split-Path -Parent $ReportPath
    if ($parent) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    [System.IO.File]::WriteAllText($ReportPath, ($report | ConvertTo-Json -Depth 8), [System.Text.UTF8Encoding]::new($false))
}

$report | ConvertTo-Json -Depth 8
if ($failed.Count -gt 0) { exit 1 }
exit 0
