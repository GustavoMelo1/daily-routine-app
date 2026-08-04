import sqlite3
import os

path = os.path.dirname(__file__)
db_path = os.path.join(path, "rotina.db")
schema_path = os.path.join(path, "schema.sql")

con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

with open(schema_path, "r") as f:
    schema_sql = f.read()

cur.executescript(schema_sql)
con.commit()
con.close()