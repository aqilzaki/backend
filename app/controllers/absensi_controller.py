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
    """Membuat data absensi baru dengan validasi sekali sehari."""
    current_user_username = get_jwt_identity()
     # 1. Tentukan zona waktu Asia/Jakarta
    zona_waktu_jakarta = pytz.timezone('Asia/Jakarta')
    
    # 2. Ambil waktu saat ini sesuai zona waktu tersebut
    waktu_jakarta_sekarang = datetime.now(zona_waktu_jakarta)
    today = waktu_jakarta_sekarang.date()
    waktu_sekarang = waktu_jakarta_sekarang.time()
    # --- LOGIKA VALIDASI SEKALI SEHARI DIMULAI DI SINI ---
    # 1. Cek ke database apakah user ini sudah ada record absensinya untuk tanggal hari ini.
    existing_absen = Absensi.query.filter_by(
        id_mr=current_user_username,
        tanggal=today
    ).first()

    # 2. Jika sudah ada, kembalikan pesan error.
    if existing_absen:
        return jsonify({'message': 'udah absen hari ini bos'}), 409 # 409 Conflict adalah status yang tepat

    # --- JIKA BELUM ABSEN, LANJUTKAN PROSES SEPERTI BIASA ---

    if 'foto_absen' not in request.files:
        return jsonify({'message': 'File foto_absen tidak ditemukan'}), 400

    file = request.files['foto_absen']
    if file.filename == '':
        return jsonify({'message': 'Tidak ada file yang dipilih'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Logika status otomatis (Hadir/Terlambat)
    waktu_sekarang = datetime.utcnow().time()
    batas_waktu_terlambat = time(9, 0, 0)
    status = 'Terlambat' if waktu_sekarang > batas_waktu_terlambat else 'Hadir'

    data = request.form
    new_absen = Absensi(
        id_mr=current_user_username,
        status_absen=status,
        lokasi=data.get('lokasi'),
        foto_absen_path=filename
        # Kolom 'tanggal' dan 'waktu_absen' akan diisi otomatis oleh default di model
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