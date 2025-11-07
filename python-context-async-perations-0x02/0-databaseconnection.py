import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        """Initialize the database name"""
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """Open the database connection"""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection"""
        if self.conn:
            self.conn.close()


# ✅ Example usage
if __name__ == "__main__":
    with DatabaseConnection('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(results)
