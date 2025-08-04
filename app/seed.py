import click
from flask.cli import with_appcontext
from . import db, bcrypt
from .models.models import User, Absensi, Kunjungan
import random
from datetime import datetime, timedelta

@click.command(name='seed_db')
@with_appcontext
def seed_db():
    """Mengisi database dengan data dummy untuk pengujian."""
    
    # Hapus data lama terlebih dahulu untuk menghindari duplikat
    Kunjungan.query.delete()
    Absensi.query.delete()
    #User.query.delete()
    db.session.commit()
    click.echo("Membersihkan database lama.")

    # Buat user sales dummy
    lokasi = ['Jakarta', 'Bandung', 'Surabaya', 'padang', 'medan'] # Lokasi berbeda untuk setiap user
    lokasi_acak = random.choice(lokasi) # Pilih lokasi acak dari daftar
    click.echo(f"Lokasi acak yang dipilih: {lokasi_acak}")
    sales_users = []
    for i in range(1, 9): # Buat 3 user sales
        username = f'000{i}'
        name= f'agus {i}'
        password = '123'    
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        email = f'teddyedwar{i}@gmail.com'  # Pilih email acak dari daftar
        lokasi = lokasi_acak # Pilih lokasi acak dari daftar
        user = User(username=username, email=email, lokasi=lokasi, name=name, password_hash=hashed_password, role='sales')
        sales_users.append(user)
        db.session.add(user)
    
    db.session.commit()
    click.echo(f"{len(sales_users)} user sales berhasil dibuat.")

    # Buat data absensi dan kunjungan untuk 30 hari terakhir
    today = datetime.utcnow().date()
    for user in sales_users:
        for i in range(30): # Loop untuk 30 hari
            current_date = today - timedelta(days=i)
            
            # 80% kemungkinan user akan absen
            if random.random() < 0.8:
                # 30% kemungkinan telat
                status = 'Terlambat' if random.random() < 0.3 else 'Hadir'
                waktu_absen = (datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.randint(7, 10), minutes=random.randint(0, 59))).time()
                absen = Absensi(id_mr=user.username, tanggal=current_date, waktu_absen=waktu_absen, status_absen=status)
                db.session.add(absen)

                # Buat data kunjungan hanya jika user absen
                jumlah_kunjungan = random.randint(3, 7)
                kegiatan_list = ['maintenance', 'akuisisi', 'prospek']
                for _ in range(jumlah_kunjungan):
                    kunjungan = Kunjungan(
                        id_mr=user.username,
                        no_visit=random.randint(1, 100),
                        nama_outlet=f"Outlet Dummy {random.randint(1, 1000)}",
                        kegiatan=random.choice(kegiatan_list),
                        rata_rata_topup=random.uniform(50000, 200000),
                        potensi_topup=random.uniform(200000, 1000000),
                        issue="Issue dummy",
                        tanggal_input=datetime.combine(current_date, waktu_absen)
                    )
                    db.session.add(kunjungan)

    db.session.commit()
    click.echo("Data dummy untuk absensi dan kunjungan berhasil dibuat.")


@click.command(name='clear_db')
@with_appcontext
def clear_db():
    """Menghapus semua data dari tabel User, Absensi, dan Kunjungan."""
    try:
        # Hapus dengan urutan yang benar untuk menghindari error foreign key
        Kunjungan.query.delete()
        Absensi.query.delete()
        #User.query.delete()
        db.session.commit()
        click.echo("Semua data dummy berhasil dihapus.")
    except Exception as e:
        db.session.rollback()
        click.echo(f"Terjadi error saat menghapus data: {e}")