from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.models import Absensi

def get_all_absensi():
    """Mengambil semua data absensi."""
    absensi_list = Absensi.query.all()
    return jsonify([absen.to_dict() for absen in absensi_list]), 200

def get_absensi_by_id(id):
    """Mengambil satu data absensi berdasarkan ID."""
    absen = Absensi.query.get_or_404(id)
    return jsonify(absen.to_dict()), 200

def create_absensi():
    """Membuat data absensi baru."""
    if 'foto_absen' not in request.files:
        return jsonify({'message': 'File foto_absen tidak ditemukan'}), 400

    file = request.files['foto_absen']
    if file.filename == '':
        return jsonify({'message': 'Tidak ada file yang dipilih'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    data = request.form
    new_absen = Absensi(
        id_mr=data.get('id_mr'),
        status_absen=data.get('status_absen'),
        lokasi=data.get('lokasi'),
        foto_absen_path=filename  # Simpan nama file
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