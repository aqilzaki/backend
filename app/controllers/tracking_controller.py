from flask import jsonify
from app.models.models import Kunjungan, User
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

    # Jika ada data, ambil nama user dari tabel User
    user = User.query.filter_by(username=username).first()

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
    Mengambil data riwayat lokasi semua sales pada tanggal tertentu
    dengan cara yang efisien.
    """
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"msg": "Format tanggal tidak valid. Gunakan YYYY-MM-DD."}), 400

    # --- PERBAIKAN UTAMA DI SINI ---
    # 1. Ambil semua kunjungan pada tanggal tersebut.
    #    SQLAlchemy akan secara otomatis me-load data user yang terkait
    #    karena kita sudah mendefinisikan relasi di model.
    kunjungan_hari_ini = Kunjungan.query.filter(
        func.date(Kunjungan.tanggal_input) == target_date
    ).order_by(Kunjungan.tanggal_input.asc()).all()

    if not kunjungan_hari_ini:
        return jsonify({
            "tanggal": date_str,
            "msg": "Tidak ada data kunjungan pada tanggal tersebut.",
            "route_per_sales": {} # Kirim objek kosong jika tidak ada data
        }), 200

    # 2. Olah data menjadi format yang dikelompokkan per sales
    route_per_sales = {}

    for kunjungan in kunjungan_hari_ini:
        # Dapatkan username dari relasi
        username = kunjungan.user.username if kunjungan.user else "unknown"

        # Jika username belum ada di laporan, buat strukturnya
        if username not in route_per_sales:
            route_per_sales[username] = {
                "name": kunjungan.user.name if kunjungan.user else "Unknown User",
                "lokasi_sales": kunjungan.user.lokasi if kunjungan.user else "N/A",
                "kunjungan": []
            }

        # Tambahkan detail kunjungan ke dalam list
        route_per_sales[username]["kunjungan"].append({
            "nama_outlet": kunjungan.nama_outlet,
            "lokasi_koordinat": kunjungan.lokasi,
            "waktu_kunjungan": kunjungan.tanggal_input.strftime('%H:%M:%S'),
            "kegiatan": kunjungan.kegiatan
        })

    return jsonify({
        "tanggal": date_str,
        "route_per_sales": route_per_sales
    }), 200