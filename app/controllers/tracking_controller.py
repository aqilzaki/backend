from flask import jsonify
from app.models.models import Kunjungan
from sqlalchemy import func
from datetime import datetime

def get_daily_tracking_data(username, date_str):
    """
    Mengambil data riwayat lokasi kunjungan seorang sales pada tanggal tertentu.
    """
    try: 
        # Ubah string tanggal (YYYY-MM-DD) menjadi objek date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"msg": "Format tanggal tidak valid. Gunakan YYYY-MM-DD."}), 400

    # Query semua kunjungan oleh user pada tanggal tersebut, diurutkan berdasarkan waktu
    kunjungan_hari_ini = Kunjungan.query.filter(
        Kunjungan.user.has(username=username), # Filter berdasarkan username di tabel User
        func.date(Kunjungan.tanggal_input) == target_date
    ).order_by(Kunjungan.tanggal_input.asc()).all()

    if not kunjungan_hari_ini:
        return jsonify({
            "username": username,
            "tanggal": date_str,
            "msg": "Tidak ada data kunjungan untuk sales ini pada tanggal tersebut.",
            "route": []
        }), 200

    # Siapkan data rute untuk dikirim
    route_data = []
    for kunjungan in kunjungan_hari_ini:
        route_data.append({
            "nama_outlet": kunjungan.nama_outlet,
            "lokasi_koordinat": kunjungan.lokasi,
            "waktu_kunjungan": kunjungan.tanggal_input.strftime('%H:%M:%S'),
            "kegiatan": kunjungan.kegiatan
        })

    return jsonify({
        "username": username,
        "tanggal": date_str,
        "route": route_data
    }), 200

def get_daily_tracking_all_data(date_str):
    """
    Mengambil data riwayat lokasi kunjungan semua sales pada tanggal tertentu.
    """
    try:
        # Ubah string tanggal (YYYY-MM-DD) menjadi objek date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"msg": "Format tanggal tidak valid. Gunakan YYYY-MM-DD."}), 400

    # Query semua kunjungan pada tanggal tersebut, diurutkan berdasarkan username dan waktu
    kunjungan_hari_ini = Kunjungan.query.filter(
        func.date(Kunjungan.tanggal_input) == target_date
    ).order_by(Kunjungan.user.has(username=Kunjungan.id_mr), Kunjungan.tanggal_input.asc()).all()

    if not kunjungan_hari_ini:
        return jsonify({
            "tanggal": date_str,
            "msg": "Tidak ada data kunjungan untuk semua sales pada tanggal tersebut.",
            "route": []
        }), 200

    # Siapkan data rute untuk dikirim
    route_data = []
    for kunjungan in kunjungan_hari_ini:
        route_data.append({
            "username": kunjungan.id_mr,
            "nama_outlet": kunjungan.nama_outlet,
            "lokasi_koordinat": kunjungan.lokasi,
            "waktu_kunjungan": kunjungan.tanggal_input.strftime('%H:%M:%S'),
            "kegiatan": kunjungan.kegiatan
        })

    return jsonify({
        "tanggal": date_str,
        "route": route_data
    }), 200