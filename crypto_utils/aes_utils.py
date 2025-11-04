# crypto_utils/aes_utils.py

from Crypto.Cipher import AES
import base64
import os

# kunci AES 32-byte dari step 1.3
AES_MASTER_KEY = bytes.fromhex("8c2f87b4f644f0c0e2cd816acf535925268c9071f112fb72330ff07cdef8d2fa")

def pad(text):
    pad_len = 16 - (len(text) % 16)
    return text + chr(pad_len) * pad_len

def unpad(text):
    pad_len = ord(text[-1])
    return text[:-pad_len]

def aes_encrypt(plaintext):
    iv = os.urandom(16)
    cipher = AES.new(AES_MASTER_KEY, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext).encode())
    return base64.b64encode(iv + ciphertext).decode()

def aes_decrypt(ciphertext_b64):
    data = base64.b64decode(ciphertext_b64)
    iv = data[:16]
    cipher = AES.new(AES_MASTER_KEY, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(data[16:]).decode()
    return unpad(plaintext)