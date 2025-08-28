# Impor variabel 'app' dari file 'app.py' Anda
from app import create_app
from app.commands import create_admin
from app.seed import seed_db, clear_db

app = create_app()

# Daftarkan perintah ke aplikasi Flask
app.cli.add_command(create_admin)
app.cli.add_command(seed_db)
app.cli.add_command(clear_db)
# Ini adalah baris yang wajib ada agar server produksi
# seperti Waitress bisa mendeteksi aplikasi Anda saat dijalankan.
if __name__ == "__main__":
    app.run()