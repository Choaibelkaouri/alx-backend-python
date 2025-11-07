import sqlite3

class ExecuteQuery:
    """Reusable context manager for executing a query with parameters"""
    def __init__(self, query, params=None):
        self.query = query
        self.params = params or []
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        print("🔄 Connection established.")
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
            print("✅ Connection closed.")

if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    with ExecuteQuery(query, [25]) as result:
        print("📋 Query results:", result)
