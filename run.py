from app import create_app
from app.commands import create_admin, create_cs
from app.seed import seed_db, clear_db

app = create_app()

# Daftarkan perintah ke aplikasi Flask
app.cli.add_command(create_admin)
app.cli.add_command(create_cs)
app.cli.add_command(seed_db)
app.cli.add_command(clear_db)

if __name__ == '__main__':
    app.run(debug=True)