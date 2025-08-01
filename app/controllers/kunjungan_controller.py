from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
# Ganti dengan dua baris ini:
from app import db
from app.models.models import Kunjungan 

def handle_kunjungan():
    data = request.form
    foto = request.files['foto']
    now = datetime.now()

    filename = secure_filename(f"kunjungan_{data['id_mr']}_{now.strftime('%Y%m%d%H%M%S')}.jpg")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    foto.save(filepath)

    kunjungan = Kunjungan(
        id_mr=data['id_mr'],
        no_visit=data['no_visit'],
        nama_outlet=data['nama_outlet'],
        lokasi=data.get('lokasi'),
        foto_kunjungan_path=filepath,
        kegiatan=data['kegiatan'],
        kompetitor=data.get('kompetitor'),
        rata_rata_topup=data.get('rata_rata_topup'),
        potensi_topup=data.get('potensi_topup'),
        presentase_pemakaian=data.get('presentase_pemakaian'),
        issue=data.get('issue')
    )
    db.session.add(kunjungan)
    db.session.commit()
    return jsonify({"message": "Kunjungan berhasil dicatat"})
