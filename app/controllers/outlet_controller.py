from flask import request, jsonify
from app import db
from app.models.models import Outlet, Kunjungan

def create_outlet():
    """Membuat outlet baru (Admin Only)."""
    data = request.get_json()
    nama_outlet = data.get('nama_outlet')
    lokasi = data.get('lokasi')

    if not nama_outlet:
        return jsonify({"msg": "Nama outlet wajib diisi."}), 400

    # Cek duplikasi berdasarkan nama
    if Outlet.query.filter_by(nama_outlet=nama_outlet).first():
        return jsonify({"msg": f"Outlet dengan nama '{nama_outlet}' sudah ada."}), 409

    # Logika untuk membuat id_outlet baru secara otomatis
    last_outlet = Outlet.query.order_by(Outlet.id.desc()).first()
    if last_outlet and last_outlet.id_outlet.startswith('TM'):
        try:
            last_id_num = int(last_outlet.id_outlet[2:])
            new_id_num = last_id_num + 1
            new_id_outlet = f"TM{new_id_num:04d}"
        except (ValueError, IndexError):
            # Fallback jika format id_outlet tidak terduga
            new_id_outlet = f"TM{last_outlet.id + 1:04d}"
    else:
        # Jika ini adalah outlet pertama di database
        new_id_outlet = "TM0001"

    new_outlet = Outlet(
        id_outlet=new_id_outlet,
        nama_outlet=nama_outlet,
        lokasi=lokasi
    )
    db.session.add(new_outlet)
    db.session.commit()

    return jsonify(new_outlet.to_dict()), 201

def get_all_outlets():
    """Mengambil semua data outlet (ID dan Nama) yang unik dari database."""
    try:
        # Query untuk mengambil ID dan Nama outlet unik
        # Kita kelompokkan berdasarkan ID untuk memastikan setiap outlet hanya muncul sekali
        outlets = db.session.query(
            Outlet.id_outlet, 
            Outlet.nama_outlet,
            Outlet.lokasi
        ).distinct(Outlet.id_outlet).all()
        
        # Ubah hasil query menjadi list of objects
        outlet_list = [
            {"id": outlet.id_outlet, "name": outlet.nama_outlet, "lokasi":outlet.lokasi} for outlet in outlets
        ]
        
        return jsonify(outlet_list), 200
    except Exception as e:
        return jsonify({"msg": "Gagal mengambil data outlet", "error": str(e)}), 500

def get_outlet_by_id(outlet_id):
    """Mengambil satu outlet berdasarkan ID (int) atau id_outlet (string)."""
    # Coba cari berdasarkan ID (angka) dulu
    outlet = db.session.get(Outlet, outlet_id)
    # Jika tidak ketemu, coba cari berdasarkan id_outlet (string)
    if not outlet:
        outlet = Outlet.query.filter_by(id_outlet=str(outlet_id)).first()
    
    if not outlet:
        return jsonify({"msg": "Outlet tidak ditemukan."}), 404
        
    return jsonify(outlet.to_dict()), 200

def update_outlet(outlet_id):
    """Memperbarui data outlet (Admin Only)."""
    outlet = db.session.get(Outlet, outlet_id)
    if not outlet:
        return jsonify({"msg": "Outlet tidak ditemukan."}), 404

    data = request.get_json()
    
    # Update field jika ada di data request
    outlet.nama_outlet = data.get('nama_outlet', outlet.nama_outlet)
    outlet.lokasi = data.get('lokasi', outlet.lokasi)
    
    db.session.commit()
    return jsonify(outlet.to_dict()), 200

def delete_outlet(outlet_id):
    """Menghapus outlet (Admin Only)."""
    outlet = db.session.get(Outlet, outlet_id)
    if not outlet:
        return jsonify({"msg": "Outlet tidak ditemukan."}), 404
        
    # Cek apakah outlet ini masih digunakan di tabel Kunjungan
    kunjungan_terkait = Kunjungan.query.filter_by(outlet_id=outlet.id).first()
    if kunjungan_terkait:
        return jsonify({
            "msg": "Outlet tidak bisa dihapus karena masih memiliki data kunjungan terkait."
        }), 409

    db.session.delete(outlet)
    db.session.commit()
    return jsonify({"msg": f"Outlet '{outlet.nama_outlet}' berhasil dihapus."}), 200