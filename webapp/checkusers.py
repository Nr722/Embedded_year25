import sqlite3

conn = sqlite3.connect('flex_app.db')
cursor = conn.cursor()



cursor.execute("SELECT id, email, password FROM user")  
rows = cursor.fetchall()
conn.close()

print("Users found in the database:")
for row in rows:
    print(row)
