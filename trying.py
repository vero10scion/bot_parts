import sqlite3
connection = sqlite3.connect('sss.db')
cursor = connection.cursor()
cursor.execute('SELECT ur_name FROM comp WHERE ur_name LIKE "%МФК%"')
res = cursor.fetchone()
print(res)
