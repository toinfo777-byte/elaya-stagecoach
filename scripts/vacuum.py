import sqlite3, os

db = "/data/elaya.db"  # тот же путь, что и в DB_URL

if os.path.exists(db):
    con = sqlite3.connect(db)
    con.execute("VACUUM")   # освобождает место, пересобирает файл
    con.close()
    print("vacuum done")
else:
    print("no db at", db)
