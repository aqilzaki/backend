from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.models import Absensi
from datetime import datetime, time as dt_time # Ganti nama import time

import time
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
    """Membuat data absensi baru (Hadir/Terlambat) dari sales."""
    try:
        username = get_jwt_identity()
        
        # Ambil data dari form-data
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        foto_absen = request.files.get('foto_absen')

        if not latitude or not longitude or not foto_absen:
            return jsonify({"msg": "Lokasi dan Foto wajib untuk absensi."}), 400

        # Gunakan zona waktu Asia/Jakarta (WIB)
        tz = pytz.timezone('Asia/Jakarta')
        today = datetime.now(tz).date()
        
        # Cek apakah user sudah absen hari ini
        existing_absensi = Absensi.query.filter_by(id_mr=username, tanggal=today).first()
        if existing_absensi:
            return jsonify({"msg": f"Anda sudah melakukan absensi hari ini."}), 400

        # Proses penyimpanan file foto
        filename = f"absen_{username}_{int(time.time())}.jpg"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        foto_absen.save(file_path)

        # Tentukan status Hadir atau Terlambat berdasarkan waktu WIB
        waktu_absen_wib = datetime.now(tz).time()
        jam_masuk = datetime.strptime('08:30:00', '%H:%M:%S').time()
        status = 'Hadir' if waktu_absen_wib <= jam_masuk else 'Terlambat'
        
        # Buat objek Absensi baru
        new_absensi = Absensi(
            id_mr=username,
            tanggal=today,
            waktu_absen=waktu_absen_wib,
            status_absen=status,
            lokasi=f"{latitude},{longitude}",
            foto_absen_path=filename
        )

        db.session.add(new_absensi)
        db.session.commit()

        return jsonify(new_absensi.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error di create_absensi: {e}")
        return jsonify({"msg": "Terjadi kesalahan di server."}), 500
    
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


def get_all_absensi_by_user():
    """Mengambil semua data absensi untuk user yang sedang login."""
    username = get_jwt_identity()
    absensi_list = Absensi.query.filter_by(id_mr=username).all()
    
    return jsonify([absen.to_dict() for absen in absensi_list]), 200