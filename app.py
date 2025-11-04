from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

# ===== Import modul kriptografi =====
from crypto_utils.hash_utils import md5_hash
from crypto_utils.caesar import caesar_encrypt, caesar_decrypt
from crypto_utils.aes_utils import aes_encrypt, aes_decrypt
from crypto_utils.fernet_utils import encrypt_file, decrypt_file
from crypto_utils.steganografi import encode_message, decode_message

# ===== Konfigurasi dasar aplikasi =====
app = Flask(__name__)
app.secret_key = "supersecretkey"  # ubah di produksi
DB_PATH = "database/app.db"

UPLOAD_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted"
ALLOWED_EXTENSIONS = {"txt", "pdf", "jpg", "jpeg", "png", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ENCRYPTED_FOLDER"] = ENCRYPTED_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

# ======================================================
# Fungsi bantu koneksi DB
# ======================================================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ======================================================
# ROUTE: REGISTER
# ======================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        existing_user = conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()

        if existing_user:
            flash("❌ Username sudah digunakan!", "danger")
        else:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, md5_hash(password))
            )
            conn.commit()
            conn.close()
            flash("✅ Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for("login"))

        conn.close()

    return render_template("register.html")


# ======================================================
# ROUTE: LOGIN
# ======================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, md5_hash(password))
        ).fetchone()
        conn.close()

        if user:
            session["username"] = username
            flash("✅ Login berhasil!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Username atau password salah.", "danger")

    return render_template("login.html")


# ======================================================
# ROUTE: DASHBOARD
# ======================================================
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])


# ======================================================
# ROUTE: ENKRIPSI & DEKRIPSI TEKS (CAESAR + AES)
# ======================================================
@app.route("/encrypt_text", methods=["GET", "POST"])
def encrypt_text():
    if "username" not in session:
        return redirect(url_for("login"))

    encrypted_text = None
    decrypted_text = None

    if request.method == "POST":
        conn = get_db_connection()
        username = session["username"]

        # Enkripsi teks
        if "text" in request.form:
            text = request.form["text"]
            shift = int(request.form["shift"])
            caesar_result = caesar_encrypt(text, shift)
            encrypted_text = aes_encrypt(caesar_result)

            # Simpan riwayat
            conn.execute("""
                INSERT INTO encrypted_messages (username, plaintext, ciphertext, algorithm)
                VALUES (?, ?, ?, ?)
            """, (username, text, encrypted_text, "Caesar + AES"))
            conn.commit()

        # Dekripsi teks
        elif "ciphertext" in request.form:
            ciphertext = request.form["ciphertext"]
            shift = int(request.form["shift"])
            try:
                aes_result = aes_decrypt(ciphertext)
                decrypted_text = caesar_decrypt(aes_result, shift)
            except Exception as e:
                decrypted_text = f"Error saat dekripsi: {e}"

        conn.close()

    return render_template("encrypt_text.html",
                           username=session["username"],
                           encrypted_text=encrypted_text,
                           decrypted_text=decrypted_text)


# ======================================================
# ROUTE: HISTORY
# ======================================================
@app.route("/history")
def history():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    data = conn.execute("""
        SELECT plaintext, ciphertext, algorithm, timestamp
        FROM encrypted_messages
        WHERE username = ?
        ORDER BY timestamp DESC
    """, (session["username"],)).fetchall()
    conn.close()

    return render_template("history.html", username=session["username"], history=data)


# ======================================================
# ROUTE: ENKRIPSI & DEKRIPSI FILE
# ======================================================
@app.route("/encrypt_file", methods=["GET", "POST"])
def encrypt_file_route():
    if "username" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            output_path = os.path.join(app.config["ENCRYPTED_FOLDER"], filename + ".enc")
            file.save(input_path)

            encrypt_file(input_path, output_path)
            message = f"✅ File {filename} berhasil dienkripsi menjadi {filename}.enc"
        else:
            message = "❌ File tidak valid atau format tidak didukung."

    return render_template("encrypt_file.html", message=message, mode="encrypt")


@app.route("/decrypt_file", methods=["GET", "POST"])
def decrypt_file_route():
    if "username" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".enc"):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            output_path = os.path.join(app.config["ENCRYPTED_FOLDER"], filename.replace(".enc", "_decrypted"))
            file.save(input_path)

            try:
                decrypt_file(input_path, output_path)
                message = f"✅ File {filename} berhasil didekripsi menjadi {filename.replace('.enc', '_decrypted')}"
            except Exception as e:
                message = f"❌ Gagal dekripsi: {e}"
        else:
            message = "❌ Pastikan file memiliki ekstensi .enc"

    return render_template("encrypt_file.html", message=message, mode="decrypt")


# ======================================================
# ROUTE: STEGANOGRAFI (ENCODE & DECODE)
# ======================================================
@app.route("/steganografi_encode", methods=["GET", "POST"])
def steganografi_encode():
    if "username" not in session:
        return redirect(url_for("login"))
    
    message = ""
    if request.method == "POST":
        file = request.files["file"]
        secret_text = request.form["message"]
        if file and secret_text:
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            output_path = os.path.join(app.config["ENCRYPTED_FOLDER"], "encoded_" + filename)
            file.save(input_path)

            encode_message(input_path, secret_text, output_path)
            message = f"✅ Pesan berhasil disisipkan ke gambar: encoded_{filename}"
        else:
            message = "❌ Harap pilih gambar dan isi pesan."
    
    return render_template("steganografi.html", mode="encode", message=message)


@app.route("/steganografi_decode", methods=["GET", "POST"])
def steganografi_decode():
    if "username" not in session:
        return redirect(url_for("login"))
    
    decoded_text = ""
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(input_path)

            decoded_text = decode_message(input_path)
    
    return render_template("steganografi.html", mode="decode", message=decoded_text)


# ======================================================
# ROUTE: LOGOUT
# ======================================================
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Anda telah logout.", "info")
    return redirect(url_for("login"))


# ======================================================
# MAIN ENTRY
# ======================================================
if __name__ == "__main__":
    os.makedirs("database", exist_ok=True)
    app.run(debug=True)
