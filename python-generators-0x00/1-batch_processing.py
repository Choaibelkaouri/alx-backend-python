#!/usr/bin/env python3
"""
1-batch_processing.py
Batch streaming & processing from the `user_data` table.

Prototypes:
- stream_users_in_batches(batch_size)
- batch_processing(batch_size)

Constraints:
- Use yield (generators)
- No more than 3 loops in total across the script
"""

import os
import mysql.connector


def _mysql_config(include_db: bool = True):
    cfg = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
    }
    if include_db:
        cfg["database"] = "ALX_prodev"
    return cfg


def stream_users_in_batches(batch_size):
    """
    Generator that yields lists (batches) of users from the DB.

    Each yielded item is a list[dict] with keys:
    ('user_id', 'name', 'email', 'age')

    Args:
        batch_size (int): number of rows per batch

    Yields:
        list[dict]: next batch of rows as dictionaries
    """
    if batch_size is None or int(batch_size) <= 0:
        raise ValueError("batch_size must be a positive integer")

    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**_mysql_config(include_db=True))
        cursor = connection.cursor(dictionary=True)

        # Deterministic order (by primary key)
        cursor.execute(
            "SELECT user_id, name, email, age FROM user_data ORDER BY user_id;"
        )

        # LOOP #1: fetch successive batches
        while True:
            batch = cursor.fetchmany(size=batch_size)
            if not batch:
                break
            yield batch

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if connection:
                connection.close()
        except Exception:
            pass


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25 and prints them.

    Args:
        batch_size (int): number of rows to fetch per batch
    """
    # LOOP #2: iterate over batches
    for batch in stream_users_in_batches(batch_size):
        # LOOP #3: iterate over users within a batch
        for user in batch:
            try:
                # Convert Decimal/int-like to int safely (cursor may return Decimal)
                age_val = int(user["age"])
            except Exception:
                continue

            if age_val > 25:
                print(user)
                # To mirror the sample output's blank line between rows:
                print()
