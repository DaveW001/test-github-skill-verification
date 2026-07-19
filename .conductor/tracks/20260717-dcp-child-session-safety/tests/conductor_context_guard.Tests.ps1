# RED TEST: Task 1.5 - Conductor pre-140K guardrail tests
# These tests verify that Conductor skill files and agent files contain
# the required DCP guardrail sections. They MUST FAIL because the guardrail
# sections have not been added yet.

param(
    [ValidateSet("RedGate", "ValidateSkill", "ValidateAgents")]
    [string]$Mode = "RedGate"
)

$ErrorActionPreference = "Stop"
$trackRoot = "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety"
$skillRoot = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline"
$agentRoot = "C:\Users\DaveWitkin\.config\opencode\agent"

# Required literal strings in guardrail sections
$requiredStrings = @(
    "~135K",           # Sample/handoff trigger
    "~140K",           # Hard stop
    "40 tool calls or 30K",  # Per-phase cap
    "DCP-unprotected"  # Status label (skill files only)
)

$requiredAgentStrings = @(
    "~135K",           # Handoff trigger
    "~140K",           # Hard stop
    "40 tool calls or 30K",  # Per-phase cap
    "Return promptly"  # One-line instruction
)

# Files that must have the guardrail section
$skillFiles = @(
    "$skillRoot\SKILL.md",
    "$skillRoot\references\stage-prompts.md",
    "$skillRoot\references\threshold-policy.md"
)

# Agent files that must have the bounded-stage section (excludes orchestrator)
$agentFiles = @(
    "$agentRoot\conductor-plan-creator.md",
    "$agentRoot\conductor-plan-reviewer.md",
    "$agentRoot\conductor-plan-reviewer-alt.md",
    "$agentRoot\conductor-test-writer.md",
    "$agentRoot\conductor-test-runner.md",
    "$agentRoot\conductor-track-executor.md",
    "$agentRoot\conductor-track-executor-glm51.md",
    "$agentRoot\conductor-track-executor-mimo2.5pro.md",
    "$agentRoot\conductor-track-validator.md",
    "$agentRoot\conductor-track-validator-m3.md",
    "$agentRoot\conductor-track-validator-alt.md",
    "$agentRoot\conductor-doc-writer.md"
)

function Test-GuardrailSection {
    param([string]$FilePath, [string]$SectionPattern, [string[]]$RequiredStrings)
    
    if (-not (Test-Path -LiteralPath $FilePath)) {
        Write-Output "MISSING_FILE: $FilePath"
        return $false
    }
    
    $content = Get-Content -LiteralPath $FilePath -Raw
    $allPresent = $true
    
    foreach ($str in $RequiredStrings) {
        if (-not $content.Contains($str)) {
            Write-Output "MISSING_STRING: '$str' in $FilePath"
            $allPresent = $false
        }
    }
    
    return $allPresent
}

switch ($Mode) {
    "RedGate" {
        # RED gate: verify guardrail sections are MISSING (expected failure)
        $allMissing = $true
        
        foreach ($file in $skillFiles) {
            $content = if (Test-Path -LiteralPath $file) { Get-Content -LiteralPath $file -Raw } else { "" }
            $hasSection = $content -match "^##\s+DCP Child-Session Guardrail\s*$"
            
            if ($hasSection) {
                $allMissing = $false
                Write-Output "UNEXPECTED_PASS: $file already has guardrail section"
            }
        }
        
        if ($allMissing) {
            Write-Output "MISSING_GUARDRAIL: No skill files have DCP Child-Session Guardrail section"
            Write-Output "RED STATE CONFIRMED: Guardrail sections not yet implemented"
            exit 1
        } else {
            Write-Output "PASS conductor-guardrail"
            exit 0
        }
    }
    
    "ValidateSkill" {
        $allPass = $true
        
        foreach ($file in $skillFiles) {
            $result = Test-GuardrailSection -FilePath $file -SectionPattern "^##\s+DCP Child-Session Guardrail\s*$" -RequiredStrings $requiredStrings
            if (-not $result) {
                $allPass = $false
            }
        }
        
        if ($allPass) {
            Write-Output "PASS conductor-guardrail"
            exit 0
        } else {
            Write-Output "FAIL conductor-guardrail"
            exit 1
        }
    }
    
    "ValidateAgents" {
        $allPass = $true
        
        foreach ($file in $agentFiles) {
            $result = Test-GuardrailSection -FilePath $file -SectionPattern "^##\s+Bounded-Stage Guardrail\s*$" -RequiredStrings $requiredAgentStrings
            if (-not $result) {
                $allPass = $false
            }
        }
        
        if ($allPass) {
            Write-Output "PASS conductor-agents"
            exit 0
        } else {
            Write-Output "FAIL conductor-agents"
            exit 1
        }
    }
}
