"""
Upgrade an OLD database file in place (idempotent - safe to run repeatedly).

New databases never need this: ``create_app()`` creates every table and column.
It only adds columns that older versions of the app did not have:
    users.profile_picture   and   posts.video_url

Usage (from the backend folder):  python scripts/migrate_db.py
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'career_guidance.db')

MISSING_COLUMNS = [
    ('users', 'profile_picture', 'VARCHAR(500)'),
    ('posts', 'video_url', 'VARCHAR(1000)'),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        for table, column, ddl in MISSING_COLUMNS:
            existing = [row[1] for row in cursor.execute(f"PRAGMA table_info({table})")]
            if not existing:
                print(f"- table '{table}' does not exist yet, skipping")
            elif column in existing:
                print(f"✓ {table}.{column} already exists")
            else:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
                print(f"✓ added {table}.{column}")
        conn.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
