from flask import jsonify
from app.models.models import Kunjungan, User
from sqlalchemy import func
from datetime import datetime

def get_daily_tracking_data(username, date_str):
    """
    Mengambil data riwayat lokasi kunjungan seorang sales pada tanggal tertentu,
    TERMASUK PATH FOTO KUNJUNGAN.
    """
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"msg": "Format tanggal salah"}), 400

    kunjungan_harian = Kunjungan.query.filter(
        Kunjungan.id_mr == username,
        func.date(Kunjungan.tanggal_input) == target_date
    ).order_by(Kunjungan.tanggal_input.asc()).all()

    if not kunjungan_harian:
        return jsonify({"msg": "Tidak ada data kunjungan untuk user ini pada tanggal tersebut.", "route": []}), 200

    route_data = []
    for k in kunjungan_harian:
        kunjungan_dict = k.to_dict()
        
        # Mengganti nama kunci 'lokasi' menjadi 'lokasi_koordinat'
        kunjungan_dict['lokasi_koordinat'] = kunjungan_dict.pop('lokasi', None)
        # Menambahkan format waktu
        kunjungan_dict['waktu_kunjungan'] = k.tanggal_input.strftime('%H:%M:%S')
        
        # --- PERUBAHAN UTAMA DI SINI ---
        # Bangun URL lengkap untuk foto jika ada
        if kunjungan_dict.get('foto_kunjungan_path'):
            kunjungan_dict['foto_kunjungan_path'] = f"{kunjungan_dict['foto_kunjungan_path']}"
        else:
            kunjungan_dict['foto_kunjungan_path'] = None
        
        route_data.append(kunjungan_dict)

    return jsonify({"route": route_data}), 200


def get_daily_tracking_all_data(date_str):
    """
    Mengambil data riwayat lokasi semua sales pada tanggal tertentu
    dengan cara yang efisien dan format yang benar.
    """
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"msg": "Format tanggal tidak valid. Gunakan YYYY-MM-DD."}), 400

    # Ambil semua kunjungan pada tanggal tersebut, dan lakukan join dengan tabel User
    kunjungan_hari_ini = Kunjungan.query.join(
        User, Kunjungan.id_mr == User.username
    ).filter(
        func.date(Kunjungan.tanggal_input) == target_date
    ).order_by(Kunjungan.id_mr, Kunjungan.tanggal_input.asc()).all()

    if not kunjungan_hari_ini:
        return jsonify({
            "tanggal": date_str,
            "msg": "Tidak ada data kunjungan pada tanggal tersebut.",
            "route_per_sales": {}
        }), 200

    route_per_sales = {}

    for kunjungan in kunjungan_hari_ini:
        username = kunjungan.id_mr
        
        # Jika username belum ada di laporan, buat strukturnya
        if username not in route_per_sales:
            route_per_sales[username] = {
                "name": kunjungan.user.name,
                "lokasi_sales": kunjungan.user.lokasi,
                "kunjungan": []
            }
        
        kunjungan_dict = kunjungan.to_dict()
        
        # --- PERBAIKAN UTAMA DI SINI ---
        # Ambil nama file dari 'foto_kunjungan'
        foto_filename = kunjungan_dict.get('foto_kunjungan_path')
        
        # Bangun URL lengkap HANYA JIKA nama filenya ada
        if foto_filename:
            foto_url = f"{foto_filename}"
        else:
            foto_url = None

        # Tambahkan detail kunjungan ke dalam list
        route_per_sales[username]["kunjungan"].append({
            "tes_gok_gok": kunjungan_dict.get('nama_outlet'),
            "nama_outlet": kunjungan_dict.get('nama_outlet'),
            "lokasi_koordinat": kunjungan_dict.get('lokasi'),
            "waktu_kunjungan": kunjungan.tanggal_input.strftime('%H:%M:%S'),
            "kegiatan": kunjungan_dict.get('kegiatan'),
            "foto_kunjungan_path": foto_url # <-- Gunakan URL yang sudah jadi
        })

    return jsonify({
        "tanggal": date_str,
        "route_per_sales": route_per_sales
    }), 200