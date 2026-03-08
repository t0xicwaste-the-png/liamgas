import sqlite3
import sys

def make_admin(username):
    try:
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("UPDATE user SET is_admin = 1 WHERE username = ?", (username,))
        if c.rowcount > 0:
            print(f"User '{username}' is now an admin.")
            conn.commit()
        else:
            print(f"User '{username}' not found.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <username>")
    else:
        make_admin(sys.argv[1])