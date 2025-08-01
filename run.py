from app import create_app, db
from flask_migrate import Migrate
from flask.cli import with_appcontext
import click

app = create_app()
migrate = Migrate(app, db)

# Tambahkan command untuk init/migrate/upgrade
@app.cli.command("init-db")
@with_appcontext
def init_db():
    click.echo("Inisialisasi database…")
    db.create_all()
