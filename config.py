from dotenv import load_dotenv
import os

# Load environment variables dari file .env
load_dotenv()

# Konfigurasi kunci & pengaturan dasar
SECRET_KEY = os.getenv("SECRET_KEY", "devsecret")
AES_MASTER_KEY = bytes.fromhex(os.getenv("AES_MASTER_KEY", "00"*32))
FERNET_KEY = os.getenv("FERNET_KEY").encode()
DATABASE_PATH = "database/app.db"

# Fungsi bantu untuk debug
if __name__ == "__main__":
    print("SECRET_KEY:", SECRET_KEY[:10], "...")
    print("AES_MASTER_KEY (len):", len(AES_MASTER_KEY))
    print("FERNET_KEY (len):", len(FERNET_KEY))
