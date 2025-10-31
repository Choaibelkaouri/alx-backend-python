#!/usr/bin/env python3
"""
4-stream_ages.py
Memory-efficient aggregation using generators.

Objective:
    - Stream user ages one by one from the database
    - Compute the average age without loading all data into memory

Constraints:
    - Use yield (generator)
    - Use no more than two loops
    - Do NOT use SQL AVERAGE()
"""

import seed


def stream_user_ages():
    """
    Generator that yields user ages one by one from the user_data table.
    Yields:
        int: the age of a user
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data;")

    # LOOP #1: yield ages one by one
    for (age,) in cursor:
        yield int(age)

    cursor.close()
    connection.close()


def compute_average_age():
    """
    Computes and prints the average user age using the generator stream_user_ages.
    Uses no more than one additional loop.
    """
    total = 0
    count = 0

    # LOOP #2: iterate through generator only once
    for age in stream_user_ages():
        total += age
        count += 1

    if count == 0:
        print("Average age of users: 0")
    else:
        average = total / count
        print(f"Average age of users: {average:.2f}")


# Entry point for direct execution
if __name__ == "__main__":
    compute_average_age()
