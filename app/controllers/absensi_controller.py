from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, time
import os
from ..models import db, Absensi

def handle_absen():
    id_mr = request.form['id_mr']
    lokasi = request.form.get('lokasi')
    foto = request.files['foto']

    now = datetime.now()
    batas_waktu = time(9, 0)
    status = 'Tepat Waktu' if now.time() <= batas_waktu else 'Terlambat'

    filename = secure_filename(f"absen_{id_mr}_{now.strftime('%Y%m%d%H%M%S')}.jpg")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    foto.save(filepath)

    absen = Absensi(
        id_mr=id_mr,
        lokasi=lokasi,
        waktu_absen=now.time(),
        status_absen=status,
        foto_absen_path=filepath
    )
    db.session.add(absen)
    db.session.commit()
    return jsonify({"message": "Absensi berhasil dicatat", "status": status})