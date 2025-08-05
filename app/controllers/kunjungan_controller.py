from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.models import Kunjungan
from flask_jwt_extended import get_jwt_identity, get_jwt

def get_all_kunjungan():
    """Mengambil semua data kunjungan."""
    kunjungan_list = Kunjungan.query.all()
    return jsonify([k.to_dict() for k in kunjungan_list]), 200

def get_kunjungan_by_id(id):
    """Mengambil satu data kunjungan berdasarkan ID."""
    kunjungan = Kunjungan.query.get_or_404(id)
    return jsonify(kunjungan.to_dict()), 200

def create_kunjungan():
    """Membuat data kunjungan baru."""
    current_user_username = get_jwt_idezntity()

    if 'foto_kunjungan' not in request.files:
        return jsonify({'message': 'File foto_kunjungan tidak ditemukan'}), 400

    file = request.files['foto_kunjungan']
    if file.filename == '':
        return jsonify({'message': 'Tidak ada file yang dipilih'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    data = request.form
    new_kunjungan = Kunjungan(
        id_mr=current_user_username,
        no_visit=data.get('no_visit'),
        nama_outlet=data.get('nama_outlet'),
        lokasi=data.get('lokasi'),
        kegiatan=data.get('kegiatan'),
        kompetitor=data.get('kompetitor'),
        rata_rata_topup=data.get('rata_rata_topup'),
        potensi_topup=data.get('potensi_topup'),
        presentase_pemakaian=data.get('presentase_pemakaian'),
        issue=data.get('issue'),
        foto_kunjungan_path=filename
    )

    db.session.add(new_kunjungan)
    db.session.commit()
    return jsonify(new_kunjungan.to_dict()), 201

def update_kunjungan(id):
    """Memperbarui data kunjungan."""
    kunjungan = Kunjungan.query.get_or_404(id)
    data = request.json

    for key, value in data.items():
        if hasattr(kunjungan, key):
            setattr(kunjungan, key, value)

    db.session.commit()
    return jsonify(kunjungan.to_dict()), 200

def delete_kunjungan(id):
    """Menghapus data kunjungan."""
    kunjungan = Kunjungan.query.get_or_404(id)
    
    if kunjungan.foto_kunjungan_path:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], kunjungan.foto_kunjungan_path))
        except OSError as e:
            print(f"Error deleting file: {e.strerror}")

    db.session.delete(kunjungan)
    db.session.commit()
    return jsonify({'message': f'Kunjungan dengan ID {id} berhasil dihapus.'}), 200


def get_kunjungan_perhari():
    """Mengambil data kunjungan per hari."""
    kunjungan_list = Kunjungan.query.all()
    kunjungan_perhari = {}

    for k in kunjungan_list:
        tanggal = k.tanggal_input.date()
        if tanggal not in kunjungan_perhari:
            kunjungan_perhari[tanggal] = []
        kunjungan_perhari[tanggal].append(k.to_dict())

    return jsonify(kunjungan_perhari), 200

# ambil kunjungan berdasarkan username nya saja
def get_kunjungan_by_username():
    """Mengambil data kunjungan berdasarkan username."""
    current_user_username = get_jwt_identity()
    kunjungan_list = Kunjungan.query.filter_by(username=current_user_username).all()
    if not kunjungan_list:
        return jsonify({'message': 'Tidak ada kunjungan ditemukan untuk pengguna ini.'}), 404
    # Mengembalikan daftar kunjungan sebagai JSON
    kunjungan_list = Kunjungan.query.filter_by(id_mr=current_user_username).all()
    return jsonify([k.to_dict() for k in kunjungan_list]), 200