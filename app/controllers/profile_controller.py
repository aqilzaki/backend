from flask import jsonify
from app.models.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

def get_my_profile():
    """Mengambil data profil user yang sedang login."""
    # Ambil username dari token JWT yang dikirim
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    username = claims.get('username', None)
    
    # Cari user di database berdasarkan username tersebut
    user = User.query.filter_by(id=current_user_id).first_or_404()
    
    # Kembalikan data user dalam format JSON
    return jsonify(user.to_dict()), 200