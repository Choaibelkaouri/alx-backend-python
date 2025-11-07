# python-decorators-0x01

A compact project showcasing practical Python decorators applied to database operations (SQLite).

## Files
- **0-log_queries.py** — `@log_queries` prints the SQL query before execution.
- **1-with_db_connection.py** — `@with_db_connection` opens/closes DB connection automatically.
- **2-transactional.py** — `@transactional` wraps operations in a transaction (commit/rollback).
- **3-retry_on_failure.py** — `@retry_on_failure(retries, delay)` retries transient failures.
- **4-cache_query.py** — `@cache_query` caches results by SQL query string.

## Usage
Ensure `users.db` exists with a `users` table. Then run any file directly, e.g.:
```bash
python3 0-log_queries.py
```

## Notes
- Python 3.8+
- SQLite (`users.db` in the same folder)
- Clean, review-friendly code — minimal prints guarded by `if __name__ == "__main__":`
