import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

sql = "SELECT * FROM users"
res = cursor.execute(sql)
user = res.fetchone()

a = 0

