#!/usr/bin/env python3
"""
RDS Database Initialization Script (psycopg2 version)
Purpose: Execute init.sql on AWS RDS PostgreSQL instance
"""

import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("Error: psycopg2 is not installed.")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)

# Database connection details
DB_CONFIG = {
    "host": "xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com",
    "port": 5432,
    "user": "postgres",
    "password": "r6wDM7nYOPyWBCkax0rRa4sQ4U4HXelJ",
    "database": "postgres"
}

def execute_init_sql():
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
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("✓ Connection established")

        # Execute SQL statements
        print("\nExecuting SQL statements...")

        # Execute the entire SQL file
        try:
            cursor.execute(sql_content)
            print("✓ SQL executed successfully")
        except Exception as e:
            print(f"⚠ Warning during execution: {e}")

        # Verify table creation
        print("\n" + "="*60)
        print("Verification:")
        print("="*60)

        # Check if tasks table exists
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'tasks'
            )
            """
        )
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("✓ tasks table exists")

            # Get table structure
            cursor.execute(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                ORDER BY ordinal_position
                """
            )
            columns = cursor.fetchall()

            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")

            # Get indexes
            cursor.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'tasks'
                """
            )
            indexes = cursor.fetchall()

            print(f"\nIndexes ({len(indexes)}):")
            for idx in indexes:
                print(f"  - {idx[0]}")

            # Get row count
            cursor.execute("SELECT COUNT(*) FROM tasks")
            row_count = cursor.fetchone()[0]
            print(f"\nRow count: {row_count}")

            if row_count > 0:
                # Show sample data
                cursor.execute("SELECT id, title, status FROM tasks LIMIT 5")
                sample_rows = cursor.fetchall()
                print("\nSample data:")
                for row in sample_rows:
                    print(f"  - {row[1]} ({row[2]})")
        else:
            print("✗ tasks table does NOT exist")
            cursor.close()
            conn.close()
            return False

        # Close connection
        cursor.close()
        conn.close()
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
    success = execute_init_sql()
    sys.exit(0 if success else 1)
