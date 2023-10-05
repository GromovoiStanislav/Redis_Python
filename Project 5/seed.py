import sqlite3


conn = sqlite3.connect('database.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    age INTEGER
                )''')

cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('John Doe', 30))
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Jane Smith', 25))
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Bob Johnson', 35))


conn.commit()
conn.close()