const fs = require("fs");
const path = "C:/Users/DaveWitkin/.config/opencode/opencode.jsonc";
const src = fs.readFileSync(path, "utf8");
const lines = src.split(/\r?\n/);

// Brace balance
let braces = 0;
for (const line of lines) {
  for (const ch of line) {
    if (ch === "{") braces++;
    if (ch === "}") braces--;
  }
}
console.log("Brace balance:", braces === 0 ? "PASS (net 0)" : "FAIL (net " + braces + ")");

// Bracket balance
let brackets = 0;
for (const line of lines) {
  for (const ch of line) {
    if (ch === "[") brackets++;
    if (ch === "]") brackets--;
  }
}
console.log("Bracket balance:", brackets === 0 ? "PASS (net 0)" : "FAIL (net " + brackets + ")");

// Check key structural elements exist
console.log("Has $schema:", src.includes('"$schema"'));
console.log("Has provider:", src.includes('"provider"'));
console.log("Has openai provider:", src.includes('"openai"'));
console.log("Has npm @ai-sdk/openai:", src.includes('"@ai-sdk/openai"'));
console.log("Has google provider:", src.includes('"google"'));
console.log("Has openrouter provider:", src.includes('"openrouter"'));
console.log("Total lines:", lines.length);
