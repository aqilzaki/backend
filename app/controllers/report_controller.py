from flask import jsonify
from sqlalchemy import func, extract
from app import db
from app.models.models import Absensi, Kunjungan
from flask_jwt_extended import get_jwt_identity
from datetime import datetime


def get_daily_report():
    """Membuat laporan harian untuk user yang sedang login."""
    current_user = get_jwt_identity()
    today = datetime.utcnow().date()

    # --- Laporan Absensi ---
    absensi_hari_ini = Absensi.query.filter_by(id_mr=current_user, tanggal=today).first()
    laporan_absen_text = "Anda belum absen hari ini, jangan lupa absen ya!"
    status_absen_code = 0 # 0: Belum Absen, 1: Hadir, 2: Terlambat
    if absensi_hari_ini:
        if absensi_hari_ini.status_absen == 'Hadir':
            laporan_absen_text = "Absen selesai bos, tepat waktu banget sih! 👍"
            status_absen_code = 1
        else:
            laporan_absen_text = "Kok telat sih bos, besok lebih pagi ya! ⏰"
            status_absen_code = 2

    # --- Laporan Kunjungan ---
    kunjungan_hari_ini = Kunjungan.query.filter(Kunjungan.id_mr == current_user, func.date(Kunjungan.tanggal_input) == today).all()
    jumlah_kunjungan = len(kunjungan_hari_ini)
    jumlah_akuisisi = sum(1 for k in kunjungan_hari_ini if k.kegiatan == 'akuisisi')

    if jumlah_kunjungan < 5:
        laporan_kunjungan_text = f"Kunjungan hari ini baru {jumlah_kunjungan}. Kurang {5 - jumlah_kunjungan} lagi, semangat! 🔥"
    else:
        if jumlah_akuisisi < 2:
            laporan_kunjungan_text = f"Kunjungan sudah {jumlah_kunjungan}, mantap! Tapi akuisisi baru {jumlah_akuisisi}, ayo tambah lagi."
        else:
            laporan_kunjungan_text = f"Target tercapai! Total {jumlah_kunjungan} kunjungan dengan {jumlah_akuisisi} akuisisi. Keren! 🏆"

    return jsonify({
        'username': current_user,
        'laporan_text': {
            'absensi': laporan_absen_text,
            'kunjungan': laporan_kunjungan_text,
        },
        'laporan_angka': {
            'absensi': {'status': status_absen_code},
            'kunjungan': {'total': jumlah_kunjungan, 'akuisisi': jumlah_akuisisi}
        }
    }), 200

def get_monthly_report(year, month):
    """Membuat laporan bulanan untuk user yang sedang login."""
    current_user = get_jwt_identity()

    # Query Absensi
    absensi_bulan_ini = db.session.query(
        Absensi.status_absen, func.count(Absensi.status_absen)
    ).filter(
        Absensi.id_mr == current_user,
        extract('year', Absensi.tanggal) == year,
        extract('month', Absensi.tanggal) == month
    ).group_by(Absensi.status_absen).all()
    
    rekap_absensi = {'Hadir': 0, 'Terlambat': 0}
    for status, jumlah in absensi_bulan_ini:
        rekap_absensi[status] = jumlah

    # Query Kunjungan
    kunjungan_bulan_ini = db.session.query(
        Kunjungan.kegiatan, func.count(Kunjungan.kegiatan)
    ).filter(
        Kunjungan.id_mr == current_user,
        extract('year', Kunjungan.tanggal_input) == year,
        extract('month', Kunjungan.tanggal_input) == month
    ).group_by(Kunjungan.kegiatan).all()

    rekap_kunjungan = {'maintenance': 0, 'akuisisi': 0, 'prospek': 0}
    total_kunjungan = 0
    for kegiatan, jumlah in kunjungan_bulan_ini:
        rekap_kunjungan[kegiatan] = jumlah
        total_kunjungan += jumlah

    return jsonify({
        'username': current_user,
        'periode': f"{month:02d}-{year}",
        'rekap_absensi': rekap_absensi,
        'rekap_kunjungan': {
            'total': total_kunjungan,
            'detail': rekap_kunjungan
        }
    }), 200

def get_yearly_report(year):
    """Membuat laporan tahunan per bulan untuk user yang sedang login."""
    current_user = get_jwt_identity()

    # Inisialisasi data laporan untuk 12 bulan
    report_data = {month: {'absensi': {'Hadir': 0, 'Terlambat': 0}, 'kunjungan': 0} for month in range(1, 13)}

    # Query Absensi Tahunan
    absensi_tahunan = db.session.query(
        extract('month', Absensi.tanggal).label('bulan'),
        Absensi.status_absen,
        func.count(Absensi.id)
    ).filter(
        Absensi.id_mr == current_user,
        extract('year', Absensi.tanggal) == year
    ).group_by('bulan', Absensi.status_absen).all()

    for bulan, status, jumlah in absensi_tahunan:
        report_data[bulan]['absensi'][status] = jumlah

    # Query Kunjungan Tahunan
    kunjungan_tahunan = db.session.query(
        extract('month', Kunjungan.tanggal_input).label('bulan'),
        func.count(Kunjungan.id)
    ).filter(
        Kunjungan.id_mr == current_user,
        extract('year', Kunjungan.tanggal_input) == year
    ).group_by('bulan').all()
    
    for bulan, jumlah in kunjungan_tahunan:
        report_data[bulan]['kunjungan'] = jumlah
        
    return jsonify({
        'username': current_user,
        'periode_tahun': year,
        'laporan_per_bulan': report_data
    }), 200

# --- FUNGSI LAPORAN UNTUK ADMIN ---

def get_admin_monthly_report(year, month, username):
    """
    Membuat laporan bulanan untuk user spesifik (dipanggil oleh admin).
    Logikanya sama dengan get_monthly_report, hanya saja username-nya dari parameter.
    """
    # Query Absensi
    absensi_bulan_ini = db.session.query(
        Absensi.status_absen, func.count(Absensi.status_absen)
    ).filter(
        Absensi.id_mr == username,
        extract('year', Absensi.tanggal) == year,
        extract('month', Absensi.tanggal) == month
    ).group_by(Absensi.status_absen).all()
    
    rekap_absensi = {'Hadir': 0, 'Terlambat': 0}
    for status, jumlah in absensi_bulan_ini:
        rekap_absensi[status] = jumlah

    # Query Kunjungan
    kunjungan_bulan_ini = db.session.query(
        Kunjungan.kegiatan, func.count(Kunjungan.kegiatan)
    ).filter(
        Kunjungan.id_mr == username,
        extract('year', Kunjungan.tanggal_input) == year,
        extract('month', Kunjungan.tanggal_input) == month
    ).group_by(Kunjungan.kegiatan).all()

    rekap_kunjungan = {'maintenance': 0, 'akuisisi': 0, 'prospek': 0}
    total_kunjungan = 0
    for kegiatan, jumlah in kunjungan_bulan_ini:
        rekap_kunjungan[kegiatan] = jumlah
        total_kunjungan += jumlah

    return jsonify({
        'username': username,
        'periode': f"{month:02d}-{year}",
        'rekap_absensi': rekap_absensi,
        'rekap_kunjungan': {
            'total': total_kunjungan,
            'detail': rekap_kunjungan
        }
    }), 200


def get_admin_all_sales_summary(year, month):
    """
    Membuat rekapitulasi performa semua sales untuk admin dalam satu bulan.
    """
    # Query untuk rekap absensi semua user
    absensi_summary = db.session.query(
        Absensi.id_mr, Absensi.status_absen, func.count(Absensi.id)
    ).filter(
        extract('year', Absensi.tanggal) == year,
        extract('month', Absensi.tanggal) == month
    ).group_by(Absensi.id_mr, Absensi.status_absen).all()
    
    # Query untuk rekap kunjungan semua user
    kunjungan_summary = db.session.query(
        Kunjungan.id_mr, func.count(Kunjungan.id)
    ).filter(
        extract('year', Kunjungan.tanggal_input) == year,
        extract('month', Kunjungan.tanggal_input) == month
    ).group_by(Kunjungan.id_mr).all()

    # Olah data menjadi format yang mudah dibaca
    report = {}
    for username, status, count in absensi_summary:
        if username not in report:
            report[username] = {'absensi': {'Hadir': 0, 'Terlambat': 0}, 'kunjungan': 0}
        report[username]['absensi'][status] = count

    for username, count in kunjungan_summary:
        if username not in report:
            report[username] = {'absensi': {'Hadir': 0, 'Terlambat': 0}, 'kunjungan': 0}
        report[username]['kunjungan'] = count

    return jsonify({
        'periode': f"{month:02d}-{year}",
        'summary_per_sales': report
    }), 200


# --- FUNGSI LAPORAN TAHUNAN BARU UNTUK ADMIN ---
def get_admin_yearly_summary(year):
    """
    Membuat rekapitulasi tahunan performa semua sales untuk admin,
    mencakup detail kunjungan dan absensi per bulan.
    """
    # --- Inisialisasi struktur data laporan yang baru ---
    # Format: { 'sales1': { 1: {'kunjungan':{...}, 'absensi':{...}}, 2: {...} }, ... }
    report = {}

    # --- 1. Query data Kunjungan untuk setahun ---
    kunjungan_summary = db.session.query(
        Kunjungan.id_mr,
        extract('month', Kunjungan.tanggal_input).label('bulan'),
        Kunjungan.kegiatan,
        func.count(Kunjungan.id).label('jumlah')
    ).filter(
        extract('year', Kunjungan.tanggal_input) == year
    ).group_by(Kunjungan.id_mr, 'bulan', Kunjungan.kegiatan).all()

    # Olah data kunjungan
    for username, bulan, kegiatan, jumlah in kunjungan_summary:
        if username not in report:
            report[username] = {
                month: {
                    'kunjungan': {'maintenance': 0, 'akuisisi': 0, 'prospek': 0, 'total': 0},
                    'absensi': {'Hadir': 0, 'Terlambat': 0}
                } for month in range(1, 13)
            }
        
        if bulan and kegiatan:
            bulan = int(bulan)
            if 1 <= bulan <= 12:
                report[username][bulan]['kunjungan'][kegiatan] = jumlah
                report[username][bulan]['kunjungan']['total'] += jumlah

    # --- 2. Query data Absensi untuk setahun ---
    absensi_summary = db.session.query(
        Absensi.id_mr,
        extract('month', Absensi.tanggal).label('bulan'),
        Absensi.status_absen,
        func.count(Absensi.id).label('jumlah')
    ).filter(
        extract('year', Absensi.tanggal) == year
    ).group_by(Absensi.id_mr, 'bulan', Absensi.status_absen).all()

    # Olah data absensi
    for username, bulan, status, jumlah in absensi_summary:
        if username not in report:
            report[username] = {
                month: {
                    'kunjungan': {'maintenance': 0, 'akuisisi': 0, 'prospek': 0, 'total': 0},
                    'absensi': {'Hadir': 0, 'Terlambat': 0}
                } for month in range(1, 13)
            }

        if bulan and status:
            bulan = int(bulan)
            if 1 <= bulan <= 12 and status in report[username][bulan]['absensi']:
                report[username][bulan]['absensi'][status] = jumlah

    return jsonify({
        'periode_tahun': year,
        'summary_tahunan_per_sales': report
    }), 200