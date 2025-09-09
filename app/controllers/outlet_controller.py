from flask import request, jsonify
from app import db
from app.models.models import Outlet, Kunjungan, User
from datetime import datetime, timedelta
from sqlalchemy import or_, and_

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

def search_outlets():
    query = request.args.get("query", "").strip()
    date_filter = request.args.get("date", "").strip()
    
    q = db.session.query(
        Outlet.id_outlet,
        Outlet.nama_outlet,
        Outlet.created_at.label("tgl_bergabung"),
        Kunjungan.id_mr,
        User.name.label("nama_sales")
    ).outerjoin(Kunjungan, Kunjungan.id_outlet == Outlet.id_outlet
    ).outerjoin(User, User.username == Kunjungan.id_mr)
    
    if query:
        q = q.filter(
            or_(
                Outlet.id_outlet.ilike(f"%{query}%"),
                Outlet.nama_outlet.ilike(f"%{query}%"),
                Kunjungan.id_mr.ilike(f"%{query}%"),
                User.name.ilike(f"%{query}%")
            )
        )
    
    if date_filter:
        today = datetime.today().date()
        if date_filter == "today":
            start = today
            end = today
        elif date_filter == "yesterday":
            start = today - timedelta(days=1)
            end = start
        elif date_filter == "day_after":
            start = today + timedelta(days=2)
            end = start
        q = q.filter(
            and_(
                Outlet.created_at >= start,
                Outlet.created_at <= end
            )
        )
    
    results = q.order_by(Outlet.created_at.desc()).all()
    
    outlet_list = [
        {
            "id_outlet": r.id_outlet,
            "nama_outlet": r.nama_outlet,
            "id_mr": r.id_mr,
            "nama_mr": r.nama_sales,
            "tgl_bergabung": r.tgl_bergabung.strftime("%Y-%m-%d") if r.tgl_bergabung else None
        }
        for r in results
    ]
    return jsonify(outlet_list)

def get_all_outlets_with_details():
    """
    Ambil semua outlet lengkap dengan id_outlet, nama_outlet, id_mr, nama_sales, dan tgl_bergabung,
    urutkan terbaru di atas
    """
    try:
        results = (
            db.session.query(
                Outlet.id_outlet,
                Outlet.nama_outlet,
                Outlet.created_at.label("tgl_bergabung"),
                Kunjungan.id_mr,
                User.name.label("nama_sales")
            )
            .outerjoin(Kunjungan, Kunjungan.id_outlet == Outlet.id_outlet)
            .outerjoin(User, User.username == Kunjungan.id_mr)
            .order_by(Outlet.created_at.desc())  # urutkan terbaru di atas
            .all()
        )

        outlet_list = []
        for row in results:
            outlet_list.append({
                "id_outlet": row.id_outlet,
                "nama_outlet": row.nama_outlet,
                "id_mr": row.id_mr if row.id_mr else None,
                "nama_mr": row.nama_sales if row.nama_sales else None,
                "tgl_bergabung": row.tgl_bergabung.strftime('%d/%m/%Y') if row.tgl_bergabung else None
            })

        return jsonify(outlet_list), 200

    except Exception as e:
        return jsonify({"msg": "Gagal mengambil data outlet", "error": str(e)}), 500

