from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Tentukan peran: 'admin' atau 'sales'
    role = db.Column(db.String(20), nullable=False, default='sales')

    # Relasi ke Absensi dan Kunjungan
    # 'id_mr' di Absensi/Kunjungan akan merujuk ke 'username' di tabel User
    absensi = db.relationship('Absensi', backref='user', lazy=True, foreign_keys='Absensi.id_mr', primaryjoin="User.username==Absensi.id_mr")
    kunjungan = db.relationship('Kunjungan', backref='user', lazy=True, foreign_keys='Kunjungan.id_mr', primaryjoin="User.username==Kunjungan.id_mr")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

class Absensi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_mr = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tanggal = db.Column(db.Date, default=datetime.utcnow().date)
    waktu_absen = db.Column(db.Time, default=datetime.utcnow().time)
    status_absen = db.Column(db.String(20))
    lokasi = db.Column(db.String(255))
    foto_absen_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Mengubah objek model menjadi dictionary."""
        return {
            'id': self.id,
            'id_mr': self.id_mr,
            'tanggal': self.tanggal.isoformat() if self.tanggal else None,
            'waktu_absen': self.waktu_absen.isoformat() if self.waktu_absen else None,
            'status_absen': self.status_absen,
            'lokasi': self.lokasi,
            'foto_absen_path': self.foto_absen_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Kunjungan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_mr = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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

    def to_dict(self):
        """Mengubah objek model menjadi dictionary."""
        return {
            'id': self.id,
            'id_mr': self.id_mr,
            'no_visit': self.no_visit,
            'nama_outlet': self.nama_outlet,
            'lokasi': self.lokasi,
            'foto_kunjungan_path': self.foto_kunjungan_path,
            'kegiatan': self.kegiatan,
            'kompetitor': self.kompetitor,
            'rata_rata_topup': self.rata_rata_topup,
            'potensi_topup': self.potensi_topup,
            'presentase_pemakaian': self.presentase_pemakaian,
            'issue': self.issue,
            'tanggal_input': self.tanggal_input.isoformat() if self.tanggal_input else None
        }