from app import create_app
# Impor perintah yang baru dibuat
from app.commands import create_admin

app = create_app()

# Daftarkan perintah ke aplikasi Flask
app.cli.add_command(create_admin)


if __name__ == '__main__':
    app.run(debug=True)