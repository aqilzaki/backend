import click
from flask.cli import with_appcontext
from . import db, bcrypt
from .models.models import User, Absensi, Kunjungan, Outlet
import random
from datetime import datetime, timedelta

@click.command(name='seed_db')
@with_appcontext
def seed_db():
    """Mengisi database dengan data dummy."""
    
    click.echo("Membersihkan database lama...")
    Kunjungan.query.delete()
    Absensi.query.delete()
    Outlet.query.delete()
    User.query.delete()
    db.session.commit()

    # --- Buat User Sales Dummy ---
    lokasi_list_user = ['Jakarta', 'Bandung', 'Surabaya', 'Padang', 'Medan']
    sales_users = []
    for i in range(1, 18):
        user = User(
            username=f'000{i}', name=f'Agus {i}',
            password_hash=bcrypt.generate_password_hash('123').decode('utf-8'),
            email=f'sales{i}@example.com', telpon=f'0812345678{i:02d}',
            lokasi=random.choice(lokasi_list_user), role='sales'
        )
        sales_users.append(user)
    db.session.add_all(sales_users)
    db.session.commit()
    click.echo(f"{len(sales_users)} user sales berhasil dibuat.")

    # --- Buat Outlet Dummy ---
    outlet_list = []
    for i in range(1, 51):
        lat = round(random.uniform(-0.95, -0.91), 6)
        lon = round(random.uniform(100.35, 100.39), 6)
        lokasi_koordinat = f"{lat},{lon}"
        outlet = Outlet(
            id_outlet=f"TM{i:04d}",
            nama_outlet=f"Toko Maju Jaya {i}",
            lokasi=lokasi_koordinat
        )
        outlet_list.append(outlet)
    db.session.add_all(outlet_list)
    db.session.commit()
    click.echo(f"{len(outlet_list)} outlet dummy berhasil dibuat.")

    # --- Buat Data Absensi dan Kunjungan ---
    today = datetime.now().date()
    for user in sales_users:
        for i in range(30):
            current_date = today - timedelta(days=i)
            if random.random() < 0.8:
                status = 'Terlambat' if random.random() < 0.3 else 'Hadir'
                waktu_absen = (datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.randint(7, 10), minutes=random.randint(0, 59))).time()
                absen = Absensi(id_mr=user.username, tanggal=current_date, waktu_absen=waktu_absen, status_absen=status, lokasi=user.lokasi)
                db.session.add(absen)

                jumlah_kunjungan = random.randint(3, 7)
                kegiatan_list = ['maintenance', 'akuisisi', 'prospek']
                for _ in range(jumlah_kunjungan):
                    outlet_terpilih = random.choice(outlet_list)
                    kunjungan = Kunjungan(
                        id_mr=user.username,
                        id_outlet=outlet_terpilih.id_outlet, # Gunakan id_outlet (string)
                        no_visit=random.randint(1, 100),
                        lokasi=outlet_terpilih.lokasi,
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
    try:
        Kunjungan.query.delete()
        Absensi.query.delete()
        Outlet.query.delete()
        User.query.delete()
        db.session.commit()
        click.echo("Semua data dummy berhasil dihapus.")
    except Exception as e:
        db.session.rollback()
        click.echo(f"Terjadi error saat menghapus data: {e}")