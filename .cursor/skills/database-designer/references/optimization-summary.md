# DrawDB JSON Format Optimization Summary

## Main Changes

Based on analysis of real DrawDB JSON files, here are the key format corrections:

### 1. ID Format Changes

**Original format (incorrect):**
- Table ID: Numeric increment (0, 1, 2, ...)
- Field ID: Numeric increment within table (0, 1, 2, ...)
- Relationship ID: Numeric increment (0, 1, 2, ...)

**New format (correct):**
- Table ID: **21-character random string** (e.g., `"_KV5MtPf2m4sI7Inu8pat"`)
- Field ID: **21-character random string** (e.g., `"B8rPRTDtOv9oD2Gp4bhWL"`)
- Relationship ID: **21-character random string** (e.g., `"vrbZaYZLNo_ESZWqI5KHv"`)
- Index ID: **Numeric increment** (0, 1, 2, ...) - globally incremented across all tables

### 2. Type Field Format Changes

**Original format (incorrect):**
```json
{
  "type": "VARCHAR",
  "size": 100
}
```

**New format (correct):**
```json
{
  "type": "VARCHAR(100)"
}
```

- **No separate size field**
- Type definition includes complete information: `"VARCHAR(100)"`, `"DECIMAL(10,2)"`, `"TINYINT(1)"`

### 3. Index Field Reference Changes

**Original format (incorrect):**
```json
{
  "fields": [0, 1]  // Using field ID numbers
}
```

**New format (correct):**
```json
{
  "fields": ["email", "username"]  // Using field name strings
}
```

### 4. Table Structure Field Order

**Original order (not recommended):**
```json
{
  "id": "...",
  "name": "...",
  "x": 100,
  "y": 100,
  "fields": [],
  "comment": "...",
  "indices": [],
  "color": "#6360f7"
}
```

**New order (recommended):**
```json
{
  "id": "...",
  "name": "...",
  "comment": "...",
  "color": "#6360f7",
  "fields": [],
  "indices": [],
  "x": 100.0,
  "y": 100.0
}
```

### 5. Relationship Field Order

**New order (recommended):**
```json
{
  "name": "",
  "startTableId": "...",
  "endTableId": "...",
  "endFieldId": "...",
  "startFieldId": "...",
  "id": "...",
  "updateConstraint": "No action",
  "deleteConstraint": "No action",
  "cardinality": "many_to_one"
}
```

---

## Python Implementation Example

```python
import random
import string
import json

class DrawDBGenerator:
    def __init__(self):
        self.colors = [
            "#6360f7",  # Purple
            "#bc49c4",  # Pink-purple
            "#ffe159",  # Yellow
            "#89e667",  # Green
            "#ff9159",  # Orange
            "#59d9ff",  # Blue
            "#ff5959",  # Red
            "#a0a0a0"   # Gray
        ]
        self.index_id_counter = 0
        self.table_map = {}  # table_name -> {id, fields: {field_name -> id}}

    def generate_id(self):
        """Generate 21-character random ID"""
        chars = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choice(chars) for _ in range(21))

    def get_coordinates(self, table_index):
        """Calculate table coordinates"""
        x = (table_index % 3) * 450 + 50
        y = (table_index // 3) * 400 + 50
        return float(x), float(y)

    def get_color(self, table_index):
        """Get table color"""
        return self.colors[table_index % len(self.colors)]

    def create_field(self, name, field_type, default="", primary=False,
                     unique=False, not_null=False, increment=False, comment=""):
        """Create field object"""
        return {
            "id": self.generate_id(),
            "name": name,
            "type": field_type,  # Complete type definition, e.g., "VARCHAR(100)"
            "default": str(default),  # Always a string
            "check": "",
            "primary": primary,
            "unique": unique,
            "notNull": not_null,
            "increment": increment,
            "comment": comment
        }

    def create_index(self, name, field_names, unique=False):
        """Create index object"""
        index = {
            "id": self.index_id_counter,
            "fields": field_names,  # Field name array, not IDs!
            "name": name,
            "unique": unique
        }
        self.index_id_counter += 1
        return index

    def create_table(self, table_index, name, comment, fields, indices=None):
        """Create table object"""
        table_id = self.generate_id()
        x, y = self.get_coordinates(table_index)
        color = self.get_color(table_index)

        # Create fields and record ID mapping
        field_objects = []
        field_map = {}
        for field_def in fields:
            field_obj = self.create_field(**field_def)
            field_objects.append(field_obj)
            field_map[field_obj["name"]] = field_obj["id"]

        # Record table info
        self.table_map[name] = {
            "id": table_id,
            "fields": field_map
        }

        # Create indexes
        index_objects = []
        if indices:
            for idx_def in indices:
                index_objects.append(self.create_index(**idx_def))

        return {
            "id": table_id,
            "name": name,
            "comment": comment,
            "color": color,
            "fields": field_objects,
            "indices": index_objects,
            "x": x,
            "y": y
        }

    def create_relationship(self, start_table, start_field,
                           end_table, end_field, cardinality="many_to_one"):
        """Create relationship object"""
        # Look up table and field IDs
        start_table_id = self.table_map[start_table]["id"]
        start_field_id = self.table_map[start_table]["fields"][start_field]
        end_table_id = self.table_map[end_table]["id"]
        end_field_id = self.table_map[end_table]["fields"][end_field]

        return {
            "name": "",
            "startTableId": start_table_id,
            "endTableId": end_table_id,
            "endFieldId": end_field_id,
            "startFieldId": start_field_id,
            "id": self.generate_id(),
            "updateConstraint": "No action",
            "deleteConstraint": "No action",
            "cardinality": cardinality
        }

    def generate(self, tables, relationships, title="Database"):
        """Generate complete DrawDB JSON"""
        table_objects = []
        for i, table_def in enumerate(tables):
            table_obj = self.create_table(i, **table_def)
            table_objects.append(table_obj)

        relationship_objects = []
        for rel_def in relationships:
            rel_obj = self.create_relationship(**rel_def)
            relationship_objects.append(rel_obj)

        return {
            "tables": table_objects,
            "relationships": relationship_objects,
            "notes": [],
            "subjectAreas": [],
            "database": "generic",
            "types": [],
            "title": title
        }


# Usage example
def example_usage():
    generator = DrawDBGenerator()

    # Define table structure
    tables = [
        {
            "name": "user_info",
            "comment": "User information table",
            "fields": [
                {
                    "name": "id",
                    "field_type": "BIGINT",
                    "primary": True,
                    "unique": True,
                    "not_null": True,
                    "increment": True,
                    "comment": "User ID"
                },
                {
                    "name": "username",
                    "field_type": "VARCHAR(50)",
                    "not_null": True,
                    "comment": "Username"
                },
                {
                    "name": "email",
                    "field_type": "VARCHAR(100)",
                    "unique": True,
                    "not_null": True,
                    "comment": "Email address"
                },
                {
                    "name": "created_at",
                    "field_type": "DATETIME",
                    "not_null": True,
                    "comment": "Creation time"
                }
            ],
            "indices": [
                {"name": "uk_email", "field_names": ["email"], "unique": True},
                {"name": "idx_username", "field_names": ["username"]}
            ]
        },
        {
            "name": "order_info",
            "comment": "Order information table",
            "fields": [
                {
                    "name": "id",
                    "field_type": "BIGINT",
                    "primary": True,
                    "unique": True,
                    "not_null": True,
                    "increment": True,
                    "comment": "Order ID"
                },
                {
                    "name": "user_id",
                    "field_type": "BIGINT",
                    "not_null": True,
                    "comment": "User ID"
                },
                {
                    "name": "order_no",
                    "field_type": "VARCHAR(50)",
                    "unique": True,
                    "not_null": True,
                    "comment": "Order number"
                },
                {
                    "name": "total_amount",
                    "field_type": "DECIMAL(10,2)",
                    "not_null": True,
                    "default": "0",
                    "comment": "Order total amount"
                }
            ],
            "indices": [
                {"name": "uk_order_no", "field_names": ["order_no"], "unique": True},
                {"name": "idx_user_id", "field_names": ["user_id"]}
            ]
        }
    ]

    # Define relationships
    relationships = [
        {
            "start_table": "order_info",
            "start_field": "user_id",
            "end_table": "user_info",
            "end_field": "id",
            "cardinality": "many_to_one"
        }
    ]

    # Generate JSON
    result = generator.generate(tables, relationships, "E-commerce System Database")

    # Output
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    example_usage()
```

---

## Type Conversion Reference

### SQL to DrawDB Type Field

| SQL Type | DrawDB type value |
|---------|-------------------|
| `BIGINT` | `"BIGINT"` |
| `INT` | `"INT"` |
| `TINYINT` | `"TINYINT"` |
| `TINYINT(1)` | `"TINYINT(1)"` |
| `VARCHAR(50)` | `"VARCHAR(50)"` |
| `TEXT` | `"TEXT"` |
| `LONGTEXT` | `"LONGTEXT"` |
| `DATETIME` | `"DATETIME"` |
| `TIMESTAMP` | `"TIMESTAMP"` |
| `DATE` | `"DATE"` |
| `DECIMAL(10,2)` | `"DECIMAL(10,2)"` |
| `BOOLEAN` | `"BOOLEAN"` |
| `ENUM('A','B')` | `"ENUM(A,B)"` |

### Notes

1. **Complete type string**: Type field must include complete type definition, including length and precision
2. **ENUM format**: ENUM type doesn't need quotes, separate values with commas directly
3. **Boolean type**: Can use `BOOLEAN` or `TINYINT(1)`
4. **Default values**: All default values are converted to string type

---

## Validation Checklist

Check before generating DrawDB JSON:

- [ ] All table IDs are 21-character random strings
- [ ] All field IDs are 21-character random strings
- [ ] All relationship IDs are 21-character random strings
- [ ] Index IDs use numeric increment (across all tables)
- [ ] type field contains complete type definition (e.g., `"VARCHAR(100)"`)
- [ ] No size field is used
- [ ] Index fields array uses field name strings
- [ ] default values are all string type
- [ ] Coordinates use floating-point numbers
- [ ] Table object field order: id, name, comment, color, fields, indices, x, y
- [ ] Relationship object field order is correct
- [ ] All comments display correctly

---

## Common Errors and Fixes

### Error 1: Using numeric IDs
```json
// Incorrect
{"id": 0}

// Correct
{"id": "_KV5MtPf2m4sI7Inu8pat"}
```

### Error 2: Separating type and size
```json
// Incorrect
{"type": "VARCHAR", "size": 100}

// Correct
{"type": "VARCHAR(100)"}
```

### Error 3: Index using field IDs
```json
// Incorrect
{"fields": [0, 1]}

// Correct
{"fields": ["email", "username"]}
```

### Error 4: Numeric default values
```json
// Incorrect
{"default": 0}

// Correct
{"default": "0"}
```

### Error 5: Integer coordinates
```json
// Not recommended
{"x": 100, "y": 200}

// Recommended
{"x": 100.0, "y": 200.0}
```
