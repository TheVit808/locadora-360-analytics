import sqlite3

conn = sqlite3.connect("./data/raw_sample/DB_LOCADORA.seed.db")
conn.execute("PRAGMA foreign_keys = ON;")

cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys;")
resultado = cursor.fetchone()[0]

print(f"Status do foreign_keys: {resultado}")  # Deve retornar 1
conn.close()