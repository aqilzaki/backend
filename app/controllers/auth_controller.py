from flask import request, jsonify
from app import db, bcrypt
from app.models.models import User
from flask_jwt_extended import create_access_token, get_jwt

# Hanya admin yang bisa mendaftarkan user baru
def register_user():
    data = request.get_json()
    username = data.get('username')
    name = data.get('name')
    email = data.get('email')
    lokasi = data.get('lokasi', None)  # Lokasi bisa diisi atau tidak
    password = data.get('password')
    role = data.get('role', 'sales') # default role is 'sales'

    if not username or not password or not email:
        return jsonify({"msg": "Username, password dan email dibutuhkan"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username sudah ada"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "email sudah ada"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, name=name, email=email, password_hash=hashed_password, role=role, lokasi=lokasi)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": f"User {username} untuk berhasil dibuat"}), 201


def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username dan password dibutuhkan"}), 400

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        # Buat token dengan role di dalamnya
        additional_claims = {"role": user.role,
                             "name": user.name}
        access_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        return jsonify(access_token=access_token, role=user.role, username=user.username, name=user.name), 200

    return jsonify({"msg": "Username atau password salah"}), 401