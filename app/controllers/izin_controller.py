from app.models.models import User, Absensi, Izin
from app import db
from flask import jsonify, request, current_app
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import func
from datetime import datetime, time
import os
import time
import traceback

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
    try:
        # data = request.json or request.form
        username = get_jwt_identity()
        foto_izin = request.files.get('foto_izin')

        print(f"[DEBUG] User JWT: {username}")
        
        print(f"[DEBUG] File data: {foto_izin}")

        user_obj = User.query.filter_by(username=username).first()
        if not user_obj:
            return jsonify({"msg": "User tidak ditemukan"}), 404

        tanggal_izin = request.form.get('tanggal_izin')
        keterangan = request.form.get('keterangan')

        print(f"[DEBUG] tanggal_izin: {tanggal_izin}, keterangan: {keterangan}")

        if not tanggal_izin:
            return jsonify({"msg": "Tanggal izin tidak boleh kosong"}), 400

        try:
            tanggal_izin = datetime.strptime(tanggal_izin, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"msg": "Format tanggal salah, gunakan YYYY-MM-DD"}), 400

        if not keterangan:
            keterangan = None

        # Cek izin duplikat
        existing_izin = Izin.query.filter_by(
            id_mr=user_obj.username,
            tanggal_izin=tanggal_izin
        ).first()
        if existing_izin:
            return jsonify({"msg": "Anda sudah mengajukan izin pada tanggal ini"}), 400

        # Proses penyimpanan file foto
        filename = None
        if foto_izin and foto_izin.filename != "":
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)  # pastikan folder ada
            filename = f"izin_{username}_{int(time.time())}.jpg"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            print(f"[DEBUG] Menyimpan foto ke: {file_path}")
            foto_izin.save(file_path)
        else:
            print("[DEBUG] Tidak ada file foto_izin yang dikirim")

        # Buat objek Izin baru
        new_izin = Izin(
            id_mr=user_obj.username,
            tanggal_izin=tanggal_izin,
            status_izin='pending',
            keterangan=keterangan,
            foto_izin_path=filename
        )
        db.session.add(new_izin)
        db.session.commit()

        return jsonify({
            "msg": "Izin berhasil dibuat",
            "name": user_obj.name,
            "izin": new_izin.to_dict()
        }), 201

    except Exception as e:
        print("[ERROR] Exception terjadi di create_izin:")
        traceback.print_exc()  # tampilkan full error di terminal
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500

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

    if newStatus == "approved":
        # ===== AUTO INSERT / UPDATE KE ABSENSI =====
        existing_absen = Absensi.query.filter_by(
            id_mr=izin.id_mr,
            tanggal=izin.tanggal_izin
        ).first()

        if not existing_absen:
            new_absen = Absensi(
                id_mr=izin.id_mr,
                tanggal=izin.tanggal_izin,
                status_absen='izin',
                waktu_absen=None,
                lokasi=None,
                foto_absen_path=izin.foto_izin_path
            )
            db.session.add(new_absen)
        else:
            # Kalau udah ada absensi → update ke izin
            existing_absen.status_absen = "izin"
            existing_absen.waktu_absen = None
            existing_absen.lokasi = None
            existing_absen.foto_absen_path = izin.foto_izin_path

    # kalau rejected → tidak ubah absensi sama sekali

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



# untuk update foto izin, bisa ditambahkan fungsi terpisah jika diperlukan
# misalnya fungsi update_izin_foto(id) yang mirip dengan create_izin tapi hanya untuk foto
# dia sendiri yang bakal update foto nya misal jika dia sakit dan surat izin nyusul atau berubah
def update_photo_by_sales_username(id):
    """Update foto izin oleh sales berdasarkan username."""
    current_user_username = get_jwt_identity()
    # if current_user_username != username:
    #     return jsonify({"msg": "Anda hanya bisa mengupdate foto izin milik Anda sendiri"}), 403
    try:
        foto_izin = request.files.get('foto_izin')
        if not foto_izin:
            return jsonify({"msg": "Foto izin tidak ditemukan dalam request"}), 400
        user_obj = User.query.filter_by(username=current_user_username).first()
        if not user_obj:
            return jsonify({"msg": "User tidak ditemukan"}), 404
        # Simpan foto izin
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)  # pastikan folder ada
        filename = f"izin_{current_user_username}_{int(time.time())}.jpg"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        foto_izin.save(file_path)
        # Update  izin  berdasarkan idnya yang belum disetujui (pending) dengan foto baru
        pending_izins = Izin.query.filter_by(id=id, id_mr=current_user_username).all()
        for izin in pending_izins:
            izin.foto_izin_path = filename
        db.session.commit()
      
        return jsonify({"msg": "Foto izin berhasil diupdate", "filename": filename}), 200
    
    except Exception as e:
    
        print("[ERROR] Exception terjadi di update_photo_by_sales_username:")
        traceback.print_exc()
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500
        