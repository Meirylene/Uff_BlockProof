import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO user (nome, email,telefone,senha) VALUES (?, ?, ?, ?)",
            ('Meiry', 'meiry@meiry.com', '1111111', 'abc')
            )

connection.commit()
connection.close()

