import sqlite3
from crypto_utils.hash_utils import md5_hash
import os

DB_PATH = "database/app.db"

def init_db():
    # Buat folder 'database' jika belum ada
    os.makedirs("database", exist_ok=True)

    # Hubungkan ke database SQLite
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Buat tabel users kalau belum ada
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Cek apakah sudah ada user admin
    cur.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cur.fetchone():
        # Tambahkan akun default admin
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", md5_hash("admin123"))
        )
        print("[INFO] Akun admin dibuat (username='admin', password='admin123')")

    conn.commit()
    conn.close()
    print("[INFO] Database berhasil diinisialisasi di:", DB_PATH)


# Jalankan fungsi utama jika file ini dieksekusi langsung
if __name__ == "__main__":
    init_db()