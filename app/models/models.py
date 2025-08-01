from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()


class Absensi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_mr = db.Column(db.String(20), nullable=False)
    tanggal = db.Column(db.Date, default=datetime.utcnow().date)
    waktu_absen = db.Column(db.Time, default=datetime.utcnow().time)
    status_absen = db.Column(db.String(20))
    foto_absen_path = db.Column(db.String(255))
    lokasi = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Kunjungan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_mr = db.Column(db.String(20), nullable=False)
    no_visit = db.Column(db.Integer, nullable=False)
    nama_outlet = db.Column(db.String(100), nullable=False)
    lokasi = db.Column(db.String(255))
    foto_kunjungan_path = db.Column(db.String(255))
    kegiatan = db.Column(db.Enum('maintenance', 'akuisisi', 'prospek'), nullable=False)
    kompetitor = db.Column(db.String(255))
    rata_rata_topup = db.Column(db.Float)
    potensi_topup = db.Column(db.Float)
    presentase_pemakaian = db.Column(db.Float)
    issue = db.Column(db.Text)
    tanggal_input = db.Column(db.DateTime, default=datetime.utcnow)

