param(
  [switch]$Apply,
  [switch]$Rollback,
  [string]$ReportDir = 'C:\Users\DaveWitkin\.config\opencode\reports\codex-skill-junctions',
  [string]$ManifestPath = '',
  [string]$CodexRoot = 'C:\Users\DaveWitkin\.codex\skills',
  [string]$VaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault',
  [string]$NativeRoot = 'C:\Users\DaveWitkin\.config\opencode\skill'
)
$ErrorActionPreference = 'Stop'
$ExcludeNames = @('.system','_archived_skills')
function Is-Reparse([IO.FileSystemInfo]$Item){ [bool]($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) }
function Get-Target($Path){ $t=(Get-Item -LiteralPath $Path).Target; if($t -is [array]){ $t[0] } else { $t } }
function Ensure-Dir($Path){ if(-not(Test-Path -LiteralPath $Path)){ New-Item -ItemType Directory -Force -Path $Path | Out-Null } }
function Inventory($Store,$Root,$Exclude=@()){
  if(-not(Test-Path -LiteralPath $Root)){ return @() }
  @(Get-ChildItem -LiteralPath $Root -Directory -Force | Where-Object { $Exclude -notcontains $_.Name } | ForEach-Object {
    $rp=Is-Reparse $_; [pscustomobject]@{Store=$Store;Name=$_.Name;Path=$_.FullName;ExistingCodexPathType=if($rp){'junction'}else{'real-folder'};IsReparsePoint=$rp;Target=if($rp){Get-Target $_.FullName}else{$null};HasSkillMd=(Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md'))}
  })
}
function Build-Map($vault,$native){
  $vh=@{}; foreach($v in $vault){ $vh[$v.Name]=$v }
  $nh=@{}; foreach($n in $native){ $nh[$n.Name]=$n }
  $names=@($vh.Keys + $nh.Keys | Sort-Object -Unique)
  foreach($name in $names){
    $v=$vh[$name]; $n=$nh[$name]
    if($v -and $n){
      if($v.IsReparsePoint -and ($v.Target -eq $n.Path)){ [pscustomobject]@{Name=$name;Source='native';Target=$n.Path;CollisionStatus='duplicate-vault-junction-to-native';Precedence='native-over-vault-junction'} }
      elseif(-not $v.IsReparsePoint -and -not $n.IsReparsePoint){ [pscustomobject]@{Name=$name;Source=$null;Target=$null;CollisionStatus='conflict-vault-and-native-real';Precedence='manual-required'} }
      else { [pscustomobject]@{Name=$name;Source='native';Target=$n.Path;CollisionStatus='duplicate-default-native';Precedence='native-preferred-for-duplicates'} }
    } elseif($v){ [pscustomobject]@{Name=$name;Source='vault';Target=$v.Path;CollisionStatus='none';Precedence='vault-only'} }
    elseif($n){ [pscustomobject]@{Name=$name;Source='native';Target=$n.Path;CollisionStatus='none';Precedence='native-only'} }
  }
}
function Write-Report($obj){ Ensure-Dir $ReportDir; $stamp=Get-Date -Format 'yyyyMMdd-HHmmss'; $p=Join-Path $ReportDir "codex-skill-junction-report-$stamp.json"; $obj | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $p -Encoding utf8; $p }
if($Rollback){
  if([string]::IsNullOrWhiteSpace($ManifestPath)){ throw 'Rollback requires -ManifestPath' }
  $manifest=Get-Content -Raw -LiteralPath $ManifestPath | ConvertFrom-Json
  $actions=@()
  foreach($a in @($manifest.Actions | Where-Object { $_.Applied -eq $true } | Sort-Object Sequence -Descending)){
    if($a.Action -eq 'created-junction'){
      if(Test-Path -LiteralPath $a.CodexPath){ $it=Get-Item -LiteralPath $a.CodexPath; if(Is-Reparse $it){ cmd /c rmdir "$($a.CodexPath)" | Out-Null; $actions += [pscustomobject]@{Name=$a.Name;Action='rolled-back-created-junction';CodexPath=$a.CodexPath;Message='Removed junction created by manifest'} } }
    } elseif($a.Action -eq 'converted-real-folder-to-junction'){
      if(Test-Path -LiteralPath $a.CodexPath){ $it=Get-Item -LiteralPath $a.CodexPath; if(Is-Reparse $it){ cmd /c rmdir "$($a.CodexPath)" | Out-Null } }
      if($a.BackupPath -and (Test-Path -LiteralPath $a.BackupPath)){ Copy-Item -LiteralPath $a.BackupPath -Destination $a.CodexPath -Recurse -Force; $actions += [pscustomobject]@{Name=$a.Name;Action='restored-real-folder';CodexPath=$a.CodexPath;Message='Restored backup from manifest'} }
    }
  }
  $report=[pscustomobject]@{Apply=$false;Rollback=$true;GeneratedAt=(Get-Date).ToString('o');ManifestPath=$ManifestPath;Actions=$actions}
  Write-Report $report; exit 0
}
$codex=Inventory 'codex' $CodexRoot @()
$vault=Inventory 'vault' $VaultRoot $ExcludeNames
$native=Inventory 'native' $NativeRoot @()
$map=@(Build-Map $vault $native)
$actions=@(); $seq=0
foreach($m in $map){
  $seq++
  $codexPath=Join-Path $CodexRoot $m.Name
  if($m.CollisionStatus -like 'conflict*'){ $actions += [pscustomobject]@{Sequence=$seq;Name=$m.Name;Action='conflict';Source=$m.Source;Target=$m.Target;CodexPath=$codexPath;ExistingCodexPathType=$null;CollisionStatus=$m.CollisionStatus;Precedence=$m.Precedence;Applied=$false;BackupPath=$null;Message='Vault and native are both real folders; choose canonical target manually'}; continue }
  if(-not(Test-Path -LiteralPath $m.Target)){ $actions += [pscustomobject]@{Sequence=$seq;Name=$m.Name;Action='missing-target';Source=$m.Source;Target=$m.Target;CodexPath=$codexPath;ExistingCodexPathType=$null;CollisionStatus=$m.CollisionStatus;Precedence=$m.Precedence;Applied=$false;BackupPath=$null;Message='Canonical target does not exist'}; continue }
  if(Test-Path -LiteralPath $codexPath){
    $ci=Get-Item -LiteralPath $codexPath; $rp=Is-Reparse $ci; $ct=if($rp){Get-Target $codexPath}else{$null}
    if($rp -and $ct -eq $m.Target){ $actions += [pscustomobject]@{Sequence=$seq;Name=$m.Name;Action='ok-existing-junction';Source=$m.Source;Target=$m.Target;CodexPath=$codexPath;ExistingCodexPathType='junction';CollisionStatus=$m.CollisionStatus;Precedence=$m.Precedence;Applied=$false;BackupPath=$null;Message='Already points at canonical target'} }
    elseif($rp){ $actions += [pscustomobject]@{Sequence=$seq;Name=$m.Name;Action='would-repoint-junction';Source=$m.Source;Target=$m.Target;CodexPath=$codexPath;ExistingCodexPathType='junction';CollisionStatus=$m.CollisionStatus;Precedence=$m.Precedence;Applied=$false;BackupPath=$null;Message="Existing junction target differs: $ct"} }
    else { $actions += [pscustomobject]@{Sequence=$seq;Name=$m.Name;Action='real-folder-needs-manual-backup-convert';Source=$m.Source;Target=$m.Target;CodexPath=$codexPath;ExistingCodexPathType='real-folder';CollisionStatus=$m.CollisionStatus;Precedence=$m.Precedence;Applied=$false;BackupPath=$null;Message='Safety: weekly job will not delete real folders automatically; run approved backup/convert flow'} }
  } else {
    $action='would-create-junction'; $applied=$false
    if($Apply){ cmd /c mklink /j "$codexPath" "$($m.Target)" | Out-Null; $action='created-junction'; $applied=$true }
    $actions += [pscustomobject]@{Sequence=$seq;Name=$m.Name;Action=$action;Source=$m.Source;Target=$m.Target;CodexPath=$codexPath;ExistingCodexPathType='missing';CollisionStatus=$m.CollisionStatus;Precedence=$m.Precedence;Applied=$applied;BackupPath=$null;Message=if($Apply){'Created missing junction'}else{'Dry-run: would create junction'}}
  }
}
$report=[pscustomobject]@{Apply=[bool]$Apply;Rollback=$false;GeneratedAt=(Get-Date).ToString('o');CodexRoot=$CodexRoot;VaultRoot=$VaultRoot;NativeRoot=$NativeRoot;ExcludedNames=$ExcludeNames;Inventory=@($codex)+@($vault)+@($native);CanonicalTargets=$map;Actions=$actions}
$p=Write-Report $report
"Report: $p"
if(@($actions|Where-Object Action -eq 'conflict').Count -gt 0){ exit 2 }
if(@($actions|Where-Object Action -eq 'missing-target').Count -gt 0){ exit 3 }
exit 0

