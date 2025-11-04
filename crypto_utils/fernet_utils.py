from cryptography.fernet import Fernet
import os

# Gunakan kunci statis dari hasil Step 1.3 (ganti sesuai milikmu)
FERNET_KEY = "bfnLw4j3NSFfHm9bqsOFA2J1VNIZTJGJYj-iqsaEN0I="

fernet = Fernet(FERNET_KEY)

def encrypt_file(input_path, output_path):
    """Enkripsi file menggunakan Fernet"""
    with open(input_path, 'rb') as f:
        data = f.read()
    encrypted_data = fernet.encrypt(data)
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)

def decrypt_file(input_path, output_path):
    """Dekripsi file menggunakan Fernet"""
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
