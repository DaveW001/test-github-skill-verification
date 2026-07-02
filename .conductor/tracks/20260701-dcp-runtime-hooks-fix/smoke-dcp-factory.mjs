import { pathToFileURL } from 'node:url';
const pkgPath = 'C:/Users/DaveWitkin/.cache/opencode/packages/@tarquinen/opencode-dcp@latest/node_modules/@tarquinen/opencode-dcp/dist/index.js';
try {
  const mod = await import(pathToFileURL(pkgPath).href);
  const factory = mod.default ?? mod.server ?? mod.plugin ?? mod;
  const ctx = { directory: 'C:/development/opencode' };
  let result = null;
  let factoryCalled = false;
  let factoryError = null;
  if (typeof factory === 'function') {
    factoryCalled = true;
    try { result = await factory(ctx); } catch (e) { factoryError = String((e && e.message) || e); }
  } else {
    result = factory;
  }
  const keys = result && typeof result === 'object' ? Object.keys(result).sort() : [];
  console.log(JSON.stringify({
    ok: true,
    exportKeys: Object.keys(mod).sort(),
    factoryCalled,
    factoryError,
    hookKeys: keys,
    hasConfig: keys.includes('config'),
    hasTool: keys.includes('tool'),
    hasCommandBefore: keys.includes('command.execute.before'),
    hasMessagesTransform: keys.includes('experimental.chat.messages.transform')
  }));
} catch (e) {
  console.log(JSON.stringify({ ok: false, error: String((e && e.message) || e) }));
}
