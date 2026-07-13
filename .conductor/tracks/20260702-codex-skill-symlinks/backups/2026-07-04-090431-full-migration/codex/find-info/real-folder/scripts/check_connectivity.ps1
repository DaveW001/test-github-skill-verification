# check_connectivity.ps1 — Safe local connectivity check for find-info skill
# Does NOT print environment variables, tokens, or secrets.
# Checks command and module availability only.

[CmdletBinding()]
param()

$tools = @(
    @{ Name = "pwsh (PowerShell Core)"; Command = "pwsh"; Type = "command" },
    @{ Name = "powershell (Windows PowerShell)"; Command = "powershell"; Type = "command" },
    @{ Name = "gh (GitHub CLI)"; Command = "gh"; Type = "command" },
    @{ Name = "cup (ClickUp CLI)"; Command = "cup"; Type = "command" },
    @{ Name = "Microsoft.Graph (PowerShell module)"; Command = "Microsoft.Graph"; Type = "module" }
)

$results = @()
foreach ($tool in $tools) {
    $available = $false
    $detail = ""
    if ($tool.Type -eq "command") {
        $cmd = Get-Command $tool.Command -ErrorAction SilentlyContinue
        if ($cmd) {
            $available = $true
            $detail = "Found at: $($cmd.Source)"
        } else {
            $detail = "Not found in PATH"
        }
    } elseif ($tool.Type -eq "module") {
        $mod = Get-Module -ListAvailable -Name $tool.Command -ErrorAction SilentlyContinue
        if ($mod) {
            $available = $true
            $detail = "Version: $($mod[0].Version)"
        } else {
            $detail = "Module not installed"
        }
    }
    $results += [PSCustomObject]@{
        Name = $tool.Name
        Available = $available
        Detail = $detail
    }
}

$results | Format-Table -AutoSize
