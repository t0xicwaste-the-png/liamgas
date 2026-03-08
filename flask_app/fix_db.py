import sqlite3

def add_admin_column():
    try:
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        # Check if column exists
        c.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in c.fetchall()]
        if 'is_admin' not in columns:
            print("Adding is_admin column to user table...")
            c.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
            print("Done.")
        else:
            print("Column is_admin already exists.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    add_admin_column()