import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect("hiresmart.db")

# Create a cursor
cursor = conn.cursor()

# Create the users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mobile TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Save changes
conn.commit()

# Close the connection
conn.close()

print("Database and users table created successfully!")