#!/usr/bin/env python3
"""
2-lazy_paginate.py
Simulates lazy loading paginated data from the `user_data` table
using a generator.

Requirements:
- Only ONE loop
- Must use yield
- Must include paginate_users(page_size, offset)
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetch one page of users from the user_data table.
    Args:
        page_size (int): number of rows per page
        offset (int): starting row index
    Returns:
        list[dict]: a list of rows as dictionaries
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily loads pages of users from the DB.
    Yields one page (list of dicts) at a time.

    Args:
        page_size (int): number of rows per page
    """
    offset = 0
    # Single loop as required
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
