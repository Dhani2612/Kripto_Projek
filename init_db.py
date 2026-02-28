import sqlite3
from crypto_utils.hash_utils import md5_hash
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "app.db")

def init_db():
    # Buat folder 'database' jika belum ada
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

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

    # Buat tabel encrypted_messages kalau belum ada
    cur.execute("""
        CREATE TABLE IF NOT EXISTS encrypted_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            plaintext TEXT,
            ciphertext TEXT,
            algorithm TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Cek apakah sudah ada user admin
    cur.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cur.fetchone():
        # Tambahkan akun default admin dengan hash yang aman
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", md5_hash("admin123")) # md5_hash skrg menggunakan werkzeug
        )
        print("[INFO] Akun admin dibuat (username='admin', password='admin123')")

    conn.commit()
    conn.close()
    print("[INFO] Database berhasil diinisialisasi di:", DB_PATH)


# Jalankan fungsi utama jika file ini dieksekusi langsung
if __name__ == "__main__":
    init_db()