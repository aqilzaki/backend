from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.models import Kunjungan, User, Outlet
from sqlalchemy import extract, func
from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt

@jwt_required()
# Di dalam file: app/controllers/kunjungan_controller.py

@jwt_required()

def create_kunjungan():
    """Membuat data kunjungan baru dengan logika untuk prospek."""
    try:
        current_user_id = get_jwt_identity()
        
        # Ambil data dari form
        kegiatan = request.form.get('kegiatan')
        outlet_input = request.form.get('nama_outlet') # Bisa ID atau Nama
        if not outlet_input:
            return jsonify({"message": "Nama/ID Outlet wajib diisi."}), 400
        if not outlet_input or not kegiatan:
            return jsonify({"message": "Nama/ID Outlet dan Kegiatan wajib diisi."}), 400

        outlet_id_to_save = None
        nama_prospek_to_save = None

        # --- LOGIKA BARU BERDASARKAN KEGIATAN ---
        if kegiatan == 'prospek':
            # Jika prospek, kita tidak mencari/membuat outlet.
            # Kita hanya simpan namanya di kolom nama_prospek.
            nama_prospek_to_save = outlet_input
        
        else: # Jika maintenance atau akuisisi
            # Gunakan logika cari atau buat outlet yang sudah ada
            outlet = Outlet.query.filter_by(id_outlet=outlet_input).first()
            if not outlet:
                outlet = Outlet.query.filter_by(nama_outlet=outlet_input).first()

            if not outlet:
                # Jika outlet belum ada, buat baru
                last_outlet = Outlet.query.order_by(Outlet.id.desc()).first()
                if last_outlet and last_outlet.id_outlet.startswith('TM'):
                    last_id_num = int(last_outlet.id_outlet[2:])
                    new_id_num = last_id_num + 1
                    new_id_outlet = f"TM{new_id_num:04d}"
                else:
                    new_id_outlet = "TM0001"
                
                outlet = Outlet(id_outlet=new_id_outlet, nama_outlet=outlet_input)
                db.session.add(outlet)
            
            # Lakukan validasi mingguan HANYA untuk maintenance/akuisisi
            satu_minggu_lalu = datetime.now() - timedelta(days=7)
            kunjungan_terakhir = Kunjungan.query.filter(
                Kunjungan.id_mr == current_user_id,
                Kunjungan.id_outlet == outlet.id_outlet,
                Kunjungan.tanggal_input > satu_minggu_lalu
            ).first()

            if kunjungan_terakhir:
                return jsonify({
                    "message": f"Anda sudah mengunjungi outlet '{outlet.nama_outlet}' dalam seminggu terakhir."
                }), 409
            
            outlet_id_to_save = outlet.id_outlet
        # --- AKHIR LOGIKA BARU ---
        # Ambil data tambahan dari form
        no_visit = request.form.get('no_visit')
        lokasi = request.form.get('lokasi')
        kompetitor = request.form.get('kompetitor')
        rata_rata_topup = float(request.form.get("rata_rata_topup", 0))
        potensi_topup = float(request.form.get("potensi_topup", 0))
        issue = request.form.get('issue')

        # Hitung presentase pemakaian
        if not rata_rata_topup or not potensi_topup:
            presentase_pemakaian = None
        else:
            presentase_pemakaian = ((potensi_topup - rata_rata_topup) / rata_rata_topup) * 100
        

        if not all([no_visit, lokasi, kegiatan]):
            return jsonify({"message": "Data wajib (No. Kunjungan, Lokasi, Kegiatan) tidak lengkap."}), 400

        foto_kunjungan_path = None
        if 'foto_kunjungan' in request.files:
            file = request.files['foto_kunjungan']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                foto_kunjungan_path = filename
        
        new_kunjungan = Kunjungan(
            id_mr=current_user_id,
            id_outlet=outlet_id_to_save,
            nama_prospek=nama_prospek_to_save,
            no_visit=int(no_visit) if no_visit else None,
            lokasi=lokasi,
            kegiatan=kegiatan,
            kompetitor=kompetitor,
            rata_rata_topup=float(rata_rata_topup) if rata_rata_topup else None,
            potensi_topup=float(potensi_topup) if potensi_topup else None,
            presentase_pemakaian=float(presentase_pemakaian) if presentase_pemakaian else None,
            issue=issue,
            foto_kunjungan_path=foto_kunjungan_path
        )

        db.session.add(new_kunjungan)
        db.session.commit()
        return jsonify({"message": "Kunjungan berhasil ditambahkan!", "kunjungan": new_kunjungan.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error saat membuat kunjungan: {e}")
        return jsonify({"message": "Terjadi kesalahan server saat memproses permintaan."}), 500
    
@jwt_required()
def get_all_kunjungan():
    """Mengambil semua data kunjungan, dikelompokkan per tahun, bulan, dan sales."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"message": "Hanya admin yang bisa mengakses fitur ini."}), 403

    # Perbaikan: Query diurutkan berdasarkan tanggal input
    semua_kunjungan = Kunjungan.query.order_by(Kunjungan.tanggal_input.desc()).all()

    if not semua_kunjungan:
        return jsonify({}), 200

    laporan_terstruktur = {}
    for kunjungan in semua_kunjungan:
        tahun = kunjungan.tanggal_input.year
        bulan = kunjungan.tanggal_input.month
        
        # Ambil username dan nama dari relasi
        username = kunjungan.user.username if kunjungan.user else "unknown"
        nama_sales = kunjungan.user.name if kunjungan.user else "Unknown"

        if tahun not in laporan_terstruktur:
            laporan_terstruktur[tahun] = {}
        if bulan not in laporan_terstruktur[tahun]:
            laporan_terstruktur[tahun][bulan] = {}
        if username not in laporan_terstruktur[tahun][bulan]:
            laporan_terstruktur[tahun][bulan][username] = {
                "name": nama_sales,
                "kunjungan_list": []
            }
        
        laporan_terstruktur[tahun][bulan][username]["kunjungan_list"].append(kunjungan.to_dict())

    return jsonify(laporan_terstruktur), 200

@jwt_required()
def get_kunjungan_by_id(id):
    """Mengambil satu data kunjungan berdasarkan ID."""
    kunjungan = Kunjungan.query.get_or_404(id)
    return jsonify(kunjungan.to_dict()), 200

@jwt_required()
def update_kunjungan(id):
    """Memperbarui data kunjungan."""
    kunjungan = Kunjungan.query.get_or_404(id)
    data = request.json

    for key, value in data.items():
        if hasattr(kunjungan, key) and key not in ['id', 'id_mr', 'id_outlet']:
            setattr(kunjungan, key, value)

    db.session.commit()
    return jsonify(kunjungan.to_dict()), 200

@jwt_required()
def delete_kunjungan(id):
    """Menghapus data kunjungan."""
    kunjungan = Kunjungan.query.get_or_404(id)
    
    if kunjungan.foto_kunjungan_path:
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.remove(os.path.join(upload_folder, kunjungan.foto_kunjungan_path))
        except OSError as e:
            print(f"Error deleting file: {e.strerror}")

    db.session.delete(kunjungan)
    db.session.commit()
    return jsonify({'message': f'Kunjungan dengan ID {id} berhasil dihapus.'}), 200

@jwt_required()
def get_kunjungan_by_username():
    """Mengambil data kunjungan untuk user yang sedang login."""
    current_user_id = get_jwt_identity()
    kunjungan_list = Kunjungan.query.filter_by(id_mr=current_user_id).order_by(Kunjungan.tanggal_input.desc()).all()
    
    return jsonify([k.to_dict() for k in kunjungan_list]), 200

@jwt_required()
def get_kunjungan_by_username_for_admin(username):
    """(Admin) Mengambil semua data kunjungan untuk seorang sales spesifik."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify([]), 200 # Kembalikan list kosong jika user tidak ada

    kunjungan_sales = Kunjungan.query.filter_by(id_mr=user.id).order_by(Kunjungan.tanggal_input.desc()).all()
    return jsonify([k.to_dict() for k in kunjungan_sales]), 200