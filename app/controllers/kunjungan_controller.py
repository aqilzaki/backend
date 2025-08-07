from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.models import Kunjungan, User
from sqlalchemy import extract
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt # Pastikan jwt_required diimpor

# Asumsi Anda memiliki konfigurasi untuk folder upload di app.config
# Contoh: app.config['UPLOAD_FOLDER'] = 'static/uploads'
# Pastikan folder ini ada dan memiliki izin tulis

def allowed_file(filename):
    # Mengambil ALLOWED_EXTENSIONS dari app.config
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})

@jwt_required() # Melindungi endpoint ini, hanya user terautentikasi yang bisa akses
def create_kunjungan():
    """Membuat data kunjungan baru."""
    try:
        current_user_username = get_jwt_identity() # PERBAIKAN: Typo 'idezntity' menjadi 'identity'
        
        # Mengambil data dari request.form (untuk field teks dari multipart/form-data)
        # Menggunakan .get() dengan default None agar tidak error jika field tidak ada
        no_visit_str = request.form.get('no_visit')
        nama_outlet = request.form.get('nama_outlet')
        lokasi = request.form.get('lokasi')
        kegiatan = request.form.get('kegiatan')
        kompetitor = request.form.get('kompetitor')
        rata_rata_topup_str = request.form.get('rata_rata_topup')
        potensi_topup_str = request.form.get('potensi_topup')
        persentase_pemakaian_str = request.form.get('persentase_pemakaian')
        issue = request.form.get('issue')

        # Validasi dasar data wajib (sesuaikan dengan kebutuhan bisnis Anda)
        if not all([no_visit_str, nama_outlet, lokasi, kegiatan]):
            return jsonify({"message": "Data wajib (No. Kunjungan, Nama Outlet, Lokasi, Kegiatan) tidak lengkap."}), 400

        # Konversi tipe data ke int/float dan tangani kemungkinan ValueError
        try:
            no_visit = int(no_visit_str)
            # Konversi string kosong menjadi None atau 0.0 sebelum ke float
            rata_rata_topup = float(rata_rata_topup_str) if rata_rata_topup_str else None
            potensi_topup = float(potensi_topup_str) if potensi_topup_str else None
            persentase_pemakaian = float(persentase_pemakaian_str) if persentase_pemakaian_str else None
        except ValueError:
            return jsonify({"message": "Format angka tidak valid untuk No. Kunjungan, Rata-rata Top Up, Potensi Top Up, atau Persentase Pemakaian."}), 400

        foto_kunjungan_path = None
        if 'foto_kunjungan' in request.files:
            file = request.files['foto_kunjungan']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Pastikan UPLOAD_FOLDER terkonfigurasi di app.config
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
                os.makedirs(upload_folder, exist_ok=True) # Pastikan folder ada
                
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                foto_kunjungan_path = filename # Simpan nama file saja di DB
            else:
                return jsonify({"message": "Tipe file foto tidak diizinkan atau file kosong."}), 400
        
        # Tanggal input otomatis di backend saat ini
        from datetime import datetime
        tanggal_input_now = datetime.now()

        new_kunjungan = Kunjungan(
            id_mr=current_user_username, # Mengambil dari token JWT
            no_visit=no_visit,
            nama_outlet=nama_outlet,
            lokasi=lokasi,
            kegiatan=kegiatan,
            kompetitor=kompetitor,
            rata_rata_topup=rata_rata_topup,
            potensi_topup=potensi_topup,
            # PERBAIKAN: Menggunakan nama kolom yang benar sesuai database Anda
            presentase_pemakaian=persentase_pemakaian, # Mengubah 'persentase_pemakaian' menjadi 'presentase_pemakaian'
            issue=issue,
            foto_kunjungan_path=foto_kunjungan_path,
            tanggal_input=tanggal_input_now # Set tanggal input di backend
        )

        db.session.add(new_kunjungan)
        db.session.commit()
        return jsonify({"message": "Kunjungan berhasil ditambahkan!", "kunjungan": new_kunjungan.to_dict()}), 201

    except Exception as e:
        db.session.rollback() # Rollback jika ada error database
        print(f"Error saat membuat kunjungan: {e}") # Log error untuk debugging
        return jsonify({"message": "Terjadi kesalahan server saat menambahkan kunjungan."}), 500

@jwt_required() # Melindungi endpoint ini
def get_all_kunjungan():
    """Mengambil semua data kunjungan, dikelompokkan per tahun, bulan, dan sales."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"message": "Hanya admin yang bisa mengakses fitur ini."}), 403

    # Ambil semua data kunjungan, join dengan User, dan urutkan
    semua_kunjungan = Kunjungan.query.join(
        User, Kunjungan.id_mr == User.username
    ).order_by(
        extract('year', Kunjungan.tanggal_input).desc(),
        extract('month', Kunjungan.tanggal_input).desc(),
        Kunjungan.id_mr.asc(),
        Kunjungan.tanggal_input.desc()
    ).all()

    if not semua_kunjungan:
        return jsonify({}), 200

    # Siapkan struktur data akhir
    laporan_terstruktur = {}

    for kunjungan in semua_kunjungan:
        tahun = kunjungan.tanggal_input.year
        bulan = kunjungan.tanggal_input.month
        username = kunjungan.id_mr
        nama_sales = kunjungan.user.name

        # Buat kunci tahun jika belum ada
        if tahun not in laporan_terstruktur:
            laporan_terstruktur[tahun] = {}

        # Buat kunci bulan di dalam tahun jika belum ada
        if bulan not in laporan_terstruktur[tahun]:
            laporan_terstruktur[tahun][bulan] = {}
        
        # Buat kunci username di dalam bulan jika belum ada
        if username not in laporan_terstruktur[tahun][bulan]:
            laporan_terstruktur[tahun][bulan][username] = {
                "name": nama_sales,
                "kunjungan_list": []
            }
        
        # Tambahkan detail kunjungan ke dalam daftar
        kunjungan_dict = kunjungan.to_dict()
        kunjungan_dict['waktu_input'] = kunjungan.tanggal_input.strftime('%Y-%m-%d %H:%M:%S')
        laporan_terstruktur[tahun][bulan][username]["kunjungan_list"].append(kunjungan_dict)

    return jsonify(laporan_terstruktur), 200

@jwt_required() # Melindungi endpoint ini
def get_kunjungan_by_id(id):
    """Mengambil satu data kunjungan berdasarkan ID."""
    kunjungan = Kunjungan.query.get_or_404(id)
    return jsonify(kunjungan.to_dict()), 200

@jwt_required() # Melindungi endpoint ini
def update_kunjungan(id):
    """Memperbarui data kunjungan."""
    kunjungan = Kunjungan.query.get_or_404(id)
    data = request.json # Asumsi update tidak menggunakan multipart/form-data

    for key, value in data.items():
        if hasattr(kunjungan, key):
            setattr(kunjungan, key, value)

    db.session.commit()
    return jsonify(kunjungan.to_dict()), 200

@jwt_required() # Melindungi endpoint ini
def delete_kunjungan(id):
    """Menghapus data kunjungan."""
    kunjungan = Kunjungan.query.get_or_404(id)
    
    if kunjungan.foto_kunjungan_path:
        try:
            # Pastikan UPLOAD_FOLDER terkonfigurasi di app.config
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            os.remove(os.path.join(upload_folder, kunjungan.foto_kunjungan_path))
        except OSError as e:
            print(f"Error deleting file: {e.strerror}") # Log error jika gagal hapus file

    db.session.delete(kunjungan)
    db.session.commit()
    return jsonify({'message': f'Kunjungan dengan ID {id} berhasil dihapus.'}), 200

@jwt_required() # Melindungi endpoint ini
def get_kunjungan_perhari():
    """Mengambil data kunjungan per hari."""
    # Ini mungkin perlu diubah untuk memfilter berdasarkan user yang login
    kunjungan_list = Kunjungan.query.all()
    kunjungan_perhari = {}

    for k in kunjungan_list:
        tanggal = k.tanggal_input.date()
        if tanggal not in kunjungan_perhari:
            kunjungan_perhari[tanggal] = []
        kunjungan_perhari[tanggal].append(k.to_dict())

    return jsonify(kunjungan_perhari), 200

@jwt_required() # Melindungi endpoint ini
def get_kunjungan_by_username():
    """Mengambil data kunjungan berdasarkan username (id_mr)."""
    current_user_username = get_jwt_identity()
    kunjungan_list = Kunjungan.query.filter_by(id_mr=current_user_username).all()
    
    # PERBAIKAN: Hapus baris duplikat ini
    # kunjungan_list = Kunjungan.query.filter_by(id_mr=current_user_username).all() 
    
    if not kunjungan_list:
        # Mengembalikan 200 OK dengan list kosong jika tidak ada kunjungan,
        # atau 404 jika memang tidak ada data sama sekali dan ingin memberi tahu frontend
        return jsonify([]), 200 # Mengembalikan array kosong jika tidak ada data
        # return jsonify({'message': 'Tidak ada kunjungan ditemukan untuk pengguna ini.'}), 404 # Opsi lain

    return jsonify([k.to_dict() for k in kunjungan_list]), 200

def get_kunjungan_by_username_for_admin(username):
    """Mengambil semua data kunjungan untuk seorang sales spesifik."""
    
    # Query semua kunjungan oleh user, diurutkan dari yang paling baru
    kunjungan_sales = Kunjungan.query.filter_by(id_mr=username).order_by(Kunjungan.tanggal_input.desc()).all()

    if not kunjungan_sales:
        # Kembalikan array kosong jika tidak ada kunjungan, bukan error
        return jsonify([]), 200

    # Ubah setiap objek kunjungan menjadi dictionary
    return jsonify([k.to_dict() for k in kunjungan_sales]), 200