# search_onedrive.ps1 — Path-safe local file search for OneDrive/SharePoint sync folders
# Does NOT access cloud APIs. Searches only the local filesystem.
# Uses LiteralPath to handle special characters in file paths safely.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RootPath,

    [Parameter(Mandatory = $true)]
    [string]$Pattern,

    [Parameter(Mandatory = $false)]
    [int]$MaxResults = 50
)

if (-not (Test-Path -LiteralPath $RootPath)) {
    Write-Warning "RootPath does not exist: $RootPath"
    exit 1
}

if (-not (Test-Path -LiteralPath $RootPath -PathType Container)) {
    Write-Warning "RootPath is not a directory: $RootPath"
    exit 1
}

$results = Get-ChildItem -LiteralPath $RootPath -Recurse -File -Filter $Pattern -ErrorAction SilentlyContinue |
    Select-Object -First $MaxResults |
    Select-Object FullName, Length, LastWriteTime

if ($results.Count -eq 0) {
    Write-Output "No files matching '$Pattern' found under $RootPath"
} else {
    Write-Output "Found $($results.Count) file(s) matching '$Pattern' under $RootPath (max $MaxResults):"
    $results | Format-Table -AutoSize
}
