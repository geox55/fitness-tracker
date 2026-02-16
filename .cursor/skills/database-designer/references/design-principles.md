# Database Design Principles

## Core Design Principles

### 1. No Physical Foreign Keys
- **Maintain relationships only at the logical level**, do not create FOREIGN KEY constraints
- Relationships are expressed through naming conventions: `user_id`, `order_id`, etc.
- Clearly document logical relationships between tables in documentation and ER diagrams
- Rationale: Avoid table locking, improve flexibility, facilitate database sharding

### 2. Realistic Field Sizes
Design field sizes based on actual business scenarios to avoid wasting storage space.

#### Common Field Size Standards

**User-related:**
- `username`: VARCHAR(50) - Username
- `real_name`: VARCHAR(50) - Real name
- `nickname`: VARCHAR(50) - Nickname
- `email`: VARCHAR(100) - Email address
- `phone`: VARCHAR(20) - Phone number (including international codes)
- `password`: VARCHAR(255) - Password hash
- `id_card`: VARCHAR(18) - ID card number

**Business data:**
- `title`: VARCHAR(200) - Title (articles, products, etc.)
- `subtitle`: VARCHAR(100) - Subtitle
- `code/number`: VARCHAR(50) - Order number, product code, etc.
- `url`: VARCHAR(500) - URL
- `address`: VARCHAR(255) - Address
- `description`: TEXT - Detailed description
- `content`: TEXT or LONGTEXT - Body content
- `remark/notes`: VARCHAR(500) - Remarks

**Amounts and numbers:**
- `price/amount`: DECIMAL(10,2) - Amount (max 99999999.99)
- `quantity`: INT - Quantity
- `percentage`: DECIMAL(5,2) - Percentage (0.00-100.00)
- `rating`: DECIMAL(3,1) - Rating (0.0-10.0)

**Status and types:**
- `status`: TINYINT - Status code (0-255)
- `type`: TINYINT - Type code
- `is_xxx`: TINYINT(1) - Boolean flag (0/1)
- `gender`: TINYINT - Gender (0/1/2)

**Time-related:**
- `created_at`: DATETIME - Creation time
- `updated_at`: DATETIME - Update time
- `deleted_at`: DATETIME - Deletion time (soft delete)
- `expire_at`: DATETIME - Expiration time

### 3. Minimal Index Strategy
Only create indexes that are essential for business operations to avoid excessive indexing that consumes storage and affects write performance.

#### Index Creation Rules

**Scenarios requiring indexes:**
1. Fields frequently used in WHERE conditions
2. Fields used in JOIN operations
3. Fields used in ORDER BY / GROUP BY
4. Fields requiring uniqueness constraints (email, phone, etc.) use UNIQUE indexes

**Index naming conventions:**
- Regular index: `idx_table_field` or `idx_field`
- Unique index: `uk_table_field` or `uk_field`
- Composite index: `idx_table_field1_field2` or `idx_field1_field2`

**Index design recommendations:**
- Generally no more than 5 indexes per table
- Composite indexes follow the leftmost prefix rule
- Low-cardinality fields (like gender, status) generally don't need indexes
- Consider using prefix indexes for VARCHAR fields

### 4. Mandatory Comments
- Every table must have a COMMENT explaining its purpose
- Every field must have a COMMENT explaining its meaning
- Comments should be clear and accurate

**Example:**
```sql
CREATE TABLE `user_info` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  `username` VARCHAR(50) NOT NULL COMMENT 'Username',
  `email` VARCHAR(100) NOT NULL COMMENT 'Email address',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User information table';
```

### 5. Basic Table Structure Focus
- Design only basic table structures and key indexes by default
- Unless explicitly requested, do not include:
  - Partition strategies
  - Read-write separation
  - Caching strategies
  - Performance tuning parameters

## Default System Fields

### Standard System Fields (Added by Default)
Unless explicitly specified otherwise, every table should include:

```sql
`id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Primary key ID',
`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
`is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
PRIMARY KEY (`id`)
```

### Optional System Fields
May be needed based on business requirements:
- `creator_id` BIGINT - Creator ID
- `updater_id` BIGINT - Updater ID
- `deleted_at` DATETIME - Deletion time
- `version` INT - Optimistic lock version number
- `tenant_id` BIGINT - Tenant ID (multi-tenant scenarios)

### Disabling System Fields
If the user explicitly states "no system fields" or "only need id", create only the minimal structure.

## Naming Conventions

### Table Naming
- Use `snake_case`
- Lowercase letters and underscores
- Names should have business meaning
- Examples: `user_info`, `order_detail`, `product_category`

### Field Naming
- Use `snake_case`
- Lowercase letters and underscores
- Boolean types use `is_xxx` prefix
- Foreign key fields use `xxx_id` suffix
- Examples: `user_name`, `is_active`, `order_id`

### Index Naming
- Regular index: `idx_field` or `idx_table_field`
- Unique index: `uk_field` or `uk_table_field`
- Composite index: `idx_field1_field2`
- Examples: `idx_username`, `uk_email`, `idx_user_id_created_at`

## Database Dialects

### Default: MySQL 8.0
If the user doesn't specify a database type, default to MySQL 8.0, including:
- Engine: InnoDB
- Character set: utf8mb4
- Collation: utf8mb4_general_ci
- AUTO_INCREMENT primary key
- DATETIME type for time fields

### Other Supported Databases
Generate corresponding syntax based on user specification:
- PostgreSQL: Use SERIAL, TIMESTAMP, TEXT, etc.
- SQL Server: Use IDENTITY, DATETIME2, NVARCHAR, etc.
- Oracle: Use SEQUENCE, DATE, VARCHAR2, etc.

## Table Relationship Handling

### Logical Relationship Documentation
Although physical foreign keys are not created, logical relationships between tables must be clearly documented:

**One-to-Many (1:N):**
- Example: One user has multiple orders
- Add foreign key field on the "many" side: `user_id`
- Marked as many-to-one in ER diagrams

**Many-to-Many (N:N):**
- Example: Student-course enrollment relationship
- Create junction table: `student_course`
- Junction table contains two foreign keys: `student_id`, `course_id`
- Marked as two many-to-one relationships in ER diagrams

**One-to-One (1:1):**
- Example: User and user details
- Add foreign key field with unique index on either side
- Marked as one-to-one in ER diagrams

## AI Inference Strategy

### Inferring Business Details
When user requirements are not detailed enough, AI should:
1. Infer reasonable fields based on common business scenarios
2. Choose appropriate data types and sizes for fields
3. Add necessary constraints (NOT NULL, DEFAULT, etc.)
4. Add auxiliary fields needed for business logic

**Example:**
User says "design a user table", AI should infer:
- Basic fields: username, password, email, phone
- Status field: status (account status)
- Optional fields: avatar (avatar URL), gender

### Inferring Index Strategy
Infer indexes based on business scenarios:
1. Login scenarios: username, email, phone need indexes
2. Query scenarios: status, type and other filter fields need indexes
3. Association scenarios: all xxx_id foreign key fields need indexes
4. Uniqueness: email, phone, etc. use UNIQUE indexes

### Inferring Table Relationships
Infer table relationships based on field naming and business logic:
- Fields named `xxx_id` are inferred as foreign key relationships
- Determine relationship type (1:1, 1:N, N:N) based on business meaning
- Automatically create junction tables for many-to-many relationships

## Quality Checklist

After completing the design, verify:
- [ ] All tables have COMMENT
- [ ] All fields have COMMENT
- [ ] Field sizes match actual business scenarios
- [ ] Index count is reasonable (≤5 per table)
- [ ] No physical foreign key constraints created
- [ ] System fields correctly added (unless explicitly not needed)
- [ ] Names follow snake_case convention
- [ ] Logical relationships clearly documented
- [ ] SQL syntax matches target database dialect
