# DrawDB Format Templates

This document defines templates and specifications for generating DrawDB-compatible JSON and DBML formats.

## JSON Format Specification

### Complete Structure
```json
{
  "tables": [],
  "relationships": [],
  "notes": [],
  "subjectAreas": [],
  "database": "generic",
  "types": [],
  "title": "Database Name"
}
```

### Tables Structure
```json
{
  "id": "random_string_id",   // Unique table ID, using random string (e.g., "_KV5MtPf2m4sI7Inu8pat")
  "name": "table_name",       // Table name
  "comment": "Table comment", // Table COMMENT
  "color": "#6360f7",         // Header color (can use predefined colors)
  "fields": [],               // Fields array
  "indices": [],              // Indexes array
  "x": 100.5,                 // X coordinate in ER diagram (floating point)
  "y": 200.5                  // Y coordinate in ER diagram (floating point)
}
```

### Fields Structure
```json
{
  "id": "random_string_id",   // Field ID, using random string (e.g., "B8rPRTDtOv9oD2Gp4bhWL")
  "name": "field_name",       // Field name
  "type": "VARCHAR(100)",     // Complete data type definition (including length/precision)
  "default": "",              // Default value (string type, numbers also as strings)
  "check": "",                // CHECK constraint (usually empty string)
  "primary": false,           // Is primary key
  "unique": false,            // Is unique
  "notNull": false,           // Is NOT NULL
  "increment": false,         // Is auto-increment
  "comment": "Field comment"  // Field COMMENT
}
```

**Important notes:**
- `type` field contains complete type definition, e.g.: `"VARCHAR(100)"`, `"DECIMAL(10,2)"`, `"BIGINT"`
- **No separate `size` field**
- `default` is always string type, numeric defaults also use strings (e.g., `"0"`, `"false"`)
- Boolean type uses `"BOOLEAN"` or `"TINYINT(1)"`

### Indices Structure
```json
{
  "id": 0,                    // Index ID, using numeric increment
  "fields": ["field_name"],   // Field name array (note: use field names, not field IDs!)
  "name": "idx_field_name",   // Index name
  "unique": false             // Is unique index
}
```

**Important notes:**
- `fields` array uses **field name strings**, not field IDs
- Composite index example: `["field1", "field2"]`

### Relationships Structure
```json
{
  "name": "",                           // Relationship name (can be empty string)
  "startTableId": "table1_id",          // Start table ID (random string)
  "endTableId": "table2_id",            // Target table ID (random string)
  "endFieldId": "field_id",             // Target table field ID (random string, usually primary key)
  "startFieldId": "field_id",           // Start table field ID (random string)
  "id": "relationship_id",              // Relationship ID (random string)
  "updateConstraint": "No action",      // Update constraint
  "deleteConstraint": "No action",      // Delete constraint
  "cardinality": "many_to_one"          // Relationship type
}
```

**Important notes:**
- All IDs use random strings, not numbers
- Maintaining field order consistent with example helps with compatibility
- `name` can be empty string

#### Cardinality Types
- `many_to_one`: Many-to-one relationship (N:1) - most common
- `one_to_one`: One-to-one relationship (1:1)
- `one_to_many`: One-to-many relationship (1:N) - rarely used
- `many_to_many`: Many-to-many relationship (N:N) - requires junction table

### Data Type Mapping

#### MySQL to DrawDB
- `BIGINT` → `"BIGINT"`
- `INT` → `"INT"`
- `TINYINT` → `"TINYINT"`
- `TINYINT(1)` → `"TINYINT(1)"` (boolean)
- `VARCHAR(n)` → `"VARCHAR(n)"` (complete string with length)
- `TEXT` → `"TEXT"`
- `LONGTEXT` → `"LONGTEXT"`
- `DATETIME` → `"DATETIME"`
- `TIMESTAMP` → `"TIMESTAMP"`
- `DATE` → `"DATE"`
- `DECIMAL(m,n)` → `"DECIMAL(m,n)"` (complete string)
- `BOOLEAN` → `"BOOLEAN"`
- `ENUM(...)` → `"ENUM(VALUE1,VALUE2)"` (complete definition)

### Color Scheme
Use predefined color rotation:
```javascript
const colors = [
  "#6360f7",  // Purple
  "#bc49c4",  // Pink-purple
  "#ffe159",  // Yellow
  "#89e667",  // Green
  "#ff9159",  // Orange
  "#59d9ff",  // Blue
  "#ff5959",  // Red
  "#a0a0a0"   // Gray
];
// Rotate through based on table order
```

### Coordinate Layout Strategy
Simple grid layout:
```javascript
const GRID_WIDTH = 450;
const GRID_HEIGHT = 400;
const START_X = 50;
const START_Y = 50;

// Table position = (column_index * GRID_WIDTH + START_X, row_index * GRID_HEIGHT + START_Y)
// 3 tables per row
const x = (tableIndex % 3) * GRID_WIDTH + START_X;
const y = Math.floor(tableIndex / 3) * GRID_HEIGHT + START_Y;
```

### ID Generation Strategy

#### Table IDs and Field IDs
Use random string generator, recommended format:
- Length: 21 characters
- Character set: `A-Za-z0-9_-`
- Examples: `"_KV5MtPf2m4sI7Inu8pat"`, `"B8rPRTDtOv9oD2Gp4bhWL"`

```javascript
function generateId() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-';
  let id = '';
  for (let i = 0; i < 21; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return id;
}
```

#### Index IDs
Use numeric increment: 0, 1, 2, 3, ...

---

## DBML Format Specification

### Table Definition
```dbml
Table table_name [headercolor: #6360f7] {
  id bigint [pk, increment, not null, unique, note: 'Primary key ID']
  field_name varchar(100) [not null, default: '', note: 'Field comment']

  Note: 'Table comment'
}
```

### Field Attributes
- `pk` - Primary key
- `increment` - Auto-increment
- `not null` - Not null
- `unique` - Unique
- `default: value` - Default value
- `note: 'comment'` - Field comment

### Relationship Definition
```dbml
// Many-to-one relationship (N:1)
Ref fk_name {
  table1.field > table2.id [delete: no action, update: no action]
}

// One-to-one relationship (1:1)
Ref fk_name {
  table1.field - table2.id [delete: no action, update: no action]
}

// One-to-many relationship (1:N) - less common
Ref fk_name {
  table1.id < table2.field [delete: no action, update: no action]
}
```

#### Relationship Symbols
- `>` - many-to-one
- `-` - one-to-one
- `<` - one-to-many

### Index Definition
In DBML, indexes are inside table definitions:
```dbml
Table table_name {
  id int [pk]
  email varchar(100)
  username varchar(50)

  indexes {
    email [unique, name: 'uk_email']
    (username, created_at) [name: 'idx_username_created_at']
  }
}
```

### Data Type Mapping

#### MySQL to DBML
- `BIGINT` → `bigint`
- `INT` → `int`
- `TINYINT` → `tinyint`
- `VARCHAR(n)` → `varchar(n)`
- `TEXT` → `text`
- `DATETIME` → `datetime`
- `DATE` → `date`
- `DECIMAL(m,n)` → `decimal(m,n)`

### Complete Example
```dbml
Table user_info [headercolor: #6360f7] {
  id bigint [pk, increment, not null, unique, note: 'User ID']
  username varchar(50) [not null, note: 'Username']
  email varchar(100) [not null, note: 'Email address']
  phone varchar(20) [note: 'Phone number']
  created_at datetime [not null, default: `CURRENT_TIMESTAMP`, note: 'Creation time']
  updated_at datetime [not null, default: `CURRENT_TIMESTAMP`, note: 'Update time']
  is_deleted tinyint(1) [not null, default: 0, note: 'Is deleted']

  indexes {
    email [unique, name: 'uk_email']
    phone [unique, name: 'uk_phone']
    username [name: 'idx_username']
  }

  Note: 'User information table'
}

Table user_profile [headercolor: #bc49c4] {
  id bigint [pk, increment, not null, unique, note: 'Profile ID']
  user_id bigint [not null, unique, note: 'User ID']
  avatar varchar(500) [note: 'Avatar URL']
  gender tinyint [note: 'Gender: 0-Unknown, 1-Male, 2-Female']
  birthday date [note: 'Birthday']
  created_at datetime [not null, default: `CURRENT_TIMESTAMP`, note: 'Creation time']
  updated_at datetime [not null, default: `CURRENT_TIMESTAMP`, note: 'Update time']
  is_deleted tinyint(1) [not null, default: 0, note: 'Is deleted']

  indexes {
    user_id [unique, name: 'uk_user_id']
  }

  Note: 'User profile table'
}

Ref user_profile_user_id_fk {
  user_profile.user_id - user_info.id [delete: no action, update: no action]
}
```

---

## Generation Specifications

### JSON Generation Steps

1. **Generate IDs for tables and fields**
   - Generate unique random string ID for each table
   - Generate unique random string ID for each field
   - Create mapping from IDs to table names and field names for later lookup

2. **Build table structures**
   - Create each table following the Tables structure format
   - Set correct coordinates (grid layout)
   - Rotate through predefined colors

3. **Build fields**
   - type field includes complete type definition (e.g., "VARCHAR(100)")
   - default values always represented as strings
   - Correctly set primary, unique, notNull, increment flags

4. **Build indexes**
   - Use numeric ID increment (starting from 0, across all tables)
   - fields array uses field names, not field IDs

5. **Build relationships**
   - Generate unique random string ID for each relationship
   - Use correct table IDs and field IDs (random strings)
   - Set cardinality based on UNIQUE constraint

### DBML Generation Order
1. Generate table definitions one by one
2. Define fields within each table
3. Define indexes within tables (if any)
4. Add table comments
5. Finally generate all relationship definitions

### Comment Handling
- JSON format: Fill in comments directly in `comment` field
- DBML format: Fill in comments in `note: 'comment'` attribute
- Table comments: JSON uses `comment`, DBML uses `Note: 'comment'`

### Relationship Inference Rules
1. Identify all `xxx_id` fields as foreign key candidates
2. Find corresponding target table based on naming
3. Target field is usually the target table's primary key (generally the first field)
4. Determine relationship type based on whether field has UNIQUE constraint:
   - Has UNIQUE → one-to-one
   - No UNIQUE → many_to_one

---

## Complete JSON Generation Example

```json
{
  "tables": [
    {
      "id": "Abc123XyZ456pQrStUv78",
      "name": "user_info",
      "comment": "User information table",
      "color": "#6360f7",
      "fields": [
        {
          "id": "fld001Abc123XyZ456pQr",
          "name": "id",
          "type": "BIGINT",
          "default": "",
          "check": "",
          "primary": true,
          "unique": true,
          "notNull": true,
          "increment": true,
          "comment": "User ID"
        },
        {
          "id": "fld002Def456UvW789xYz",
          "name": "username",
          "type": "VARCHAR(50)",
          "default": "",
          "check": "",
          "primary": false,
          "unique": false,
          "notNull": true,
          "increment": false,
          "comment": "Username"
        },
        {
          "id": "fld003Ghi789AbC012dEf",
          "name": "email",
          "type": "VARCHAR(100)",
          "default": "",
          "check": "",
          "primary": false,
          "unique": true,
          "notNull": true,
          "increment": false,
          "comment": "Email address"
        }
      ],
      "indices": [
        {
          "id": 0,
          "fields": ["email"],
          "name": "uk_email",
          "unique": true
        },
        {
          "id": 1,
          "fields": ["username"],
          "name": "idx_username",
          "unique": false
        }
      ],
      "x": 50.0,
      "y": 50.0
    },
    {
      "id": "Xyz789MnO012pQrStUv34",
      "name": "order_info",
      "comment": "Order information table",
      "color": "#bc49c4",
      "fields": [
        {
          "id": "fld004Jkl345MnO678pQr",
          "name": "id",
          "type": "BIGINT",
          "default": "",
          "check": "",
          "primary": true,
          "unique": true,
          "notNull": true,
          "increment": true,
          "comment": "Order ID"
        },
        {
          "id": "fld005Stu901VwX234yZa",
          "name": "user_id",
          "type": "BIGINT",
          "default": "",
          "check": "",
          "primary": false,
          "unique": false,
          "notNull": true,
          "increment": false,
          "comment": "User ID"
        },
        {
          "id": "fld006Bcd567EfG890hIj",
          "name": "order_no",
          "type": "VARCHAR(50)",
          "default": "",
          "check": "",
          "primary": false,
          "unique": true,
          "notNull": true,
          "increment": false,
          "comment": "Order number"
        }
      ],
      "indices": [
        {
          "id": 2,
          "fields": ["order_no"],
          "name": "uk_order_no",
          "unique": true
        },
        {
          "id": 3,
          "fields": ["user_id"],
          "name": "idx_user_id",
          "unique": false
        }
      ],
      "x": 500.0,
      "y": 50.0
    }
  ],
  "relationships": [
    {
      "name": "",
      "startTableId": "Xyz789MnO012pQrStUv34",
      "endTableId": "Abc123XyZ456pQrStUv78",
      "endFieldId": "fld001Abc123XyZ456pQr",
      "startFieldId": "fld005Stu901VwX234yZa",
      "id": "rel001Klm678NoP901qRs",
      "updateConstraint": "No action",
      "deleteConstraint": "No action",
      "cardinality": "many_to_one"
    }
  ],
  "notes": [],
  "subjectAreas": [],
  "database": "generic",
  "types": [],
  "title": "E-commerce System Database"
}
```
