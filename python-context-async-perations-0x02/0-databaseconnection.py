import sqlite3

class DatabaseConnection:
    """Custom class-based context manager for DB connection"""
    def __enter__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        print("✅ Connection opened.")
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
            print("🔒 Connection closed.")

if __name__ == "__main__":
    with DatabaseConnection() as cursor:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        print("📊 Query result:", rows)
