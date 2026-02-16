# Database Design Examples

## Example 1: E-commerce System Core Tables

### Requirements Description
Design a core database for an e-commerce system, including user, product, and order functionality.

### Table Structure Design

#### 1. User Table (user_info)
```sql
CREATE TABLE `user_info` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  `username` VARCHAR(50) NOT NULL COMMENT 'Username',
  `password` VARCHAR(255) NOT NULL COMMENT 'Password (encrypted)',
  `email` VARCHAR(100) NOT NULL COMMENT 'Email address',
  `phone` VARCHAR(20) NOT NULL COMMENT 'Phone number',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT 'Account status: 0-Disabled, 1-Active, 2-Frozen',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_email` (`email`),
  UNIQUE KEY `uk_phone` (`phone`),
  KEY `idx_username` (`username`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User information table';
```

#### 2. Product Table (product_info)
```sql
CREATE TABLE `product_info` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Product ID',
  `product_code` VARCHAR(50) NOT NULL COMMENT 'Product code',
  `product_name` VARCHAR(200) NOT NULL COMMENT 'Product name',
  `category_id` BIGINT NOT NULL COMMENT 'Category ID',
  `price` DECIMAL(10,2) NOT NULL COMMENT 'Product price',
  `stock` INT NOT NULL DEFAULT 0 COMMENT 'Stock quantity',
  `description` TEXT COMMENT 'Product description',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT 'Product status: 0-Inactive, 1-Active, 2-Sold out',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_product_code` (`product_code`),
  KEY `idx_category_id` (`category_id`),
  KEY `idx_product_name` (`product_name`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Product information table';
```

#### 3. Order Table (order_info)
```sql
CREATE TABLE `order_info` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Order ID',
  `order_no` VARCHAR(50) NOT NULL COMMENT 'Order number',
  `user_id` BIGINT NOT NULL COMMENT 'User ID',
  `total_amount` DECIMAL(10,2) NOT NULL COMMENT 'Order total amount',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT 'Order status: 0-Pending payment, 1-Paid, 2-Shipped, 3-Completed, 4-Cancelled',
  `pay_time` DATETIME COMMENT 'Payment time',
  `ship_time` DATETIME COMMENT 'Shipping time',
  `complete_time` DATETIME COMMENT 'Completion time',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Order information table';
```

#### 4. Order Detail Table (order_detail)
```sql
CREATE TABLE `order_detail` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Detail ID',
  `order_id` BIGINT NOT NULL COMMENT 'Order ID',
  `product_id` BIGINT NOT NULL COMMENT 'Product ID',
  `product_name` VARCHAR(200) NOT NULL COMMENT 'Product name (snapshot)',
  `price` DECIMAL(10,2) NOT NULL COMMENT 'Unit price (snapshot)',
  `quantity` INT NOT NULL COMMENT 'Purchase quantity',
  `subtotal` DECIMAL(10,2) NOT NULL COMMENT 'Subtotal amount',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Order detail table';
```

### Table Relationships
- user_info (1) → order_info (N): One user can have multiple orders
- order_info (1) → order_detail (N): One order contains multiple product details
- product_info (1) → order_detail (N): One product can appear in multiple orders

---

## Example 2: Blog System

### Requirements Description
Design a simple blog system supporting user article publishing, comments, and tagging functionality.

### Table Structure Design

#### 1. Article Table (article)
```sql
CREATE TABLE `article` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Article ID',
  `user_id` BIGINT NOT NULL COMMENT 'Author ID',
  `title` VARCHAR(200) NOT NULL COMMENT 'Article title',
  `summary` VARCHAR(500) COMMENT 'Article summary',
  `content` LONGTEXT NOT NULL COMMENT 'Article content',
  `view_count` INT NOT NULL DEFAULT 0 COMMENT 'View count',
  `like_count` INT NOT NULL DEFAULT 0 COMMENT 'Like count',
  `comment_count` INT NOT NULL DEFAULT 0 COMMENT 'Comment count',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT 'Publish status: 0-Draft, 1-Published, 2-Offline',
  `publish_time` DATETIME COMMENT 'Publish time',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_publish_time` (`publish_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Article table';
```

#### 2. Comment Table (comment)
```sql
CREATE TABLE `comment` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Comment ID',
  `article_id` BIGINT NOT NULL COMMENT 'Article ID',
  `user_id` BIGINT NOT NULL COMMENT 'Commenter user ID',
  `parent_id` BIGINT DEFAULT 0 COMMENT 'Parent comment ID: 0 means top-level comment',
  `content` TEXT NOT NULL COMMENT 'Comment content',
  `like_count` INT NOT NULL DEFAULT 0 COMMENT 'Like count',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT 'Comment status: 0-Deleted, 1-Normal, 2-Hidden',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
  PRIMARY KEY (`id`),
  KEY `idx_article_id` (`article_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Comment table';
```

#### 3. Tag Table (tag)
```sql
CREATE TABLE `tag` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Tag ID',
  `tag_name` VARCHAR(50) NOT NULL COMMENT 'Tag name',
  `use_count` INT NOT NULL DEFAULT 0 COMMENT 'Usage count',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tag_name` (`tag_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Tag table';
```

#### 4. Article-Tag Association Table (article_tag)
```sql
CREATE TABLE `article_tag` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Association ID',
  `article_id` BIGINT NOT NULL COMMENT 'Article ID',
  `tag_id` BIGINT NOT NULL COMMENT 'Tag ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  PRIMARY KEY (`id`),
  KEY `idx_article_id` (`article_id`),
  KEY `idx_tag_id` (`tag_id`),
  UNIQUE KEY `uk_article_tag` (`article_id`, `tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Article-tag association table';
```

### Table Relationships
- user_info (1) → article (N): One user can write multiple articles
- article (1) → comment (N): One article can have multiple comments
- user_info (1) → comment (N): One user can make multiple comments
- article (N) ↔ tag (N): Articles and tags have a many-to-many relationship, connected via article_tag junction table

---

## Index Design Guidelines

### When Indexes Are Needed

1. **WHERE Condition Fields**
   - Example: `WHERE user_id = ?` → needs `idx_user_id`
   - Example: `WHERE status = ? AND created_at > ?` → needs composite index `idx_status_created_at`

2. **JOIN Association Fields**
   - Example: `JOIN order_info ON order_detail.order_id = order_info.id` → needs `idx_order_id`

3. **ORDER BY / GROUP BY Fields**
   - Example: `ORDER BY created_at DESC` → needs `idx_created_at`
   - Example: `GROUP BY category_id` → needs `idx_category_id`

4. **Uniqueness Constraint Fields**
   - Example: email, phone, order_no, etc. → use UNIQUE indexes

### When Indexes Are Not Needed

1. **Low-cardinality Fields**
   - Gender (only 2-3 values)
   - Simple status codes (only 0/1)
   - Boolean fields (is_deleted, etc.)

2. **Frequently Updated Fields**
   - view_count (view count)
   - like_count (like count)
   - Frequent updates reduce index efficiency

3. **Small Tables**
   - Tables with very few records (a few hundred or less) don't need many indexes
   - Full table scan may be faster than index lookup

### Composite Index Design

Follow the **leftmost prefix rule**:
```sql
-- Create composite index
KEY `idx_status_created_at` (`status`, `created_at`)

-- Queries that can use the index
WHERE status = ? AND created_at > ?  -- Uses full index
WHERE status = ?                      -- Uses leftmost column

-- Queries that cannot use the index
WHERE created_at > ?                  -- Doesn't satisfy leftmost prefix
```

---

## Field Design Considerations

### 1. Snapshot Fields
In orders and transactions, save snapshot data at the time of the transaction:
```sql
-- In order_detail table
product_name VARCHAR(200)  -- Product name snapshot (product may be renamed)
price DECIMAL(10,2)        -- Price snapshot (product may have price changes)
```

### 2. Counter Fields
For performance, some counts can be stored redundantly:
```sql
-- In article table
view_count INT DEFAULT 0      -- View count
like_count INT DEFAULT 0      -- Like count
comment_count INT DEFAULT 0   -- Comment count
```

### 3. Hierarchical Structure
Use parent_id to implement tree structures:
```sql
-- In comment table
parent_id BIGINT DEFAULT 0  -- 0 means top-level comment, non-0 means reply to a comment
```

### 4. Soft Delete
Use is_deleted to implement soft delete:
```sql
is_deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is deleted: 0-No, 1-Yes'
-- Queries need to add condition: WHERE is_deleted = 0
```

### 5. Status Transitions
Design reasonable status codes:
```sql
-- Order status
status TINYINT COMMENT '0-Pending payment, 1-Paid, 2-Shipped, 3-Completed, 4-Cancelled'
-- Status transitions: 0 → 1 → 2 → 3 or 0 → 4
```
