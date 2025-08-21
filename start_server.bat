@echo off
ECHO "🚀 Memulai server backend..."

REM 1. Masuk ke direktori proyek (jika diperlukan)
REM cd C:\path\to\your\project

REM 2. Aktifkan virtual environment
ECHO "🐍 Mengaktifkan virtual environment..."
call venv\Scripts\activate

REM 3. (Opsional) Install atau update library
ECHO "📦 Menginstall dependencies..."
pip install -r requirements.txt

REM 4. Jalankan aplikasi menggunakan Waitress (Gunicorn tidak ada di Windows)
ECHO "🔥 Menjalankan Waitress di port 5000..."
waitress-serve --host 127.0.0.1 --port 5000 wsgi:app

ECHO "✅ Server berhasil dijalankan."
pause