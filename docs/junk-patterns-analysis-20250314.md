# Junk Mail Pattern Analysis

## Date: 2025-03-14
## Source: Manual junk mail review

---

## SAFE DOMAINS (Not Junk - Added to Allowlist)

| Domain | Notes |
|--------|-------|
| myskylight.com | Legitimate service |
| mail.perplexity.ai | AI assistant notifications |
| link.com | Link management platform |
| openart.ai | AI art platform |

---

## JUNK DOMAINS ADDED (53 total)

### Cold Outreach / B2B Lead Gen
- `tryedgestack.com`, `tryrefstack.com`, `tryechocloud.com` - "Try" prefix SaaS
- `getleadtools.com`, `getfutureflow.com` - "Get" prefix lead gen
- `growiqsparkhub.com`, `growoutreach.site` - "Grow" prefix marketing
- `campaignexhq.com`, `coldhivego.co` - Cold outreach services
- `wisepitchagency.com` - Pitch/outreach agency

### SEO / Marketing Spam
- `tools.seoforums01@outlook.com` - SEO tools spam
- `smallseoservice@hotmail.com` - SEO service spam
- `boostchatturaiads.online` - Ad service spam
- `mavenupweb.com` - Web marketing

### Conference / Event Spam
- `conferencetimex.com` - Conference registration spam
- `cognitivepublishing.co.uk` - Publishing/event spam
- `information.transcityrail.com` - Industry event spam
- `gotrademissions.digital` - Trade mission spam

### B2B Database / Data Sellers
- `clarab2bdatabase@gmail.com` - B2B data seller pattern
- `partners.hal9.com` - Partner/data spam
- `cohen-partners.com` - Fake partner outreach

### Randomized / Auto-Generated Usernames
These appear on consumer domains (gmail, hotmail, outlook) but follow patterns:
- `bricethomas1`, `ujwqqyb2378`, `pollybarnard45` - Name + number
- `leatricesalwasser5355`, `jenningsmiller656` - Full name + number
- `aaron.wells74`, `isabella.miller.01` - Name + number with dots
- `aarohi.sharma01`, `khanhly446688` - Patterned usernames

### Generic Role Addresses (High Spam Risk)
- `info@`, `admin@`, `hello@`, `support@` - When on suspicious domains
- `marketing@`, `communications@`, `investing@`
- `daily@`, `updates@`, `noreply@`, `notice@`

### Suspicious TLDs / Patterns
- `.xyz` domains: `monerabusinesscashflow.xyz`
- `.site` domains: `pltechhire.site`
- Double extension: `wallstreetenglish.ar` (Argentina TLD for English course)
- Subdomain spam: `agile.agileglobalbook.com`, `alpha.detroittraders.com`
- Hyphenated: `lusha-notice.com`

### Fake Vendor / Brand Impersonation
- `chevrolet@autogearmasters.com` - Brand name in local part
- `railtechnologymagazine@...` - Magazine impersonation
- `vciso@adiit.com` - Fake CISO title

### International / Geographic Spam
- `ygcn26.org.cn` - Chinese domain
- `kiemdinh.vn` - Vietnam
- `wallstreetenglish.ar` - Argentina
- `gwdciraq.com` - Iraq

---

## PATTERN CATEGORIES

### 1. Consumer Domain Suspicious Patterns
Since we never add `gmail.com`, `hotmail.com`, `outlook.com` to junk domains, we detect:

| Pattern Type | Example | Regex |
|--------------|---------|-------|
| Name+Number | `bricethomas1` | `^bricethomas[0-9]+` |
| Random string+Number | `ujwqqyb2378` | `^ujwqqyb[0-9]+` |
| B2B data sellers | `clarab2bdatabase` | `^clarab[0-9]+bdatabase` |
| SEO spam | `tools.seoforums01` | `^tools\.seo` |
| Role account on consumer | `smallseoservice@hotmail` | `^smallseoservice` |

### 2. Domain Name Patterns
| Pattern | Examples |
|---------|----------|
| `try` prefix | tryedgestack, tryrefstack, tryechocloud |
| `get` prefix | getleadtools, getfutureflow |
| `grow` prefix | growiqsparkhub, growoutreach |
| Hyphenated notice | lusha-notice |
| Suspicious TLD | .xyz, .site, .pro, .digital |

### 3. Subject Line Keywords
- "quick question"
- "podcast" (guest invitations)
- "valuation", "funding" (investment spam)
- "marketing", "seo"
- "outreach", "lead generation"
- "conference", "delegates"
- "partnership", "opportunity"

### 4. Body Content Phrases
- "i came across your profile"
- "would you be interested"
- "are you open to"
- "schedule a call"
- "15 minutes", "30 minutes"
- "b2b database"

---

## TRIAGE RULES

**DELETE NOW (High Confidence):**
- 2+ indicators match
- Known junk domain + any other indicator

**REVIEW (Medium Confidence):**
- Single indicator on consumer domain
- Generic role address on unknown domain

**KEEP (Safe):**
- Domain in safe list
- No indicators detected

---

## STATISTICS

| Category | Count |
|----------|-------|
| Safe domains | 4 |
| Junk domains | 53 |
| Unique local part patterns | 55 |
| Subject keywords | 15 |
| Body phrases | 12 |
| Consumer providers protected | 10 |

---

## NOTES

- Consumer providers (Gmail, Hotmail, Outlook, Yahoo) are NEVER added to junk domains list
- Instead, we use local_part regex patterns to catch suspicious usernames
- The pattern `clarab2bdatabase` appears 3 times in the list - high-frequency spammer
- Multiple senders use `hotmail.com` with numbered usernames - auto-generated accounts
