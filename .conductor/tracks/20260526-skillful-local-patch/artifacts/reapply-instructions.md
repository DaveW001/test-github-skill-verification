# Re-application Instructions: skillful createRequire Polyfill

## Problem

`@zenobius/opencode-skillful` v1.2.5 bundles a Bun-specific API (`import.meta.require`) on line 28 of `dist/index.js`. Node.js does not support this, causing `TypeError: __require is not a function` at runtime.

## Target File

```
C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js
```

## Patch

**oldString:**
```js
var __require = import.meta.require;
```

**newString:**
```js
import { createRequire as __createRequire } from "module";
var __require = __createRequire(import.meta.url);
```

## Steps to Re-apply

1. **Backup:**
   ```powershell
   Copy-Item "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" "C:\path\to\backup\index.js.backup"
   ```

2. **Apply patch** - replace the oldString with newString in `dist/index.js`.

3. **Verify:**
   ```powershell
   Select-String -LiteralPath "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" -Pattern "import.meta.require"
   # Should return zero matches.

   Select-String -LiteralPath "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" -Pattern "createRequire"
   # Should return the new lines.

   node -e "import('file:///C:/Users/DaveWitkin/AppData/Roaming/npm/node_modules/@zenobius/opencode-skillful/dist/index.js').then(() => console.log('OK')).catch(e => console.error(e.constructor.name, e.message))"
   # Should print OK.
   ```

## Warning

**`npm update -g @zenobius/opencode-skillful` will overwrite this patch.** Re-apply after any global update until the upstream package is fixed.

## Why This Works

ES module `import` declarations are hoisted by the JavaScript engine regardless of where they appear in the file. The bundled file already uses inline `import` statements elsewhere (lines 16191+), so this pattern is consistent. `createRequire(import.meta.url)` is the standard Node.js way to obtain a CommonJS `require` function inside an ES module.
