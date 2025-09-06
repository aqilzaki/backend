from flask import request, jsonify
from app import db
from app.models.models import komplainan_customer
from datetime import datetime

# ================== CREATE ==================
def create_complain():
    try:
        data =  request.form or request.json
        produk = data.get("produk")
        nomor_konsumen = data.get("nomor_konsumen")
        nomor_tujuan = data.get("nomor_tujuan")
        status_komplain = data.get("status_komplain", "belum selesai")
        pic_created = data.get("pic_created")
        keterangan = data.get("keterangan")

        if not all([ produk, nomor_konsumen, pic_created]):
            return jsonify({"msg": "Field wajib:  produk, nomor_tujuan,  nomor_konsumen, pic_created"}), 400

        

        complain = komplainan_customer(
            id_mr=('cs'),
            produk=produk,
            nomor_konsumen=nomor_konsumen,
            nomor_tujuan=nomor_tujuan,
            status_komplain=status_komplain,
            created_at=datetime.utcnow(),
            pic_created=pic_created,
            keterangan=keterangan
        )
        db.session.add(complain)
        db.session.commit()

        return jsonify({"msg": "Komplain berhasil dibuat", "data": complain.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Terjadi kesalahan: {str(e)}"}), 500


# ================== UPDATE STATUS ==================
def update_status(id):
    try:
        data = request.get_json(silent=True) or request.form.to_dict()

        status_komplain = data.get("status_komplain")
        pic_updated = data.get("pic_updated")  # siapa yang update
        keterangan = data.get("keterangan")

        if not status_komplain or not pic_updated:
            return jsonify({"msg": "Field wajib: status_komplain & pic_updated"}), 400

        complain = komplainan_customer.query.get(id)
        if not complain:
            return jsonify({"msg": "Komplain tidak ditemukan"}), 404

        complain.status_komplain = status_komplain
        complain.pic_updated = pic_updated
        complain.updated_at = datetime.utcnow()

        if keterangan:
            complain.keterangan = keterangan

        db.session.commit()

        return jsonify({"msg": "Status komplain berhasil diperbarui", "data": complain.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Terjadi kesalahan: {str(e)}"}), 500


# ================== GET ALL ==================
def get_all_complain():
    try:
        complains = komplainan_customer.query.order_by(komplainan_customer.created_at.desc()).all()
        return jsonify([c.to_dict() for c in complains]), 200
    except Exception as e:
        return jsonify({"msg": f"Terjadi error: {str(e)}"}), 500


# ================== GET BY ID ==================
def get_complain_by_id(id):
    try:
        complain = komplainan_customer.query.get(id)
        if not complain:
            return jsonify({"msg": "Komplain tidak ditemukan"}), 404
        return jsonify(complain.to_dict()), 200
    except Exception as e:
        return jsonify({"msg": f"Terjadi error: {str(e)}"}), 500


# ================== DELETE ==================
def delete_complain(id):
    try:
        complain = komplainan_customer.query.get(id)
        if not complain:
            return jsonify({"msg": "Komplain tidak ditemukan"}), 404

        db.session.delete(complain)
        db.session.commit()

        return jsonify({"msg": f"Komplain dengan ID {id} berhasil dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Terjadi error: {str(e)}"}), 500
