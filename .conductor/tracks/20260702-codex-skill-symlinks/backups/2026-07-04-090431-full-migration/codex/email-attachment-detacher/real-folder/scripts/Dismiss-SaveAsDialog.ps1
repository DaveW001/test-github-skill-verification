param(
    [string]$TitlePattern = 'Save As'
)

Add-Type -AssemblyName System.Windows.Forms

$signature = @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class Win32WindowTools {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
'@

if (-not ([System.Management.Automation.PSTypeName]'Win32WindowTools').Type) {
    Add-Type $signature
}

$matchedWindows = New-Object System.Collections.Generic.List[object]
[Win32WindowTools]::EnumWindows({
    param([IntPtr]$hWnd, [IntPtr]$lParam)
    if (-not [Win32WindowTools]::IsWindowVisible($hWnd)) { return $true }
    $buffer = New-Object System.Text.StringBuilder 256
    [void][Win32WindowTools]::GetWindowText($hWnd, $buffer, $buffer.Capacity)
    $title = $buffer.ToString()
    if ($title -match $TitlePattern) {
        $matchedWindows.Add([pscustomobject]@{ Handle = $hWnd; Title = $title })
    }
    return $true
}, [IntPtr]::Zero) | Out-Null

if ($matchedWindows.Count -eq 0) {
    Write-Output "No matching dialog found."
    exit 1
}

$target = $matchedWindows[0]
[void][Win32WindowTools]::SetForegroundWindow($target.Handle)
Start-Sleep -Milliseconds 150
[System.Windows.Forms.SendKeys]::SendWait('{ESC}')
Write-Output "Dismissed dialog: $($target.Title)"
