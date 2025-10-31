python-generators-0x00
#!/usr/bin/env python3
"""
Seed script for the ALX_prodev MySQL database.

Functions (as required by the spec):
- connect_db()                  : connects to the MySQL server (no DB selected)
- create_database(connection)   : creates ALX_prodev if it does not exist
- connect_to_prodev()           : connects to the ALX_prodev database
- create_table(connection)      : creates user_data table if it does not exist
- insert_data(connection, data) : inserts CSV rows into user_data (idempotent)

Environment variables (with sensible defaults):
- MYSQL_HOST (default: 'localhost')
- MYSQL_PORT (default: '3306')
- MYSQL_USER (default: 'root')
- MYSQL_PASSWORD (default: '')

CSV expected columns: user_id,name,email,age
"""

import csv
import os
import sys
from decimal import Decimal

try:
    import mysql.connector  # mysql-connector-python
except Exception as e:
    print("mysql-connector-python is required. Install with: pip install mysql-connector-python")
    raise e


DB_NAME = "ALX_prodev"
TABLE_NAME = "user_data"


def _get_mysql_config(include_database: bool = False):
    """Read connection settings from environment variables."""
    cfg = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "autocommit": True,
    }
    if include_database:
        cfg["database"] = DB_NAME
    return cfg


def connect_db():
    """
    Connects to the MySQL database server (no specific database selected).
    Returns:
        mysql.connector.connection.MySQLConnection | None
    """
    try:
        conn = mysql.connector.connect(**_get_mysql_config(include_database=False))
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    """
    if connection is None:
        print("No server connection provided to create_database().")
        return
    try:
        cur = connection.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        cur.close()
    except mysql.connector.Error as err:
        print(f"Error creating database {DB_NAME}: {err}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    Returns:
        mysql.connector.connection.MySQLConnection | None
    """
    try:
        conn = mysql.connector.connect(**_get_mysql_config(include_database=True))
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database {DB_NAME}: {err}")
        return None


def create_table(connection):
    """
    Creates the table user_data with the required fields if it does not exist.

    Schema:
      user_id CHAR(36) PRIMARY KEY, indexed
      name    VARCHAR(255) NOT NULL
      email   VARCHAR(255) NOT NULL
      age     DECIMAL(5,0) NOT NULL
    """
    if connection is None:
        print("No connection provided to create_table().")
        return

    create_stmt = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        user_id CHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(5,0) NOT NULL,
        PRIMARY KEY (user_id),
        INDEX idx_user_id (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        cur = connection.cursor()
        cur.execute(create_stmt)
        cur.close()
        # Match the sample output line exactly
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Error creating table {TABLE_NAME}: {err}")


def insert_data(connection, data):
    """
    Inserts data from CSV into the database if it does not exist.

    Args:
      connection: open MySQL connection to ALX_prodev
      data: path to CSV file (e.g., 'user_data.csv')

    Behavior:
      - Idempotent via PRIMARY KEY and INSERT IGNORE.
      - Expects headers: user_id,name,email,age
    """
    if connection is None:
        print("No connection provided to insert_data().")
        return

    if not os.path.exists(data):
        print(f"CSV file not found: {data}")
        return

    rows = []
    try:
        with open(data, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {"user_id", "name", "email", "age"}
            missing = required - set([h.strip() for h in reader.fieldnames or []])
            if missing:
                print(f"CSV is missing required columns: {', '.join(sorted(missing))}")
                return

            for r in reader:
                user_id = r["user_id"].strip()
                name = r["name"].strip()
                email = r["email"].strip()
                age_raw = r["age"].strip()

                # store as integer-like DECIMAL (5,0); accept int-like or decimal strings
                try:
                    # Normalize to an integer-like Decimal to satisfy DECIMAL(5,0)
                    age = int(Decimal(age_raw))
                except Exception:
                    print(f"Skipping row with invalid age '{age_raw}' for user_id {user_id}")
                    continue

                rows.append((user_id, name, email, age))
    except Exception as e:
        print(f"Error reading CSV '{data}': {e}")
        return

    if not rows:
        # Nothing to insert
        return

    insert_stmt = f"""
        INSERT IGNORE INTO {TABLE_NAME} (user_id, name, email, age)
        VALUES (%s, %s, %s, %s);
    """

    try:
        cur = connection.cursor()
        cur.executemany(insert_stmt, rows)
        cur.close()
    except mysql.connector.Error as err:
        print(f"Error inserting CSV rows: {err}")


# Optional: Make the module runnable for quick manual checks
if __name__ == "__main__":
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()
        conn = connect_to_prodev()
        if conn:
            create_table(conn)
            csv_path = sys.argv[1] if len(sys.argv) > 1 else "user_data.csv"
            insert_data(conn, csv_path)
            conn.close()
