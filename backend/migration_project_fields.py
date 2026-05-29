"""Add project_number, commission_type, customer_name columns to projects table."""
import sqlite3

conn = sqlite3.connect("app.db")
cur = conn.cursor()

# Check if columns already exist
cur.execute("PRAGMA table_info(projects)")
cols = {row[1] for row in cur.fetchall()}

additions = [
    ("project_number", "VARCHAR(100) DEFAULT ''"),
    ("commission_type", "VARCHAR(100) DEFAULT ''"),
    ("customer_name", "VARCHAR(200) DEFAULT ''"),
]

for col_name, col_type in additions:
    if col_name not in cols:
        cur.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    else:
        print(f"Column already exists: {col_name}")

conn.commit()
conn.close()
print("Migration complete.")
