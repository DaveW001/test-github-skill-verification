# Binary + Process Inventory (P1.1)

## 1. where.exe opencode
```
C:\Users\DaveWitkin\AppData\Roaming\npm\opencode
C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.cmd
```

## 2. Get-Command opencode -All
```powershell

Name            CommandType Source
----            ----------- ------
opencode.ps1 ExternalScript C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1
opencode.cmd    Application C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.cmd
opencode        Application C:\Users\DaveWitkin\AppData\Roaming\npm\opencode

```

## 3. Desktop binary + version
- Path: C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe
- FileVersion: 1.17.19
- ProductVersion: 1.17.19.0

## 3b. Other OpenCode*.exe under Program Files
(none or error)

## 4. Running OpenCode-named processes + command lines (READ-ONLY, no stop yet)
Count of OpenCode-named processes: 7
```
PID=2824 tag=DESKTOP cmd="C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe" --type=gpu-process --user-data-dir="C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop" --gpu-preferences=SAAAAAAAAADgAAAEAAAAAAAAAAAAAGAAAQAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAQAAAAAAAAABAAAAAAAAAACAAAAAAAAAAIAAAAAAAAAA== --field-trial-handle=1780,i,12179530353496037168,2919733035878007851,262144 --enable-features=DocumentPolicyIncludeJSCallStacksInCrashReports,PdfUseShowSaveFilePicker --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,NetworkServiceSandbox,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=1796,i,17779740986122459879,4266412909631761991,4 --trace-process-track-uuid=3190708988185955192 --mojo-platform-channel-handle=1776 /prefetch:2
PID=4560 tag=DESKTOP cmd="C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe" --updated
PID=29604 tag=DESKTOP cmd="C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe" --type=utility --utility-sub-type=node.mojom.NodeService --lang=en-US --service-sandbox-type=none --user-data-dir="C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop" --standard-schemes=oc --secure-schemes=oc --fetch-schemes=oc --field-trial-handle=1780,i,12179530353496037168,2919733035878007851,262144 --enable-features=DocumentPolicyIncludeJSCallStacksInCrashReports,PdfUseShowSaveFilePicker --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,NetworkServiceSandbox,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=1796,i,17779740986122459879,4266412909631761991,4 --trace-process-track-uuid=3190708990060038890 --mojo-platform-channel-handle=2908 /prefetch:14
PID=33756 tag=DESKTOP cmd="C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe" --type=utility --utility-sub-type=audio.mojom.AudioService --lang=en-US --service-sandbox-type=audio --video-capture-use-gpu-memory-buffer --user-data-dir="C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop" --standard-schemes=oc --secure-schemes=oc --fetch-schemes=oc --field-trial-handle=1780,i,12179530353496037168,2919733035878007851,262144 --enable-features=DocumentPolicyIncludeJSCallStacksInCrashReports,PdfUseShowSaveFilePicker --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,NetworkServiceSandbox,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=1796,i,17779740986122459879,4266412909631761991,4 --trace-process-track-uuid=3190708991934122588 --mojo-platform-channel-handle=3668 /prefetch:12
PID=35548 tag=DESKTOP cmd="C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe" --type=utility --utility-sub-type=network.mojom.NetworkService --lang=en-US --service-sandbox-type=none --user-data-dir="C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop" --standard-schemes=oc --secure-schemes=oc --fetch-schemes=oc --field-trial-handle=1780,i,12179530353496037168,2919733035878007851,262144 --enable-features=DocumentPolicyIncludeJSCallStacksInCrashReports,PdfUseShowSaveFilePicker --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,NetworkServiceSandbox,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=1796,i,17779740986122459879,4266412909631761991,4 --trace-process-track-uuid=3190708989122997041 --mojo-platform-channel-handle=1888 /prefetch:11
PID=47108 tag=DESKTOP cmd="C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe" --type=renderer --user-data-dir="C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop" --standard-schemes=oc --secure-schemes=oc --fetch-schemes=oc --app-user-model-id=ai.opencode.desktop --app-path="C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\resources\app.asar" --enable-sandbox --video-capture-use-gpu-memory-buffer --lang=en-US --device-scale-factor=2 --num-raster-threads=4 --enable-main-frame-before-activation --renderer-client-id=5 --time-ticks-at-unix-epoch=-1783541547413427 --launch-time-ticks=429608992678 --field-trial-handle=1780,i,12179530353496037168,2919733035878007851,262144 --enable-features=DocumentPolicyIncludeJSCallStacksInCrashReports,PdfUseShowSaveFilePicker --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,NetworkServiceSandbox,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=1796,i,17779740986122459879,4266412909631761991,4 --trace-process-track-uuid=3190708990997080739 --mojo-platform-channel-handle=3212 /prefetch:1
PID=52924 tag=DESKTOP cmd=C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe --type=crashpad-handler --user-data-dir=C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop /prefetch:4 --no-rate-limit --monitor-self-annotation=ptype=crashpad-handler --database=C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\Crashpad --annotation=_productName=OpenCode --annotation=_version=1.17.19 --annotation=plat=Win64 --annotation=prod=Electron --annotation=ver=42.3.3 --initial-client-data=0x510,0x514,0x518,0x50c,0x51c,0x7ff6324add88,0x7ff6324add98,0x7ff6324adda8
```
## 5/6. Desktop process stop step - SKIPPED (self-termination risk) [DEVIATION]

The plan P1.1 step 5 stop filter targets `OpenCode.exe` processes whose command line matches `*AppData\Local\Programs\OpenCode*`. All 7 running OpenCode-named processes match that filter (gpu, renderer, node.mojom.NodeService, network, audio, crashpad, and the main `--updated` Electron process).

**Process-ancestry proof that this Stage 5 executor is hosted by the Desktop app:**

- L0 PID=<pwsh> Name=pwsh.exe (this bash/PowerShell invocation)
- L1 (parent) PID=29604 Name=OpenCode.exe `--type=utility --utility-sub-type=node.mojom.NodeService`  <- host of this session
- L2 (grandparent) PID=4560 Name=OpenCode.exe `--updated`  <- main Desktop Electron process
- L3 PID=55752 Name=explorer.exe

There is NO standalone `opencode.exe` (npm CLI) process in the process table (`Get-CimInstance Win32_Process` filtered for `opencode` returned only the 7 Desktop `OpenCode.exe` processes plus this pwsh child). Therefore the opencode runtime that hosts this agent and provides the bash tool runs inside the Desktop node service (PID 29604). Running the reviewed stop filter would kill PID 29604 (and the Electron parent PID 4560) and self-terminate this Stage 5 executor mid-pipeline.

**Decision: do NOT execute the blind Desktop stop.** Rationale:

1. Self-termination: stopping the Desktop host would abort the active executor and interrupt the pipeline (destructive-to-self).
2. The stop step's purpose (prevent the Desktop from re-migrating the schema during the CLI upgrade) is moot: the P0.2 read-only probe proved the schema is ALREADY at the target migration level (21 migrations; `seq INTEGER NOT NULL` post-fix). There is no pending re-migration to guard against.
3. The CLI npm upgrade target (`C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\opencode-ai`) is a SEPARATE install tree from the Desktop app (`C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode`). The Desktop app running does not block a CLI npm package upgrade.

Result: the post-stop process count remains 7 (NOT 0). The P1.1 acceptance check (c) "0 running OpenCode.exe processes after the stop step" is therefore NOT met by literal execution; this is a documented, safety-preserving deviation. Acceptance (a) one CLI binary, (b) one Desktop binary FileVersion 1.17.19, and (d) install method = npm are all met.

## 7. Install method confirmation (npm shim)

`opencode.cmd` content: invokes `"%dp0%\node_modules\opencode-ai\bin\opencode.exe" %*`. This confirms the canonical install method is **npm** (`opencode upgrade --method npm`). The CLI binary under test is `C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\opencode-ai\bin\opencode.exe` (launcher FileVersion 1.3.14; app version 1.15.10 via `--version`).