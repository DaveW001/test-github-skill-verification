#Requires -Version 5.1
<#
.SYNOPSIS
    Confirmed-skill smoke-test harness (structural + script checks + functional prompt).

.DESCRIPTION
    Validates an OpenCode skill directory:
      - SKILL.md existence and YAML frontmatter fences
      - frontmatter `name` matches the directory slug and the naming regex
      - frontmatter `description` exists and is under 1024 characters
      - local Markdown links ([text](target)) resolve
      - local referenced files with known extensions resolve
      - PowerShell (.ps1) syntax via PSParser::Tokenize
      - Python (.py) syntax via `ast.parse` when a Python interpreter is available
    Emits a deterministic RESULT: PASS / RESULT: FAIL summary and, when
    -PrintFunctionalPrompt is set, a FUNCTIONAL PROMPT TEMPLATE for a Task sub-agent.

    This harness makes NO external API calls and never reads, prints, or inspects
    token / credential values. Warnings do not fail the run; only explicit FAIL
    results on a file that exists (or is clearly required and missing) do.

.PARAMETER SkillPath
    Absolute path to the skill directory to validate.

.PARAMETER PrintFunctionalPrompt
    Print a FUNCTIONAL PROMPT TEMPLATE suitable for a Task sub-agent functional smoke test.

.EXAMPLE
    pwsh -NoProfile -ExecutionPolicy Bypass -File .\skill-smoke-test.ps1 `
        -SkillPath C:\skills\my-skill -PrintFunctionalPrompt
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$SkillPath,
    [switch]$PrintFunctionalPrompt
)

$ErrorActionPreference = 'Continue'

# ---- shared, script-scoped state ----
$script:Results   = @()
$script:FailCount = 0
$script:WarnCount = 0

function Add-Result {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Category,
        [Parameter(Mandatory=$true)][ValidateSet('PASS','FAIL','WARN','SKIP','INFO')][string]$Status,
        [Parameter(Mandatory=$true)][string]$Message
    )
    $script:Results += [pscustomobject]@{ Category = $Category; Status = $Status; Message = $Message }
    switch ($Status) {
        'FAIL' { $script:FailCount++ }
        'WARN' { $script:WarnCount++ }
    }
}

function Get-SkillFrontmatter {
    <#
        Returns an ordered hashtable of top-level frontmatter keys parsed from a
        SKILL.md file, or $null when the frontmatter fences are missing/malformed.
        Only the simple `key: value` form is parsed (sufficient for name/description).
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $raw = Get-Content -Raw -LiteralPath $Path
    if ([string]::IsNullOrEmpty($raw)) { return $null }
    if ($raw -notmatch '(?s)\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)') { return $null }
    $fmText = $Matches[1]
    $fm = [ordered]@{}
    foreach ($line in ($fmText -split "`r?`n")) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line -match '^\s*([A-Za-z0-9_]+)\s*:\s*(.*)$') {
            $fm[$Matches[1]] = $Matches[2].Trim().Trim('"').Trim("'")
        }
    }
    return $fm
}

function Test-SkillStructure {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$SkillPath)

    $skillMd = Join-Path $SkillPath 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillMd)) {
        Add-Result -Category 'STRUCTURE' -Status 'FAIL' -Message "SKILL.md not found at $skillMd"
        return
    }
    Add-Result -Category 'STRUCTURE' -Status 'PASS' -Message 'SKILL.md exists'

    $fm = Get-SkillFrontmatter -Path $skillMd
    if ($null -eq $fm) {
        Add-Result -Category 'STRUCTURE' -Status 'FAIL' -Message 'Frontmatter fences (--- ... ---) missing or malformed at top of SKILL.md'
        return
    }
    Add-Result -Category 'STRUCTURE' -Status 'PASS' -Message 'Frontmatter fences present'

    $dirSlug = Split-Path -Leaf $SkillPath
    if (-not $fm.Contains('name')) {
        Add-Result -Category 'STRUCTURE' -Status 'FAIL' -Message 'Frontmatter is missing the required `name` field'
    } else {
        $nameVal = [string]$fm['name']
        if ($nameVal -ceq $dirSlug) {
            Add-Result -Category 'STRUCTURE' -Status 'PASS' -Message "name ('$nameVal') matches directory slug"
        } else {
            Add-Result -Category 'STRUCTURE' -Status 'FAIL' -Message "name ('$nameVal') does not match directory slug ('$dirSlug')"
        }
        if ($nameVal -match '^[a-z0-9]+(-[a-z0-9]+)*$') {
            Add-Result -Category 'STRUCTURE' -Status 'PASS' -Message 'name matches the naming regex ^[a-z0-9]+(-[a-z0-9]+)*$'
        } else {
            Add-Result -Category 'STRUCTURE' -Status 'WARN' -Message "name ('$nameVal') does not match the recommended naming regex"
        }
    }

    if (-not $fm.Contains('description')) {
        Add-Result -Category 'STRUCTURE' -Status 'FAIL' -Message 'Frontmatter is missing the required `description` field'
    } else {
        $desc = [string]$fm['description']
        if ([string]::IsNullOrWhiteSpace($desc)) {
            Add-Result -Category 'STRUCTURE' -Status 'FAIL' -Message 'description is empty'
        } else {
            if ($desc.Length -le 1024) {
                Add-Result -Category 'STRUCTURE' -Status 'PASS' -Message "description present ($($desc.Length) chars, <= 1024)"
            } else {
                Add-Result -Category 'STRUCTURE' -Status 'FAIL' -Message "description is $($desc.Length) chars, exceeds the 1024 limit"
            }
        }
    }
}

function Test-MarkdownLinks {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$SkillPath)
    $mdFiles = @(Get-ChildItem -LiteralPath $SkillPath -Recurse -File -Filter '*.md' -ErrorAction SilentlyContinue)
    if ($mdFiles.Count -eq 0) {
        Add-Result -Category 'REFERENCES' -Status 'WARN' -Message 'No Markdown files found to scan for links'
        return
    }
    $knownExt = @('.md','.ps1','.py','.json','.jsonc','.txt','.yaml','.yml','.js','.ts','.csv','.sh','.toml','.html','.example')
    $linkRegex = [regex]'\[([^\]]+)\]\(([^)]+)\)'
    foreach ($md in $mdFiles) {
        $raw = Get-Content -Raw -LiteralPath $md.FullName
        if ([string]::IsNullOrEmpty($raw)) { continue }
        # Strip fenced code blocks so links inside code are not treated as real references
        $stripped = [regex]::Replace($raw, '(?s)```.*?```', '')
        foreach ($m in $linkRegex.Matches($stripped)) {
            $target = $m.Groups[2].Value.Trim()
            if ($target -match '^\s*(\S+)') { $target = $Matches[1] }
            if ($target -match '(?i)^[a-z][a-z0-9+.-]*://') { continue }   # http(s)://, ftp://, etc.
            if ($target -match '(?i)^mailto:') { continue }
            if ($target.StartsWith('#')) { continue }
            if ($target -eq '') { continue }
            $clean = ($target -split '#')[0]
            $clean = ($clean -split '\?')[0]
            if ([string]::IsNullOrEmpty($clean)) { continue }
            $resolved = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($md.DirectoryName, $clean))
            if (Test-Path -LiteralPath $resolved) {
                Add-Result -Category 'REFERENCES' -Status 'PASS' -Message "$($md.Name): link '$clean' resolved"
            } else {
                $ext = [System.IO.Path]::GetExtension($clean).ToLower()
                if ($knownExt -contains $ext) {
                    Add-Result -Category 'REFERENCES' -Status 'FAIL' -Message "$($md.Name): link '$clean' (known extension) not found"
                } else {
                    Add-Result -Category 'REFERENCES' -Status 'WARN' -Message "$($md.Name): link '$clean' not found (ambiguous/external; not a hard failure)"
                }
            }
        }
    }
}

function Test-ReferencedFiles {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$SkillPath)
    $mdFiles = @(Get-ChildItem -LiteralPath $SkillPath -Recurse -File -Filter '*.md' -ErrorAction SilentlyContinue)
    if ($mdFiles.Count -eq 0) { return }
    $knownExt = @('.md','.ps1','.py','.json','.jsonc','.txt','.yaml','.yml','.js','.ts','.csv','.sh','.toml','.html')
    # backtick-wrapped relative paths carrying a known extension, e.g. `reference.md`, `scripts/helper.py`
    $codeRefRegex = [regex]'`([^`]*\.[A-Za-z0-9]+)`'
    foreach ($md in $mdFiles) {
        $raw = Get-Content -Raw -LiteralPath $md.FullName
        if ([string]::IsNullOrEmpty($raw)) { continue }
        $stripped = [regex]::Replace($raw, '(?s)```.*?```', '')
        foreach ($m in $codeRefRegex.Matches($stripped)) {
            $rawPath = $m.Groups[1].Value.Trim()
            if ($rawPath -match '(?i)^[a-z][a-z0-9+.-]*://') { continue }
            if ($rawPath -match '(?i)^mailto:') { continue }
            if ($rawPath.Contains('~')) { continue }
            if ($rawPath.Contains('$')) { continue }
            if ($rawPath.StartsWith('/') -or $rawPath.StartsWith('#')) { continue }
            if ($rawPath -match '^[A-Za-z]:[\\/]') { continue }
            $clean = ($rawPath -split '#')[0]
            $clean = ($clean -split '\?')[0]
            if ([string]::IsNullOrEmpty($clean)) { continue }
            $ext = [System.IO.Path]::GetExtension($clean).ToLower()
            if (-not ($knownExt -contains $ext)) { continue }
            $resolved = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($md.DirectoryName, $clean))
            if (Test-Path -LiteralPath $resolved) {
                Add-Result -Category 'REFERENCES' -Status 'PASS' -Message "$($md.Name): referenced file '$clean' resolved"
            } else {
                Add-Result -Category 'REFERENCES' -Status 'WARN' -Message "$($md.Name): referenced file '$clean' not found (warning; verify if intentional)"
            }
        }
    }
}

function Test-ScriptSyntax {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$SkillPath)
    $ps1 = @(Get-ChildItem -LiteralPath $SkillPath -Recurse -File -Filter '*.ps1' -ErrorAction SilentlyContinue)
    $py  = @(Get-ChildItem -LiteralPath $SkillPath -Recurse -File -Filter '*.py' -ErrorAction SilentlyContinue)
    $hasScripts = $false

    foreach ($f in $ps1) {
        $hasScripts = $true
        $errors = $null
        try {
            [System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw -LiteralPath $f.FullName), [ref]$errors) | Out-Null
            if ($null -eq $errors -or $errors.Count -eq 0) {
                Add-Result -Category 'SCRIPT SYNTAX' -Status 'PASS' -Message "$($f.Name): PowerShell tokenize OK (0 parse errors)"
            } else {
                $msgs = (($errors | ForEach-Object { $_.Message }) -join '; ')
                Add-Result -Category 'SCRIPT SYNTAX' -Status 'FAIL' -Message "$($f.Name): $($errors.Count) PowerShell parse error(s): $msgs"
            }
        } catch {
            Add-Result -Category 'SCRIPT SYNTAX' -Status 'FAIL' -Message "$($f.Name): could not tokenize: $($_.Exception.Message)"
        }
    }

    $pyExe = $null
    foreach ($cmd in @('python','py')) {
        $g = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($null -ne $g -and -not [string]::IsNullOrEmpty($g.Source) -and ($g.Source -notmatch 'WindowsApps')) {
            $pyExe = $g.Source
            break
        }
    }

    # Static checker script. Using a file (not python -c) avoids native argument
    # quoting issues when the target path or code contains spaces/quotes.
    $checkerCode = @"
import ast, sys
try:
    ast.parse(open(sys.argv[1], encoding='utf-8').read())
    print('PY_SYNTAX_OK')
except SyntaxError as e:
    print('PY_SYNTAX_ERROR: ' + str(e))
    sys.exit(1)
except Exception as e:
    print('PY_ERROR: ' + str(e))
    sys.exit(2)
"@

    foreach ($f in $py) {
        $hasScripts = $true
        if ([string]::IsNullOrEmpty($pyExe)) {
            Add-Result -Category 'SCRIPT SYNTAX' -Status 'WARN' -Message "$($f.Name): no Python interpreter available; skipping ast.parse (not a failure)"
            continue
        }
        $checker  = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), ('harness-pycheck-' + [guid]::NewGuid().ToString('N') + '.py'))
        $combined = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), ('harness-py-out-' + [guid]::NewGuid().ToString('N') + '.txt'))
        try {
            Set-Content -LiteralPath $checker -Value $checkerCode -Encoding utf8
            & $pyExe $checker $f.FullName *> $combined
            if ($LASTEXITCODE -eq 0) {
                Add-Result -Category 'SCRIPT SYNTAX' -Status 'PASS' -Message "$($f.Name): Python ast.parse OK"
            } else {
                $errOut = ''
                if (Test-Path -LiteralPath $combined) { $errOut = (Get-Content -Raw -LiteralPath $combined).Trim() }
                Add-Result -Category 'SCRIPT SYNTAX' -Status 'FAIL' -Message "$($f.Name): Python parse error (exit $LASTEXITCODE): $errOut"
            }
        } catch {
            Add-Result -Category 'SCRIPT SYNTAX' -Status 'WARN' -Message "$($f.Name): Python check unavailable: $($_.Exception.Message)"
        } finally {
            if (Test-Path -LiteralPath $checker)  { Remove-Item -LiteralPath $checker  -Force -ErrorAction SilentlyContinue }
            if (Test-Path -LiteralPath $combined) { Remove-Item -LiteralPath $combined -Force -ErrorAction SilentlyContinue }
        }
    }

    if (-not $hasScripts) {
        Add-Result -Category 'SCRIPT SYNTAX' -Status 'SKIP' -Message 'No .ps1 or .py scripts included in the skill'
    }
}

function Write-FunctionalPrompt {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$SkillPath,
        [Parameter(Mandatory=$true)][string]$SkillName
    )
    $template = @"
FUNCTIONAL PROMPT TEMPLATE
==========================
You are a Task sub-agent performing an OFFLINE functional smoke test of the
OpenCode skill located at:

  $SkillPath
  (skill name: $SkillName)

Read that skill's SKILL.md and any files it references, then follow the skill's
own instructions to complete ONE representative, safe request for this skill.

STRICT RULES
- Do NOT call any real external API, webhook, or production system.
- Do NOT send any real message, email, ticket, or other side-effecting request.
- Do NOT read, print, expose, or transmit any token, key, or credential value.
- If the skill would normally perform a network action, SIMULATE it: produce the
  exact request payload or plan you would send, then STOP before transmission.
- Use ONLY the skill's own instructions; do not invent undocumented steps.

REQUIRED REPORT HEADINGS (return all four)
  ## Instructions followed
  ## Expected output produced
  ## Forbidden actions avoided
  ## Verdict
The Verdict line MUST be exactly one of:
  FUNCTIONAL_SMOKE_TEST_PASSED
  FUNCTIONAL_SMOKE_TEST_FAILED
If FAILED, state the explicit reason(s) under ## Verdict.
"@
    Write-Output ''
    Write-Output $template
}

function Write-Summary {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$SkillPath,
        [Parameter(Mandatory=$true)][string]$SkillName
    )
    Write-Output ''
    Write-Output 'SKILL SMOKE TEST SUMMARY'
    Write-Output ('SKILL: ' + $SkillName)
    Write-Output ('PATH:  ' + $SkillPath)

    foreach ($cat in @('STRUCTURE','REFERENCES','SCRIPT SYNTAX')) {
        $catResults = @($script:Results | Where-Object { $_.Category -eq $cat })
        if ($catResults.Count -eq 0) {
            Write-Output ($cat + ': NOT RUN')
            continue
        }
        $fails  = @($catResults | Where-Object { $_.Status -eq 'FAIL' }).Count
        $warns  = @($catResults | Where-Object { $_.Status -eq 'WARN' }).Count
        $passes = @($catResults | Where-Object { $_.Status -eq 'PASS' }).Count
        $skips  = @($catResults | Where-Object { $_.Status -eq 'SKIP' }).Count
        $parts = @()
        if ($passes -gt 0) { $parts += ("PASS x" + $passes) }
        if ($warns   -gt 0) { $parts += ("WARN x" + $warns) }
        if ($skips   -gt 0) { $parts += ("SKIP x" + $skips) }
        if ($fails   -gt 0) { $parts += ("FAIL x" + $fails) }
        $verdict = 'OK'
        if ($fails -gt 0) { $verdict = 'FAIL' }
        Write-Output ($cat + ': ' + $verdict + ' (' + ($parts -join ', ') + ')')
    }

    Write-Output ('WARNINGS: ' + $script:WarnCount + '   FAILURES: ' + $script:FailCount)
    if ($script:FailCount -eq 0) {
        Write-Output 'RESULT: PASS'
    } else {
        Write-Output 'RESULT: FAIL'
    }

    Write-Output ''
    Write-Output 'DETAILS'
    foreach ($r in $script:Results) {
        Write-Output ('  [' + $r.Category + '][' + $r.Status + '] ' + $r.Message)
    }
}

function Main {
    [CmdletBinding()]
    param()
    if ([string]::IsNullOrWhiteSpace($SkillPath)) {
        Write-Error 'SkillPath is required.'
        exit 2
    }
    $absPath = $SkillPath
    try { $absPath = [System.IO.Path]::GetFullPath($SkillPath) } catch { }
    if (-not (Test-Path -LiteralPath $absPath -PathType Container)) {
        Write-Output 'SKILL SMOKE TEST SUMMARY'
        Write-Output ('STRUCTURE: FAIL - skill directory not found: ' + $SkillPath)
        Write-Output 'REFERENCES: NOT RUN (skill directory missing)'
        Write-Output 'SCRIPT SYNTAX: NOT RUN (skill directory missing)'
        Write-Output 'RESULT: FAIL'
        exit 1
    }
    $skillName = Split-Path -Leaf $absPath

    Test-SkillStructure  -SkillPath $absPath
    Test-MarkdownLinks   -SkillPath $absPath
    Test-ReferencedFiles -SkillPath $absPath
    Test-ScriptSyntax    -SkillPath $absPath

    Write-Summary -SkillPath $absPath -SkillName $skillName

    if ($PrintFunctionalPrompt) {
        Write-FunctionalPrompt -SkillPath $absPath -SkillName $skillName
    }

    if ($script:FailCount -eq 0) { exit 0 } else { exit 1 }
}

Main
