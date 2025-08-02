from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    CORS(app)
    
    # Konfigurasi aplikasi
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/absensi_sales'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Ini memaksa koneksi database untuk menggunakan zona waktu +07:00 (WIB)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {'time_zone': '+07:00'}
    }
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads')
    # (PENTING) Ganti dengan kunci rahasia yang kuat dan acak
    app.config['JWT_SECRET_KEY'] = 'ini kunci rahasia tekmo yang sangat rahasia' 

    # Hubungkan ekstensi dengan aplikasi
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Impor dan daftarkan blueprint
    from app.routes.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Impor model agar terdeteksi oleh Flask-Migrate
    with app.app_context():
        from .models import models

    return app  