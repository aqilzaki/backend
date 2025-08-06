from flask import request, jsonify
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app import db, mail, bcrypt
from app.models.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

# Buat serializer untuk token reset password yang aman
# Gunakan kunci rahasia yang sama dengan JWT untuk konsistensi
serializer = URLSafeTimedSerializer(os.environ.get('JWT_SECRET_KEY') or 'ganti-dengan-kunci-rahasia-anda-yang-sangat-aman')

def get_my_profile():
    """Mengambil data profil user yang sedang login."""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict()), 200

def update_my_profile():
    """Memperbarui data profil (email, no telpon) untuk user yang sedang login."""
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "User tidak ditemukan"}), 404

    data = request.get_json()
    new_email = data.get('email')
    new_phone = data.get('telpon')

    # Validasi email jika diubah
    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({"msg": "Email sudah digunakan oleh user lain"}), 400
        user.email = new_email

    if new_phone:
        user.telpon = new_phone
    
    db.session.commit()
    return jsonify({"msg": "Profil berhasil diperbarui"}), 200

def change_my_password():
    """Mengubah password untuk user yang sedang login."""
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "User tidak ditemukan"}), 404

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"msg": "Password lama dan baru wajib diisi"}), 400

    # Cek apakah password lama cocok
    if not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"msg": "Password lama salah"}), 401

    # Hash password baru dan simpan
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    
    db.session.commit()
    return jsonify({"msg": "Password berhasil diubah"}), 200


def forgot_password():
    """Membuat dan mengirim token reset password ke email pengguna."""
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        # Untuk keamanan, jangan beri tahu jika email tidak ada.
        return jsonify({"msg": "Jika email Anda terdaftar, Anda akan menerima instruksi reset password."}), 200

    # Buat token yang berlaku selama 1 jam (3600 detik)
    token = serializer.dumps(user.email, salt='email-reset-salt')

    # Buat email
    msg = Message('Reset Password Aplikasi Sales',
                  sender='noreply@aplikasisales.com',
                  recipients=[user.email])
    
    # Link ini idealnya mengarah ke halaman frontend Anda
    link = f"http://localhost:3000/reset-password?token={token}"
    msg.body = f"Untuk mereset password Anda, silakan klik link berikut. Link ini hanya berlaku selama 1 jam ya:\n\n{link}"

    try:
        mail.send(msg)
        return jsonify({"msg": "Email instruksi telah dikirim."}), 200
    except Exception as e:
        return jsonify({"msg": "Gagal mengirim email.", "error": str(e)}), 500

def reset_password():
    """Mengganti password pengguna menggunakan token yang valid."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"msg": "Token dan password baru dibutuhkan"}), 400

    try:
        # Verifikasi token, dengan masa berlaku 1 jam
        email = serializer.loads(token, salt='email-reset-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({"msg": "Token sudah kadaluwarsa!"}), 400
    except Exception:
        return jsonify({"msg": "Token tidak valid!"}), 400

    user = User.query.filter_by(email=email).first_or_404()
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password_hash = hashed_password
    db.session.commit()

    return jsonify({"msg": "Password berhasil direset. Silakan login."}), 200