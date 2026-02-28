from werkzeug.security import generate_password_hash, check_password_hash

def md5_hash(password: str) -> str:
    """
    Mengubah string password menjadi hash yang aman menggunakan werkzeug.security.
    Nama fungsi tetap md5_hash untuk kompatibilitas, meskipun algoritma di baliknya telah diperbarui ke PBKDF2:sha256.
    """
    return generate_password_hash(password)

def verify_md5(password: str, hashed: str) -> bool:
    """
    Mengecek apakah password cocok dengan hash yang tersimpan.
    """
    return check_password_hash(hashed, password)

# Contoh uji manual
if __name__ == "__main__":
    pw = "admin123"
    hashed = md5_hash(pw)
    print("Secure Hash:", hashed)
    print("Verifikasi:", verify_md5(pw, hashed))