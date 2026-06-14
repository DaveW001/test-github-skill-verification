param(
    [string]$CacheBundle = "$env:USERPROFILE\.cache\opencode\packages\@zenobius\opencode-skillful@latest\node_modules\@zenobius\opencode-skillful\dist\index.js",
    [string]$ArtifactDir = "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path -LiteralPath $CacheBundle)) {
    throw "Skillful Desktop cache bundle not found: $CacheBundle"
}

$content = Get-Content -LiteralPath $CacheBundle -Raw

$oldRequire = 'var __require = import.meta.require;'
$newRequire = @'
import { createRequire as __createRequire } from "module";
var __require = __createRequire(import.meta.url);
'@.Trim()

$oldWindowsConfigImport = 'const importedConfig = await import(configPath + cacheBuster);'
$newWindowsConfigImport = 'const importedConfig = await import(pathToFileURL(configPath).href + cacheBuster);'

$oldSkillFs = @'
var readSkillFile = async (path) => {
  const file2 = Bun.file(path);
  return file2.text();
};
var listSkillFiles = (skillPath, subdirectory) => {
  const glob = new Bun.Glob(join(subdirectory, "**", "*"));
  return Array.from(glob.scanSync({ cwd: skillPath, absolute: true }));
};
var findSkillPaths = async (basePath) => {
  const glob = new Bun.Glob("**/SKILL.md");
  const results = [];
  for await (const path of glob.scan({ cwd: basePath, absolute: true })) {
    results.push(path);
  }
  return results;
};
'@.Trim()

$newSkillFs = @'
var readSkillFile = async (path) => {
  const { readFileSync } = __require("fs");
  return readFileSync(path, "utf8");
};
var listSkillFiles = (skillPath, subdirectory) => {
  const { readdirSync } = __require("fs");
  const results = [];
  const walk = (directory) => {
    if (!existsSync(directory)) {
      return;
    }
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const fullPath = join(directory, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
      } else {
        results.push(fullPath);
      }
    }
  };
  walk(join(skillPath, subdirectory));
  return results;
};
var findSkillPaths = async (basePath) => {
  const { readdirSync } = __require("fs");
  const results = [];
  const walk = (directory) => {
    if (!existsSync(directory)) {
      return;
    }
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const fullPath = join(directory, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.name === "SKILL.md") {
        results.push(fullPath);
      }
    }
  };
  walk(basePath);
  return results;
};
'@.Trim()

$requiresPatch = ($content -match [regex]::Escape($oldRequire)) -or ($content -match 'Bun\.file|Bun\.Glob') -or ($content -match [regex]::Escape($oldWindowsConfigImport))

if ($requiresPatch) {
    if ($content -notmatch [regex]::Escape($oldRequire) -and $content -notmatch 'createRequire as __createRequire') {
        throw "Expected Skillful require patch target not found. Inspect bundle before editing: $CacheBundle"
    }
    if ($content -match 'Bun\.file|Bun\.Glob' -and $content -notmatch [regex]::Escape($oldSkillFs)) {
        throw "Expected Skillful Bun filesystem block not found. Inspect bundle before editing: $CacheBundle"
    }

    New-Item -ItemType Directory -Path $ArtifactDir -Force | Out-Null
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backup = Join-Path $ArtifactDir "desktop-cache-index.js.backup-$timestamp"
    Copy-Item -LiteralPath $CacheBundle -Destination $backup -Force

    $patched = $content
    if ($patched -match [regex]::Escape($oldRequire)) {
        $patched = $patched.Replace($oldRequire, $newRequire)
    }
    if ($patched -match [regex]::Escape($oldWindowsConfigImport)) {
        if ($patched -notmatch 'import \{ pathToFileURL \} from "url";') {
            $patched = $patched.Replace('import { resolve as resolve5 } from "path";', "import { resolve as resolve5 } from `"path`";`r`nimport { pathToFileURL } from `"url`";")
        }
        $patched = $patched.Replace($oldWindowsConfigImport, $newWindowsConfigImport)
    }
    if ($patched -match 'Bun\.file|Bun\.Glob') {
        $patched = $patched.Replace($oldSkillFs, $newSkillFs)
    }
    Set-Content -LiteralPath $CacheBundle -Value $patched -NoNewline

    Write-Output "Patched Skillful Desktop cache bundle: $CacheBundle"
    Write-Output "Backup: $backup"
} else {
    Write-Output "Already patched: $CacheBundle"
}

$verify = Get-Content -LiteralPath $CacheBundle -Raw
if ($verify -match [regex]::Escape($oldRequire)) {
    throw "Patch verification failed: import.meta.require remains in $CacheBundle"
}
if ($verify -match 'Bun\.file|Bun\.Glob') {
    throw "Patch verification failed: Bun filesystem APIs remain in $CacheBundle"
}
if ($verify -notmatch 'createRequire as __createRequire') {
    throw "Patch verification failed: createRequire polyfill missing in $CacheBundle"
}
if ($verify -match [regex]::Escape($oldWindowsConfigImport)) {
    throw "Patch verification failed: Windows config import path fix missing in $CacheBundle"
}

$jsonConfig = @'
{
  "debug": false,
  "basePaths": [
    "C:/Users/DaveWitkin/.opencode-lazy-vault"
  ],
  "promptRenderer": "xml",
  "modelRenderers": {}
}
'@

$mjsConfig = @'
export default {
  debug: false,
  basePaths: [
    "C:/Users/DaveWitkin/.opencode-lazy-vault"
  ],
  promptRenderer: "xml",
  modelRenderers: {}
};
'@

# The archived plugin README documents %APPDATA%, but the bundled bunfig code in
# the cached package actually searches ~/.config/opencode-skillful on Windows.
# Use .mjs so Electron/Node can dynamic-import the config without JSON import
# assertions.
$homeConfigDir = Join-Path $env:USERPROFILE ".config\opencode-skillful"
$homeMjsConfigPath = Join-Path $homeConfigDir "opencode-skillful.config.mjs"
$homeJsonConfigPath = Join-Path $homeConfigDir ".opencode-skillful.json"
New-Item -ItemType Directory -Path $homeConfigDir -Force | Out-Null
Set-Content -LiteralPath $homeMjsConfigPath -Value $mjsConfig -NoNewline
Set-Content -LiteralPath $homeJsonConfigPath -Value $jsonConfig -NoNewline
Write-Output "Ensured Skillful importable Windows config: $homeMjsConfigPath"

# Keep the README-documented location populated for reference and for any future
# fixed release that follows the documented Windows path.
$appDataConfigDir = Join-Path $env:APPDATA "opencode-skillful"
$appDataConfigPath = Join-Path $appDataConfigDir "config.json"
New-Item -ItemType Directory -Path $appDataConfigDir -Force | Out-Null
Set-Content -LiteralPath $appDataConfigPath -Value $jsonConfig -NoNewline
Write-Output "Ensured Skillful README-documented Windows config: $appDataConfigPath"
