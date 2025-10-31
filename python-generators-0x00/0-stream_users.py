#!/usr/bin/env python3
"""
0-stream_users.py
Generator that streams rows from the `user_data` table one by one.

Requirements:
- Use Python `yield` (generator)
- Only one loop
- Return each row as a dictionary
"""

import os
import mysql.connector


def stream_users():
    """
    Connects to the ALX_prodev database and yields rows one by one
    from the user_data table as dictionaries.

    Yields:
        dict: A single row with keys ('user_id', 'name', 'email', 'age')
    """
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": "ALX_prodev"
    }

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)  # Return rows as dicts

        cursor.execute("SELECT user_id, name, email, age FROM user_data;")

        # single loop with yield (generator)
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            cursor.close()
            connection.close()
        except Exception:
            pass
