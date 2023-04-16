import sqlite3

conn = sqlite3.connect('blockchain.db')
c = conn.cursor()

c.execute('''CREATE TABLE blockchain
                (id_index INTEGER, timestamp TEXT, data TEXT, previous_hash TEXT, hash TEXT)''')


conn.commit()
conn.close()