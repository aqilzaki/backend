from app.models.models import User, Absensi, Izin
from app import db
from flask import jsonify, request, current_app
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import func
def get_all_izin():
    """
    Mengambil semua data izin yang ada di database.
    Admin bisa melihat semua data, sedangkan sales hanya bisa melihat data miliknya sendiri.
    """
    current_user_username = get_jwt_identity()
    claims = get_jwt()

    if claims.get('role') == 'admin':
        # Admin bisa lihat semua data
        izin_list = Izin.query.all()
    else:
        # Sales hanya bisa lihat datanya sendiri
        izin_list = Izin.query.filter_by(id_mr=current_user_username).all()

    return jsonify([izin.to_dict() for izin in izin_list]), 200

def get_izin_by_id(id):
    """Mengambil satu data izin berdasarkan ID."""
    izin = Izin.query.get_or_404(id)
    return jsonify(izin.to_dict()), 200

def create_izin(): 
    """Membuat data baru untuk izin."""
    data = request.json
    username = get_jwt_identity()

    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
        return jsonify({"msg": "User tidak ditemukan"}), 404
    
    tanggal_izin = data.get('tanggal_izin')
    keterangan = data.get('keterangan')

    if not tanggal_izin:
        return jsonify({"msg": "Tanggal izin tidak boleh kosong"}), 400
    try:
        tanggal_izin = datetime.strptime(tanggal_izin, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"msg": "Format tanggal salah, gunakan YYYY-MM-DD"}), 400
    if not keterangan:
        keterangan = None
    # Cek apakah user sudah mengajukan izin pada tanggal ini
    existing_izin = Izin.query.filter_by(id_mr=user_obj.username, tanggal_izin=tanggal_izin).first()
    if existing_izin:
        return jsonify({"msg": "Anda sudah mengajukan izin pada tanggal ini"}), 400
    # Buat objek Izin baru
    new_izin = Izin(
        id_mr=user_obj.username,
        tanggal_izin=tanggal_izin,
        status_izin='pending',  # Status awal adalah 'pending'
        keterangan=keterangan
    )
    db.session.add(new_izin)
    db.session.commit()
    return jsonify({"msg": "Izin berhasil dibuat",
                    'name': user_obj.name,
                    "izin": new_izin.to_dict()}), 201

def update_izin_status(id, newStatus):
    """
    Mengupdate status izin berdasarkan ID.
    Hanya admin yang bisa mengubah status izin.
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Hanya admin yang bisa mengubah status izin"}), 403


    izin = Izin.query.get_or_404(id)
    if newStatus not in ['approved', 'rejected']:
        return jsonify({"msg": "Status tidak valid, hanya bisa 'approved' atau 'rejected'"}), 400

    izin.status_izin = newStatus
    db.session.commit()
    return jsonify({"msg": "Status izin berhasil diupdate", "izin": izin.to_dict()}), 200

def delete_izin(id):
    """
    Menghapus data izin berdasarkan ID.
    Hanya admin yang bisa menghapus data izin.
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"msg": "Hanya admin yang bisa menghapus data izin"}), 403

    izin = Izin.query.get_or_404(id)
    db.session.delete(izin)
    db.session.commit()
    return jsonify({"msg": "Izin berhasil dihapus"}), 200
