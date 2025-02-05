import sqlite3

conn = sqlite3.connect('flex_app.db')
cursor = conn.cursor()

# You must match the actual table name. By default with Flask-SQLAlchemy, 
# the table is likely named 'user' or 'User'. 
# Check exactly how it's named in your DB if this fails.

cursor.execute("SELECT id, email, password FROM user")  
rows = cursor.fetchall()
conn.close()

print("Users found in the database:")
for row in rows:
    print(row)
