import os
from PIL import Image

def encode_message(image_path, message, output_path):
    """
    Sisipkan pesan teks ke dalam gambar (support jpg/png/bmp) menggunakan LSB
    """
    # Pastikan gambar dibuka dan diubah ke RGB
    img = Image.open(image_path).convert("RGB")

    # 🔄 Auto-convert ke PNG lossless (sementara)
    temp_png = "temp_steg.png"
    img.save(temp_png, format="PNG")
    img = Image.open(temp_png)

    encoded = img.copy()
    width, height = img.size
    message += "###"  # Penanda akhir pesan
    binary_message = ''.join(format(ord(c), '08b') for c in message)
    data_index = 0

    for y in range(height):
        for x in range(width):
            pixel = list(img.getpixel((x, y)))
            for n in range(3):
                if data_index < len(binary_message):
                    pixel[n] = pixel[n] & ~1 | int(binary_message[data_index])
                    data_index += 1
            encoded.putpixel((x, y), tuple(pixel))
            if data_index >= len(binary_message):
                # Simpan hasil encode (auto ubah ke PNG tapi ubah nama sesuai ekstensi asli)
                base, ext = os.path.splitext(output_path)
                final_output = base + ".png"
                encoded.save(final_output, format="PNG")
                os.remove(temp_png)  # hapus file sementara
                print(f"[DEBUG] Pesan disimpan di {final_output}")
                return final_output

    encoded.save(output_path, format="PNG")
    os.remove(temp_png)
    print("[WARNING] Pesan mungkin terlalu panjang untuk gambar ini!")
    return output_path


def decode_message(image_path):
    """
    Ambil pesan teks dari gambar (LSB)
    """
    # Konversi dulu ke PNG lossless agar bit tetap stabil
    img = Image.open(image_path).convert("RGB")
    temp_png = "temp_decode.png"
    img.save(temp_png, format="PNG")
    img = Image.open(temp_png)

    binary_data = ""
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            for n in range(3):
                binary_data += str(pixel[n] & 1)

    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_message = ""
    for char in chars:
        if len(char) < 8:
            continue
        decoded_message += chr(int(char, 2))
        if decoded_message.endswith("###"):
            os.remove(temp_png)
            print("[DEBUG] Pesan berhasil ditemukan!")
            return decoded_message[:-3]

    os.remove(temp_png)
    print("[ERROR] Pesan tidak ditemukan!")
    return ""