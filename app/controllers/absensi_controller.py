from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.models import Absensi
from datetime import datetime, time
import pytz
from flask_jwt_extended import get_jwt_identity, get_jwt

def get_all_absensi():
    current_user_username = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') == 'admin':
        # Admin bisa lihat semua data
        absensi_list = Absensi.query.all()
    else:
        # Sales hanya bisa lihat datanya sendiri
        absensi_list = Absensi.query.filter_by(id_mr=current_user_username).all()
        
    return jsonify([absen.to_dict() for absen in absensi_list]), 200

def get_absensi_by_id(id):
    """Mengambil satu data absensi berdasarkan ID."""
    absen = Absensi.query.get_or_404(id)
    return jsonify(absen.to_dict()), 200

def create_absensi():
    """
    Membuat data absensi baru dengan validasi dan zona waktu yang benar dan konsisten.
    """
    current_user_username = get_jwt_identity()

    # 1. Dapatkan waktu saat ini. Karena koneksi DB sudah di-set, kita bisa pakai waktu server.
    #    Namun, menggunakan pytz tetap praktik terbaik untuk kejelasan.
    zona_waktu_jakarta = pytz.timezone('Asia/Jakarta')
    waktu_sekarang_obj = datetime.now(zona_waktu_jakarta)
    
    # 2. Ekstrak tanggal dan waktu untuk digunakan di semua logika
    tanggal_hari_ini = waktu_sekarang_obj.date()
    waktu_saat_ini = waktu_sekarang_obj.time()

    # 3. VALIDASI SEKALI SEHARI (DIJAMIN BERFUNGSI)
    #    Mencari absensi berdasarkan username DAN tanggal yang sudah benar (WIB).
    existing_absen = Absensi.query.filter_by(
        id_mr=current_user_username,
        tanggal=tanggal_hari_ini
    ).first()

    if existing_absen:
        return jsonify({'message': 'udah absen hari ini bos'}), 409

    # 4. Lanjutkan proses jika validasi lolos
    if 'foto_absen' not in request.files:
        return jsonify({'message': 'File foto_absen tidak ditemukan'}), 400

    file = request.files['foto_absen']
    if file.filename == '':
        return jsonify({'message': 'Tidak ada file yang dipilih'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # 5. Tentukan status berdasarkan waktu yang sudah benar
    batas_waktu_terlambat = time(9, 0, 0)
    status = 'Terlambat' if waktu_saat_ini > batas_waktu_terlambat else 'Hadir'

    # 6. Buat objek Absensi baru dengan data yang eksplisit dan konsisten
    new_absen = Absensi(
        id_mr=current_user_username,
        status_absen=status,
        foto_absen_path=filename,
        tanggal=tanggal_hari_ini,      # Gunakan tanggal yang sudah kita definisikan
        waktu_absen=waktu_saat_ini,    # Gunakan waktu yang sudah kita definisikan
        created_at=waktu_sekarang_obj  # Gunakan objek datetime lengkap
    )

    db.session.add(new_absen)
    db.session.commit()
    
    return jsonify(new_absen.to_dict()), 201

def update_absensi(id):
    """Memperbarui data absensi."""
    absen = Absensi.query.get_or_404(id)
    data = request.json

    absen.id_mr = data.get('id_mr', absen.id_mr)
    absen.status_absen = data.get('status_absen', absen.status_absen)
    absen.lokasi = data.get('lokasi', absen.lokasi)
    # Note: Logika untuk update foto bisa lebih kompleks, ini contoh sederhana.

    db.session.commit()
    return jsonify(absen.to_dict()), 200

def delete_absensi(id):
    """Menghapus data absensi."""
    absen = Absensi.query.get_or_404(id)
    
    # Hapus file foto terkait jika ada
    if absen.foto_absen_path:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], absen.foto_absen_path))
        except OSError as e:
            print(f"Error deleting file: {e.strerror}")

    db.session.delete(absen)
    db.session.commit()
    return jsonify({'message': f'Absensi dengan ID {id} berhasil dihapus.'}), 200