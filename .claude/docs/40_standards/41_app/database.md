# データベース設計標準（PostgreSQL / SQL Server）

## 基本方針

- **正規化（第3正規形まで）を基本とし、パフォーマンスが必要な場合のみ非正規化**
- **命名規則の統一**
- **インデックスの適切な設計**
- **制約（CONSTRAINT）の活用**
- **パーティショニング（大規模データの場合）**
- **セキュリティ（暗号化、最小権限の原則）**

---

## 命名規則

### テーブル名

```sql
-- ✅ Good: 複数形、スネークケース
users
orders
order_items
product_categories

-- ❌ Bad: 単数形、キャメルケース
User
OrderItem
productCategory
```

### カラム名

```sql
-- ✅ Good: スネークケース、意味が明確
id
user_id
email_address
created_at
updated_at
is_active
total_amount

-- ❌ Bad: キャメルケース、省略形
ID
userId
emailAddr
createdDate
active (boolean なのに is_ がない)
amt (何の金額か不明)
```

### 主キー・外部キー

```sql
-- ✅ Good: 主キーは id
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL
);

-- ✅ Good: 外部キーは {テーブル名}_id
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ❌ Bad: 主キーが user_id（わかりにくい）
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY
);
```

### インデックス名

```sql
-- ✅ Good: idx_{テーブル名}_{カラム名}
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ✅ Good: 複合インデックス
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at);
```

### 制約名

```sql
-- ✅ Good: わかりやすい制約名
ALTER TABLE users
  ADD CONSTRAINT uk_users_email UNIQUE (email);

ALTER TABLE orders
  ADD CONSTRAINT fk_orders_user_id FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE users
  ADD CONSTRAINT chk_users_age CHECK (age >= 0 AND age <= 150);
```

---

## データ型の選択

### PostgreSQL

```sql
-- ✅ Good: 適切なデータ型
CREATE TABLE users (
  id SERIAL PRIMARY KEY,                      -- 自動採番
  uuid UUID DEFAULT gen_random_uuid(),         -- UUID
  name VARCHAR(100) NOT NULL,                  -- 可変長文字列
  email VARCHAR(255) NOT NULL,
  age INTEGER,                                 -- 整数
  balance NUMERIC(10, 2),                      -- 金額（10桁、小数2桁）
  is_active BOOLEAN DEFAULT TRUE,              -- 真偽値
  birth_date DATE,                             -- 日付
  created_at TIMESTAMP NOT NULL DEFAULT NOW(), -- タイムスタンプ
  metadata JSONB                               -- JSON（インデックス可能）
);

-- ❌ Bad: 不適切なデータ型
CREATE TABLE users (
  id VARCHAR(50),                -- 数値なのに VARCHAR
  balance FLOAT,                 -- 金額に FLOAT（丸め誤差の危険）
  is_active VARCHAR(5),          -- TRUE/FALSE を文字列で保存
  created_at VARCHAR(50)         -- 日時を文字列で保存
);
```

### SQL Server

```sql
-- ✅ Good: 適切なデータ型
CREATE TABLE users (
  id INT IDENTITY(1,1) PRIMARY KEY,            -- 自動採番
  uuid UNIQUEIDENTIFIER DEFAULT NEWID(),       -- UUID
  name NVARCHAR(100) NOT NULL,                 -- Unicode 文字列
  email NVARCHAR(255) NOT NULL,
  age INT,
  balance DECIMAL(10, 2),                      -- 金額
  is_active BIT DEFAULT 1,                     -- 真偽値
  birth_date DATE,
  created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
  metadata NVARCHAR(MAX)                       -- JSON（SQL Server 2016+）
);
```

---

## テーブル設計

### 正規化（第3正規形）

```sql
-- ✅ Good: 正規化されたテーブル
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE addresses (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  zip_code VARCHAR(10),
  state VARCHAR(50),
  city VARCHAR(100),
  street VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ❌ Bad: 非正規化（住所が users テーブルに含まれる）
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  zip_code VARCHAR(10),
  state VARCHAR(50),
  city VARCHAR(100),
  street VARCHAR(255)
);
```

### 多対多リレーション（中間テーブル）

```sql
-- ✅ Good: 中間テーブルで多対多を表現
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL
);

CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE user_roles (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
```

### 監査カラム（Audit Columns）

```sql
-- ✅ Good: すべてのテーブルに監査カラムを追加
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,

  -- 監査カラム
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by INTEGER REFERENCES users(id),
  updated_by INTEGER REFERENCES users(id)
);

-- ✅ Good: 論理削除用カラム
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
```

### ソフトデリート（論理削除）

```sql
-- ✅ Good: 論理削除の実装
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  deleted_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- インデックス（削除されていないレコードのみ）
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;

-- ビューで論理削除されていないレコードのみ表示
CREATE VIEW active_users AS
SELECT * FROM users WHERE deleted_at IS NULL;
```

---

## インデックス設計

### 基本的なインデックス

```sql
-- ✅ Good: 頻繁に検索されるカラムにインデックス
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ✅ Good: UNIQUE インデックス
CREATE UNIQUE INDEX uk_users_email ON users(email);

-- ✅ Good: 複合インデックス（検索条件が複数の場合）
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at);

-- 使用例：このクエリは idx_orders_user_id_created_at を使用
SELECT * FROM orders
WHERE user_id = 123 AND created_at > '2024-01-01';
```

### 部分インデックス（Partial Index）

```sql
-- ✅ Good: 特定の条件のみにインデックス（PostgreSQL）
CREATE INDEX idx_orders_pending ON orders(created_at)
WHERE status = 'pending';

-- 使用例：このクエリは idx_orders_pending を使用
SELECT * FROM orders
WHERE status = 'pending' AND created_at > '2024-01-01';
```

### インデックスの注意点

```sql
-- ❌ Bad: 過剰なインデックス（INSERT/UPDATE が遅くなる）
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_age ON users(age);
CREATE INDEX idx_users_created_at ON users(created_at);
-- → 本当に必要なインデックスだけ作成する

-- ❌ Bad: カーディナリティが低いカラムへのインデックス
CREATE INDEX idx_users_is_active ON users(is_active);
-- → TRUE/FALSE の2値しかない場合、インデックスの効果は低い
-- → 部分インデックスを検討
```

---

## 制約（CONSTRAINT）

### NOT NULL 制約

```sql
-- ✅ Good: 必須カラムには NOT NULL
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  age INTEGER  -- NULL 許可（任意項目）
);
```

### UNIQUE 制約

```sql
-- ✅ Good: 重複を許さないカラムに UNIQUE
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE
);

-- ✅ Good: 複合 UNIQUE（複数カラムの組み合わせが一意）
CREATE TABLE user_roles (
  user_id INTEGER NOT NULL,
  role_id INTEGER NOT NULL,
  UNIQUE (user_id, role_id)
);
```

### CHECK 制約

```sql
-- ✅ Good: データの整合性をチェック
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  age INTEGER CHECK (age >= 0 AND age <= 150),
  email VARCHAR(255) CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  status VARCHAR(20) CHECK (status IN ('pending', 'processing', 'completed', 'cancelled')),
  total_amount NUMERIC(10, 2) CHECK (total_amount >= 0)
);
```

### 外部キー制約

```sql
-- ✅ Good: 外部キー制約で参照整合性を保証
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ON DELETE CASCADE: 親レコード削除時に子レコードも削除
-- ON DELETE RESTRICT: 親レコード削除を禁止（子レコードが存在する場合）
-- ON DELETE SET NULL: 親レコード削除時に外部キーを NULL に設定
```

---

## パフォーマンス最適化

### EXPLAIN でクエリ分析

```sql
-- ✅ Good: EXPLAIN で実行計画を確認
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123 AND created_at > '2024-01-01';

-- インデックスが使われているか確認
-- Seq Scan（シーケンシャルスキャン）→ インデックスが使われていない
-- Index Scan → インデックスが使われている
```

### ページング（LIMIT / OFFSET）

```sql
-- ✅ Good: LIMIT でページング
SELECT * FROM orders
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;  -- 1ページ目

-- ❌ Bad: OFFSET が大きい場合は遅い
SELECT * FROM orders
ORDER BY created_at DESC
LIMIT 20 OFFSET 100000;  -- 10万件スキップ → 遅い

-- ✅ Better: Keyset Pagination（カーソルベース）
SELECT * FROM orders
WHERE created_at < '2024-01-01 10:00:00'
ORDER BY created_at DESC
LIMIT 20;
```

### N+1 問題の回避

```sql
-- ❌ Bad: N+1 問題
-- 1. users を取得
SELECT * FROM users;

-- 2. 各 user に対して orders を取得（N回クエリ）
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM orders WHERE user_id = 2;
...

-- ✅ Good: JOIN で1クエリにまとめる
SELECT users.*, orders.*
FROM users
LEFT JOIN orders ON users.id = orders.user_id;
```

### パーティショニング（大規模データ）

```sql
-- ✅ Good: 日付でパーティション分割（PostgreSQL）
CREATE TABLE orders (
  id SERIAL,
  user_id INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL,
  total_amount NUMERIC(10, 2)
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_01 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- クエリは通常通り（自動的に適切なパーティションが選ばれる）
SELECT * FROM orders WHERE created_at > '2024-01-15';
```

---

## トランザクション

### ACID 特性の保証

```sql
-- ✅ Good: トランザクションで一貫性を保証
BEGIN;

INSERT INTO users (name, email) VALUES ('John', 'john@example.com');
INSERT INTO orders (user_id, total_amount) VALUES (LASTVAL(), 100.00);

COMMIT;

-- エラーが発生した場合はロールバック
BEGIN;

INSERT INTO users (name, email) VALUES ('Jane', 'jane@example.com');
-- エラー発生
ROLLBACK;
```

### 分離レベル

```sql
-- ✅ Good: 必要に応じて分離レベルを設定
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- デフォルト（PostgreSQL）

BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- より厳密な分離（ファントムリードを防ぐ）

BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- 最も厳密（完全な直列化）
```

---

## セキュリティ

### SQL インジェクション対策

```sql
-- ❌ Bad: 文字列連結（SQL インジェクションの危険）
query = "SELECT * FROM users WHERE email = '" + userInput + "'";

-- ✅ Good: プレースホルダ（パラメータ化クエリ）
-- PostgreSQL（pg ライブラリ）
const result = await pool.query('SELECT * FROM users WHERE email = $1', [userInput]);

-- SQL Server（mssql ライブラリ）
const result = await pool.request()
  .input('email', sql.VarChar, userInput)
  .query('SELECT * FROM users WHERE email = @email');
```

### 最小権限の原則

```sql
-- ✅ Good: アプリケーション用のユーザーを作成（最小権限）
CREATE USER app_user WITH PASSWORD 'secure_password';

-- 必要な権限のみ付与
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;

-- ❌ Bad: SUPERUSER 権限（すべての権限）を付与
GRANT ALL PRIVILEGES ON ALL TABLES TO app_user;
```

### 暗号化

```sql
-- ✅ Good: パスワードはハッシュ化して保存
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,  -- bcrypt でハッシュ化
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ❌ Bad: 平文でパスワードを保存
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255),
  password VARCHAR(255)  -- 平文（絶対NG）
);
```

### 機密データの暗号化（PostgreSQL）

```sql
-- ✅ Good: pgcrypto 拡張で暗号化
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  credit_card_encrypted BYTEA  -- 暗号化されたクレジットカード番号
);

-- 暗号化して挿入
INSERT INTO users (email, credit_card_encrypted)
VALUES ('john@example.com', pgp_sym_encrypt('1234-5678-9012-3456', 'encryption_key'));

-- 復号化して取得
SELECT email, pgp_sym_decrypt(credit_card_encrypted, 'encryption_key') AS credit_card
FROM users;
```

---

## バックアップ・リカバリ

### PostgreSQL

```bash
# フルバックアップ
pg_dump -U postgres -d mydb -F c -f mydb_backup.dump

# リストア
pg_restore -U postgres -d mydb -F c mydb_backup.dump

# 継続的アーカイビング（PITR: Point-In-Time Recovery）
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

### SQL Server

```sql
-- フルバックアップ
BACKUP DATABASE MyDB TO DISK = 'C:\Backup\MyDB.bak';

-- リストア
RESTORE DATABASE MyDB FROM DISK = 'C:\Backup\MyDB.bak';

-- トランザクションログバックアップ（PITR）
BACKUP LOG MyDB TO DISK = 'C:\Backup\MyDB_log.trn';
```

---

## マイグレーション管理

### 原則

- **前進のみ（Forward-Only）**: マイグレーションは前進のみ（ロールバックは避ける）
- **冪等性（Idempotent）**: 何度実行しても同じ結果
- **小さなステップ**: 1マイグレーション = 1変更

### マイグレーション例（Flyway / Liquibase スタイル）

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- V2__add_age_to_users.sql
ALTER TABLE users ADD COLUMN age INTEGER;

-- V3__create_orders_table.sql
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  total_amount NUMERIC(10, 2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### 本番環境でのマイグレーション（ゼロダウンタイム）

```sql
-- ❌ Bad: カラム削除（ダウンタイム発生）
ALTER TABLE users DROP COLUMN old_column;

-- ✅ Good: 段階的な削除
-- Step 1: アプリケーションコードから old_column の使用を削除
-- Step 2: デプロイ
-- Step 3: カラム削除
ALTER TABLE users DROP COLUMN old_column;
```

---

## ベストプラクティス

1. **正規化を基本とする**: 冗長性を排除、データの整合性を保つ
2. **適切なインデックスを作成**: 検索頻度の高いカラムにインデックス
3. **制約を活用**: NOT NULL、UNIQUE、CHECK、外部キーで整合性を保証
4. **監査カラムを必ず追加**: created_at、updated_at、created_by、updated_by
5. **論理削除を検討**: deleted_at カラムでソフトデリート
6. **トランザクションを使用**: 複数の操作をアトミックに実行
7. **セキュリティを意識**: SQL インジェクション対策、最小権限、暗号化
8. **バックアップを定期的に実行**: PITR（ポイントインタイムリカバリ）を設定
9. **EXPLAIN でクエリを分析**: パフォーマンスボトルネックを特定
10. **マイグレーション管理**: Flyway、Liquibase、Entity Framework Migrations 等を使用

---

**参照**: `.claude/docs/10_facilitation/2.3_設計フェーズ/2.3.6_データベース設計/`
