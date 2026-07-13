# Google Contacts — Tool Reference

## Google MCP Tools Used

All tools are from the `mcp-google` MCP server, configured as `mcp.google` in `opencode.json`.

### list-contacts

List Google Contacts. Returns array with resourceName, names, emailAddresses, phoneNumbers per contact.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | no | - | Search query to filter contacts |
| `pageSize` | number | no | 100 | Max contacts (max 2000) |
| `pageToken` | string | no | - | Pagination token |
| `personFields` | string | no | names,emailAddresses,phoneNumbers,addresses,organizations,biographies,photos | Fields to include |
| `sources` | array | no | ["READ_SOURCE_TYPE_CONTACT"] | Sources to search |

**Example — Search by name:**
```json
{
  "query": "Sarah",
  "pageSize": 10
}
```

**Example — Full contact list:**
```json
{
  "pageSize": 50,
  "personFields": "names,emailAddresses,phoneNumbers,organizations"
}
```

**Response shape:**
```json
[
  {
    "resourceName": "people/c1234567890",
    "names": [{"displayName": "Sarah Johnson", "givenName": "Sarah", "familyName": "Johnson"}],
    "emailAddresses": [{"value": "sarah@example.com", "type": "work"}],
    "phoneNumbers": [{"value": "+15551234567", "type": "mobile"}],
    "organizations": [{"name": "Company Inc.", "title": "VP Engineering"}]
  }
]
```

### get-contact

Retrieve one contact by resourceName. Returns full contact with all requested fields.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resourceName` | string | yes | Contact resource name (e.g., `people/c1234567890`) |
| `personFields` | string | no | Fields to include |

**Example:**
```json
{
  "resourceName": "people/c1234567890",
  "personFields": "names,emailAddresses,phoneNumbers,addresses,organizations,biographies"
}
```

### create-contact

Create new contact. Returns created contact with resourceName, etag, metadata.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `givenName` | string | no* | First name |
| `familyName` | string | no* | Last name |
| `middleName` | string | no | Middle name |
| `displayName` | string | no | Display name (defaults to givenName + familyName) |
| `emailAddresses` | array | no | Email objects with `value` and optional `type` |
| `phoneNumbers` | array | no | Phone objects with `value` and optional `type` |
| `addresses` | array | no | Address objects |
| `organizations` | array | no | Organization objects with `name`, `title`, `department` |
| `biographies` | array | no | Biography objects with `value` |
| `notes` | string | no | Notes (added as biography if no biographies) |

*At least givenName or familyName should be provided.

**Example:**
```json
{
  "givenName": "Jane",
  "familyName": "Doe",
  "emailAddresses": [{"value": "jane@example.com", "type": "work"}],
  "phoneNumbers": [{"value": "+15559876543", "type": "mobile"}],
  "organizations": [{"name": "Acme Corp", "title": "CTO", "type": "work"}],
  "notes": "Met at TechConf 2026"
}
```

### update-contact

Modify existing contact. Returns updated contact with new etag.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resourceName` | string | yes | Contact resource name to update |
| `updatePersonFields` | string | yes | Comma-separated fields being updated |
| `givenName` | string | no | Updated first name |
| `familyName` | string | no | Updated last name |
| `displayName` | string | no | Updated display name |
| `emailAddresses` | array | no | Replaces ALL emails |
| `phoneNumbers` | array | no | Replaces ALL phones |
| `addresses` | array | no | Replaces ALL addresses |
| `organizations` | array | no | Replaces ALL organizations |
| `biographies` | array | no | Replaces ALL biographies |

**⚠️ Warning:** Array fields (emails, phones, addresses, organizations, biographies) are fully replaced, not appended.

**Example — Update phone number:**
```json
{
  "resourceName": "people/c1234567890",
  "updatePersonFields": "phoneNumbers",
  "phoneNumbers": [
    {"value": "+15551112222", "type": "mobile"},
    {"value": "+15553334444", "type": "work"}
  ]
}
```

### delete-contact

Remove contact permanently. Returns empty on success.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resourceName` | string | yes | Contact resource name to delete |

**Example:**
```json
{
  "resourceName": "people/c1234567890"
}
```
