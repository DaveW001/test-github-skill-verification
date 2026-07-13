param(
  [switch]$Apply,
  [string]$TrackDir = 'C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks',
  [string]$CodexRoot = 'C:\Users\DaveWitkin\.codex\skills',
  [string]$VaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault',
  [string]$NativeRoot = 'C:\Users\DaveWitkin\.config\opencode\skill'
)
$ErrorActionPreference='Stop'
$ExcludeNames=@('.system','_archived_skills')
$PhaseMSkills=@('nlm-skill','pptx-to-pdf-converter')
function Is-Reparse($Path){ if(-not(Test-Path -LiteralPath $Path)){ return $false }; [bool]((Get-Item -LiteralPath $Path).Attributes -band [IO.FileAttributes]::ReparsePoint) }
function TargetOf($Path){ $t=(Get-Item -LiteralPath $Path).Target; if($t -is [array]){$t[0]}else{$t} }
function EnsureDir($Path){ if(-not(Test-Path -LiteralPath $Path)){ New-Item -ItemType Directory -Force -Path $Path|Out-Null } }
function CopyBackup($Source,$Dest){ if(-not(Test-Path -LiteralPath $Source)){ return $false }; EnsureDir (Split-Path -Parent $Dest); Copy-Item -LiteralPath $Source -Destination $Dest -Recurse -Force; return (Test-Path -LiteralPath $Dest) }
function RemoveJunction($Path){ if(Test-Path -LiteralPath $Path){ cmd /c rmdir "$Path" | Out-Null } }
function RemoveRealDir($Path){ if(Test-Path -LiteralPath $Path){ Remove-Item -LiteralPath $Path -Recurse -Force } }
function NewJunction($Link,$Target){ cmd /c mklink /j "$Link" "$Target" | Out-Null }
function HashSkill($Path){ $f=Join-Path $Path 'SKILL.md'; if(Test-Path -LiteralPath $f){ (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash } else { $null } }
function StripVersionFrontmatter($SkillPath){
  $file=Join-Path $SkillPath 'SKILL.md'; if(-not(Test-Path -LiteralPath $file)){ return }
  $lines=Get-Content -LiteralPath $file
  if($lines.Count -lt 3 -or $lines[0] -ne '---'){ return }
  $end=-1; for($i=1;$i -lt $lines.Count;$i++){ if($lines[$i] -eq '---'){ $end=$i; break } }
  if($end -lt 0){ return }
  $out=@(); for($i=0;$i -lt $lines.Count;$i++){ if($i -le $end -and $lines[$i] -match '^version\s*:'){ continue }; $out += $lines[$i] }
  Set-Content -LiteralPath $file -Value $out -Encoding utf8
}
function ValidateSkill($SkillPath){
  $validator=Join-Path $VaultRoot '.system\skill-creator\scripts\quick_validate.py'
  if(Test-Path -LiteralPath $validator){ $env:PYTHONUTF8='1'; $out=& python $validator $SkillPath 2>&1; return [pscustomobject]@{Ran=$true;ExitCode=$LASTEXITCODE;Output=($out -join "`n")} }
  return [pscustomobject]@{Ran=$false;ExitCode=$null;Output='validator missing'}
}
$stamp=Get-Date -Format 'yyyy-MM-dd-HHmmss'
$backupRoot=Join-Path $TrackDir "backups\$stamp-full-migration"
$reportPath=Join-Path $TrackDir "migration-executor-report-$stamp.json"
EnsureDir $backupRoot
$actions=@(); $seq=0
function AddAction($Name,$Action,$Path,$Target,$Applied,$Message,$Backup=$null,$Extra=$null){
  $script:seq++
  $script:actions += [pscustomobject]@{Sequence=$script:seq;Name=$Name;Action=$Action;Path=$Path;Target=$Target;Applied=[bool]$Applied;BackupPath=$Backup;Message=$Message;Extra=$Extra}
}
# Preflight backup roots marker
Set-Content -LiteralPath (Join-Path $backupRoot 'README.txt') -Value "Backup root for Codex/OpenCode skill migration $stamp. Nothing is removed unless its backup exists first." -Encoding utf8
# Phase M: move two native skills into real vault folders, then repoint Codex to vault and remove native.
foreach($name in $PhaseMSkills){
  $native=Join-Path $NativeRoot $name; $vault=Join-Path $VaultRoot $name; $codex=Join-Path $CodexRoot $name
  if(-not(Test-Path -LiteralPath $native) -and (Test-Path -LiteralPath $vault) -and -not(Is-Reparse $vault)){
    AddAction $name 'phase-m-already-migrated' $vault $null $false 'Vault is already real and native is absent.'
  } elseif(Test-Path -LiteralPath $native){
    $nativeBackup=Join-Path $backupRoot "phase-m\$name\native"
    if(-not(CopyBackup $native $nativeBackup)){ throw "Backup failed for native $name" }
    AddAction $name 'backup-native' $native $null $Apply "Backed up native before migration." $nativeBackup
    if($Apply){
      if(Test-Path -LiteralPath $vault){
        $vaultBackup=Join-Path $backupRoot "phase-m\$name\vault-existing"
        CopyBackup $vault $vaultBackup | Out-Null
        if(Is-Reparse $vault){ RemoveJunction $vault } else { RemoveRealDir $vault }
        AddAction $name 'remove-existing-vault-after-backup' $vault $null $true 'Removed existing vault entry after backup; junction removed with rmdir.' $vaultBackup
      }
      Copy-Item -LiteralPath $native -Destination $vault -Recurse -Force
      StripVersionFrontmatter $vault
      $validation=ValidateSkill $vault
      if($validation.Ran -and $validation.ExitCode -ne 0){ throw "Validation failed for ${name}: $($validation.Output)" }
      AddAction $name 'copy-native-to-real-vault' $vault $native $true 'Copied native to vault as real folder and validated/normalized frontmatter.' $null $validation
      if(Test-Path -LiteralPath $codex){
        $codexBackup=Join-Path $backupRoot "phase-m\$name\codex-existing"
        CopyBackup $codex $codexBackup | Out-Null
        if(Is-Reparse $codex){ RemoveJunction $codex } else { RemoveRealDir $codex }
        AddAction $name 'remove-existing-codex-after-backup' $codex $null $true 'Removed existing Codex entry after backup.' $codexBackup
      }
      NewJunction $codex $vault
      AddAction $name 'create-codex-junction-to-vault' $codex $vault $true 'Codex now points to real vault folder.'
      if(-not(Test-Path -LiteralPath (Join-Path $vault 'SKILL.md'))){ throw "Vault copy missing SKILL.md for $name" }
      if(-not(Test-Path -LiteralPath (Join-Path $codex 'SKILL.md'))){ throw "Codex junction missing SKILL.md for $name" }
      RemoveRealDir $native
      AddAction $name 'remove-native-after-backup-and-repoint' $native $null $true 'Removed native only after native backup, real vault copy, validation, and Codex repoint.' $nativeBackup
    } else {
      AddAction $name 'would-migrate-native-to-vault' $native $vault $false 'Dry-run: would make vault real, repoint Codex to vault, then remove native after backups.' $nativeBackup
    }
  } else {
    AddAction $name 'phase-m-missing-native' $native $vault $false 'Native missing and vault not clearly already migrated; inspect.'
  }
}
# Build canonical map after possible Phase M. Vault real or vault-only preferred; native-only native; vault junction to native native; vault real + native real conflict except native always-on duplicates where vault is junction.
$vaultItems=@(Get-ChildItem -LiteralPath $VaultRoot -Directory -Force | Where-Object { $ExcludeNames -notcontains $_.Name })
$nativeItems=@(Get-ChildItem -LiteralPath $NativeRoot -Directory -Force)
$vh=@{}; foreach($i in $vaultItems){$vh[$i.Name]=$i}
$nh=@{}; foreach($i in $nativeItems){$nh[$i.Name]=$i}
$names=@($vh.Keys + $nh.Keys | Sort-Object -Unique)
$canonical=@()
foreach($name in $names){
  $v=$vh[$name]; $n=$nh[$name]
  if($v -and $n){
    $vRp=Is-Reparse $v.FullName; $vT=if($vRp){TargetOf $v.FullName}else{$null}
    if($vRp -and $vT -eq $n.FullName){ $canonical += [pscustomobject]@{Name=$name;Target=$n.FullName;Reason='vault-junction-to-native'} }
    elseif(-not $vRp -and -not(Is-Reparse $n.FullName)){ $canonical += [pscustomobject]@{Name=$name;Target=$v.FullName;Reason='vault-real-preferred-over-native-real'} }
    else { $canonical += [pscustomobject]@{Name=$name;Target=$v.FullName;Reason='vault-preferred'} }
  } elseif($v){ $canonical += [pscustomobject]@{Name=$name;Target=$v.FullName;Reason='vault-only'} }
  elseif($n){ $canonical += [pscustomobject]@{Name=$name;Target=$n.FullName;Reason='native-only'} }
}
$canonical | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $backupRoot 'canonical-map.json') -Encoding utf8
# Convert Codex to junction layer.
foreach($c in $canonical){
  $codexPath=Join-Path $CodexRoot $c.Name
  if(-not(Test-Path -LiteralPath $c.Target)){ throw "Canonical target missing for $($c.Name): $($c.Target)" }
  if(Test-Path -LiteralPath $codexPath){
    if(Is-Reparse $codexPath){
      $cur=TargetOf $codexPath
      if($cur -eq $c.Target){ AddAction $c.Name 'codex-junction-already-correct' $codexPath $c.Target $false 'No change needed.'; continue }
      $meta=Join-Path $backupRoot "codex\$($c.Name)\junction-metadata.json"; EnsureDir (Split-Path -Parent $meta); [pscustomobject]@{Path=$codexPath;OldTarget=$cur;NewTarget=$c.Target;BackedUpAt=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $meta -Encoding utf8
      if($Apply){ RemoveJunction $codexPath; NewJunction $codexPath $c.Target; AddAction $c.Name 'repoint-codex-junction' $codexPath $c.Target $true "Repointed from $cur to canonical target." $meta }
      else { AddAction $c.Name 'would-repoint-codex-junction' $codexPath $c.Target $false "Dry-run: would repoint from $cur." $meta }
    } else {
      $backup=Join-Path $backupRoot "codex\$($c.Name)\real-folder"
      if(-not(CopyBackup $codexPath $backup)){ throw "Backup failed for real Codex folder $($c.Name)" }
      $oldHash=HashSkill $backup; $newHash=HashSkill $c.Target
      $extra=[pscustomobject]@{BackupSkillHash=$oldHash;TargetSkillHash=$newHash;SkillMdHashesMatch=($oldHash -and $newHash -and $oldHash -eq $newHash)}
      if($Apply){ RemoveRealDir $codexPath; NewJunction $codexPath $c.Target; AddAction $c.Name 'convert-real-codex-folder-to-junction' $codexPath $c.Target $true 'Backed up real Codex folder, removed it, and created junction to canonical target.' $backup $extra }
      else { AddAction $c.Name 'would-convert-real-codex-folder-to-junction' $codexPath $c.Target $false 'Dry-run: would backup real folder, remove it, and create junction.' $backup $extra }
    }
  } else {
    if($Apply){ NewJunction $codexPath $c.Target; AddAction $c.Name 'create-missing-codex-junction' $codexPath $c.Target $true 'Created missing Codex junction.' }
    else { AddAction $c.Name 'would-create-missing-codex-junction' $codexPath $c.Target $false 'Dry-run: would create missing Codex junction.' }
  }
}
# Final validation
$dangling=@(); $nonJunction=@(); $excludedPresent=@()
foreach($i in @(Get-ChildItem -LiteralPath $CodexRoot -Directory -Force)){
  if($ExcludeNames -contains $i.Name){ $excludedPresent += $i.FullName; continue }
  if(Is-Reparse $i.FullName){ $t=TargetOf $i.FullName; if(-not(Test-Path -LiteralPath $t)){ $dangling += [pscustomobject]@{Name=$i.Name;Path=$i.FullName;Target=$t} } }
  else { $nonJunction += $i.FullName }
}
$report=[pscustomobject]@{Apply=[bool]$Apply;GeneratedAt=(Get-Date).ToString('o');BackupRoot=$backupRoot;CodexRoot=$CodexRoot;VaultRoot=$VaultRoot;NativeRoot=$NativeRoot;PhaseMSkills=$PhaseMSkills;ExcludedNames=$ExcludeNames;Actions=$actions;DanglingCodexJunctions=$dangling;NonJunctionCodexDirs=$nonJunction;ExcludedCodexDirsPresent=$excludedPresent}
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding utf8
Copy-Item -LiteralPath $reportPath -Destination (Join-Path $backupRoot 'migration-report.json') -Force
Compress-Archive -LiteralPath $backupRoot -DestinationPath "$backupRoot.zip" -Force
"Report: $reportPath"
"BackupRoot: $backupRoot"
if(@($dangling).Count -gt 0){ exit 3 }
if($Apply -and @($nonJunction).Count -gt 0){ exit 4 }
exit 0

