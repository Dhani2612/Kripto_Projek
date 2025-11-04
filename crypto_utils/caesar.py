def caesar_encrypt(text: str, shift: int = 3) -> str:
    """
    Enkripsi teks dengan Caesar Cipher (geser huruf).
    """
    result = ""
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - start + shift) % 26 + start)
        else:
            result += char
    return result


def caesar_decrypt(cipher: str, shift: int = 3) -> str:
    """
    Dekripsi teks hasil Caesar Cipher.
    """
    return caesar_encrypt(cipher, -shift)


# Contoh uji manual
if __name__ == "__main__":
    plain = "Halo Dunia"
    cipher = caesar_encrypt(plain, 5)
    print("Cipher:", cipher)
    print("Decrypt:", caesar_decrypt(cipher, 5))