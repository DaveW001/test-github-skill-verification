const fs = require("fs");
const p = "C:\\Users\\DaveWitkin\\.config\\opencode\\opencode.jsonc";
let s = fs.readFileSync(p, "utf8");
s = s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1").replace(/,\s*([}\]])/g, "$1");
const cfg = JSON.parse(s);
const providers = cfg.provider || cfg.providers || {};
for (const name of ["zai-coding-plan", "opencode-go"]) {
  const b = providers[name];
  if (!b || !b.options || b.options.timeout !== 600000 || b.options.headerTimeout !== 60000 || b.options.chunkTimeout !== 120000) {
    throw new Error(name + " timeout options missing or wrong");
  }
}
console.log("OK JSONC parses and provider timeout option bodies verified");
