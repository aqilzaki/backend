import click
from flask.cli import with_appcontext
from .controllers import db, bcrypt
from .models.models import User

# Gunakan decorator @click untuk membuat perintah baru
@click.command(name='create_admin')
@click.argument('username')
@click.argument('password')
@with_appcontext
def create_admin(username, password):
    """Membuat user baru dengan peran sebagai admin."""
    # Cek apakah username sudah ada
    if User.query.filter_by(username=username).first():
        click.echo(f"Error: User dengan username '{username}' sudah ada.")
        return

    # Hash password dan buat user baru
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    admin_user = User(
        username=username,
        password_hash=hashed_password,
        role='admin'  # Ini yang paling penting
    )

    db.session.add(admin_user)
    db.session.commit()

    click.echo(f"Admin '{username}' berhasil dibuat!")