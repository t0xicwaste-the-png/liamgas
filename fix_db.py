from flask_app.app import app, db
from sqlalchemy import text

print("STARTING DATABASE FIX...")

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Force add the column. If it exists, Postgres will throw an error, which we catch.
            conn.execute(text('ALTER TABLE "user" ADD COLUMN profile_pic_url VARCHAR(500)'))
            conn.commit()
            print("SUCCESS: 'profile_pic_url' column added!")
    except Exception as e:
        print(f"NOTE: Column likely already exists or other error: {e}")

print("DATABASE FIX COMPLETE.")
