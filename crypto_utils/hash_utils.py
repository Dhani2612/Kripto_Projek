import hashlib

def md5_hash(password: str) -> str:
    """
    Mengubah string password menjadi hash MD5 hex.
    """
    return hashlib.md5(password.encode()).hexdigest()

def verify_md5(password: str, hashed: str) -> bool:
    """
    Mengecek apakah password cocok dengan hash MD5 yang tersimpan.
    """
    return md5_hash(password) == hashed

# Contoh uji manual
if __name__ == "__main__":
    pw = "admin123"
    hashed = md5_hash(pw)
    print("MD5 Hash:", hashed)
    print("Verifikasi:", verify_md5(pw, hashed))