#!/usr/bin/env python3
"""
RDS Database Initialization Script
Purpose: Execute init.sql on AWS RDS PostgreSQL instance
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Database connection details
DB_CONFIG = {
    "host": "xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com",
    "port": 5432,
    "user": "postgres",
    "password": "r6wDM7nYOPyWBCkax0rRa4sQ4U4HXelJ",
    "database": "postgres"
}

async def execute_init_sql():
    """Execute init.sql on RDS database"""

    # Read init.sql file
    init_sql_path = Path(__file__).parent / "init.sql"
    print(f"Reading SQL file: {init_sql_path}")

    with open(init_sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print(f"SQL content loaded ({len(sql_content)} characters)")

    # Connect to database
    print(f"\nConnecting to RDS: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

    try:
        conn = await asyncpg.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        print("✓ Connection established")

        # Execute SQL statements
        print("\nExecuting SQL statements...")

        # Split SQL by semicolons and execute each statement
        statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]

        for i, statement in enumerate(statements, 1):
            # Skip comment-only statements
            if all(line.strip().startswith("--") or not line.strip() for line in statement.split("\n")):
                continue

            print(f"\n[{i}/{len(statements)}] Executing statement:")
            print(f"  {statement[:100]}..." if len(statement) > 100 else f"  {statement}")

            try:
                result = await conn.fetch(statement)
                if result:
                    print(f"  ✓ Result: {result}")
                else:
                    print(f"  ✓ Executed successfully")
            except Exception as e:
                print(f"  ⚠ Warning: {e}")

        # Verify table creation
        print("\n" + "="*60)
        print("Verification:")
        print("="*60)

        # Check if tasks table exists
        table_check = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'tasks'
            )
            """
        )

        if table_check:
            print("✓ tasks table exists")

            # Get table structure
            columns = await conn.fetch(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                ORDER BY ordinal_position
                """
            )

            print("\nTable structure:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")

            # Get indexes
            indexes = await conn.fetch(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'tasks'
                """
            )

            print(f"\nIndexes ({len(indexes)}):")
            for idx in indexes:
                print(f"  - {idx['indexname']}")

            # Get row count
            row_count = await conn.fetchval("SELECT COUNT(*) FROM tasks")
            print(f"\nRow count: {row_count}")

            if row_count > 0:
                # Show sample data
                sample_rows = await conn.fetch("SELECT id, title, status FROM tasks LIMIT 5")
                print("\nSample data:")
                for row in sample_rows:
                    print(f"  - {row['title']} ({row['status']})")
        else:
            print("✗ tasks table does NOT exist")
            return False

        # Close connection
        await conn.close()
        print("\n✓ Connection closed")

        print("\n" + "="*60)
        print("Database initialization completed successfully!")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(execute_init_sql())
    sys.exit(0 if success else 1)
