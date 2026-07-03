# Espanso Snippet Management

> Audience: AI agents and humans adding or modifying text-expansion snippets in espanso.
> Goal: make changes that load on the first try. espanso disables the ENTIRE match file on a
> single YAML error, so correctness matters more than speed.

## 1. Where espanso lives

| Item | Path |
|---|---|
| Match files (snippets) | `%APPDATA%\espanso\match\*.yml` -> `C:\Users\<user>\AppData\Roaming\espanso\match\` |
| Config | `%APPDATA%\espanso\config\default.yml` |
| Daemon binary | `C:\Users\<user>\AppData\Local\Programs\Espanso\espansod.exe` (v2.3.x) |
| Launcher shim | `...\Espanso\espanso.cmd` -- BROKEN/empty in this install; do NOT rely on it |

espanso loads EVERY `.yml` under `match\`. A syntax error in one file disables the matches in
that file and logs `[ERROR] unable to load match group <file>`.

## 2. Anatomy of a match file

```yaml
matches:
  - trigger: "#word"
    replace: "expanded text"
```

- Top-level key is always `matches:` (2-space indent).
- Each snippet is a list item under it: `- trigger:` at 2 spaces.
- The snippet's own keys (`replace`, `triggers`, `vars`, `word`, `image_path`, ...) sit at 4 spaces.

## 3. Indentation ruler (read this twice)

YAML is whitespace-sensitive. Nearly every espanso error is an indentation mistake.
Memorize this ladder -- each nesting level adds exactly 2 spaces, never tabs:

```
COLUMN:  0   2   4   6   8   10
matches:
          - trigger: "#x"        <- item + its first key on one line (2 sp)
            replace: "..."       <- item's sibling keys (4 sp)
            vars:                <- still 4 sp
              - name: myvar      <- list item under vars (6 sp)
                type: date       <- that item's keys (8 sp)
                params:          <- 8 sp
                  format: "%x"   <- nested key (10 sp)
```

## 4. Triggers

- Single trigger: `trigger: "#today"`
- Multiple aliases for one expansion: `triggers: ["#today", "##d", "#date"]`
- Trigger text may contain `#`, letters, digits, `-`, `_`. Avoid spaces.

## 5. Replacements

Single-line (double-quote the value if it contains `:`, `#`, `{`, `}`, or a literal `"`):
```yaml
  - trigger: "#emg"
    replace: "davidawitkin@gmail.com"
```

Multi-line block (note the `|`; body is indented to 6 spaces, i.e. +2 under the 4-space `replace:`):
```yaml
  - trigger: "#homeadd"
    replace: |
      1401 Concord Point Lane
      Reston, VA 20194
```
The `|` (literal block scalar) preserves newlines exactly. Blank lines inside the block are
preserved -- keep them indented to the same column as the body.

## 6. Variables (date, shell, etc.)

A variable computes a value referenced as `{{varname}}`. The `vars:` block is where most
indentation bugs happen.

```yaml
  - trigger: "#todaylong"
    replace: "{{mydatelong}}"
    vars:
      - name: mydatelong
        type: date
        params:
          format: "%A, %B %d, %Y"
```

Common `date` format codes:
- `%Y-%m-%d`              -> 2026-07-03
- `%A, %B %d, %Y`         -> Friday, July 03, 2026
- `%Y-%m-%d %I:%M:%S %p`  -> 2026-07-03 02:14:00 PM

### The bug we keep hitting

`- name:` MUST be at 6 spaces (nested under `vars:`). If it slips to 2 spaces it lands at the
`matches:` list level and breaks the whole file:

```yaml
    vars:
  - name: mydate      # WRONG -- only 2 spaces; parser reads this as a new match item
        type: date    # <- "mapping values are not allowed in this context" fires HERE
```

## 7. Copy-paste templates

### Plain text
```yaml
  # LABEL (comment; keep at 2 spaces)
  - trigger: "#tag"
    replace: "value"
```

### Multi-trigger
```yaml
  - triggers: ["#a", "#b"]
    replace: "value"
```

### Multi-line
```yaml
  - trigger: "#tag"
    replace: |
      Line one
      Line two
```

### Date variable
```yaml
  - trigger: "#tag"
    replace: "{{mydate}}"
    vars:
      - name: mydate
        type: date
        params:
          format: "%Y-%m-%d"
```

## 8. Comment placement

Comments start with `#`. Inside the `matches:` list, indent them to 2 spaces so they sit with
the snippets:
```yaml
  # Calendly 15 Min
  - trigger: "#cal15"
```
A column-0 comment is technically valid but inconsistent with the rest of the file -- keep
comments at 2 spaces.

## 9. Validate after every edit (required)

espanso does not auto-validate; a bad edit silently disables the file until reload. Always
validate before walking away.

### Step 1 -- parse the YAML
```powershell
python -c "import yaml; yaml.safe_load(open(r'C:\Users\DaveWitkin\AppData\Roaming\espanso\match\migrated_snippets.yml',encoding='utf-8')); print('OK')"
```
Prints `OK` = structurally valid. (No Python? `pip install pyyaml`, or skip to Step 2.)

### Step 2 -- confirm espanso loads the matches
The `espanso.cmd` shim is broken in this install. Use the daemon binary directly:
```powershell
& "C:\Users\DaveWitkin\AppData\Local\Programs\Espanso\espansod.exe" match list
```
- Exit code 0 + your triggers listed = the file loaded.
- Exit code 1 with `[ERROR] unable to load match group` = still broken; the message names the
  file, line, and column.

### Step 3 -- reload the running daemon (if edits do not appear)
```powershell
# Listing (Step 2) forces a parse. For a hard reload when run as a Windows service:
Restart-Service espanso
```

## 10. Error cheat sheet

| Error | Almost always means |
|---|---|
| `mapping values are not allowed [in this context | here] at line N col M  (espanso: "...in this context"; PyYAML: "...here")` | A key (often `- name:` under `vars:`, or a sibling key) is at the wrong indent. Recheck the ladder in section 3. |
| `did not find expected key` / `while parsing a block mapping` | A snippet item lost its indentation or a `- ` bullet is misaligned. |
| `unable to load match group <file>` | The named file has a YAML error -- fix per the line/col in the nested cause. |
| Trigger does not expand after a good edit | Daemon needs a reload (section 9, Step 3), or the file is excluded in config. |

## 11. Do / Don't

Do:
- Copy an existing working snippet and edit in place -- it preserves correct indentation.
- Validate (section 9) after every change.
- Keep a `.bak` before bulk edits: `Copy-Item file.yml file.yml.bak`.

Don't:
- Don't mix tabs and spaces. Spaces only.
- Don't put `- name:` at 2 spaces under `vars:` (the #1 recurring bug).
- Don't put snippet comments at column 0; use 2 spaces.
- Don't trust a silent success -- always run `espansod.exe match list`.

## 12. Quick reference: indent cheatsheet

```
matches:                    # 0 sp
  - trigger: "#x"           # 2 sp  (item + first key)
    replace: "y"            # 4 sp
    triggers: ["#a","#b"]   # 4 sp  (use instead of trigger: for aliases)
    vars:                   # 4 sp
      - name: v             # 6 sp  (under vars:)
        type: date          # 8 sp
        params:             # 8 sp
          format: "%Y"      # 10 sp
```
