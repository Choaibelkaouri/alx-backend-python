# python-context-async-operations-0x02

This project demonstrates **context managers and asynchronous programming** in Python for managing SQLite database connections.

## Tasks
- **0-databaseconnection.py** – Class-based context manager that opens/closes DB connections.
- **1-execute.py** – Reusable query manager executing parameterized SQL safely.

## Usage
```bash
python3 0-databaseconnection.py
python3 1-execute.py
```

Ensure a `users.db` file exists with a `users` table.

## Requirements
- Python 3.8+
- SQLite3
