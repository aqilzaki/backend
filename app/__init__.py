from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail() # Buat objek Mail

def create_app():
    app = Flask(__name__,static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static')
  )
    
    CORS(app)
    
    # Konfigurasi aplikasi
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/absensi_sales'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://teke5124_tekmo:Tekno_123@localhost/teke5124_absensi_sales'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Ini memaksa koneksi database untuk menggunakan zona waktu +07:00 (WIB)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {'time_zone': '+07:00'}
    }
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads')
    # (PENTING) Ganti dengan kunci rahasia yang kuat dan acak
    app.config['JWT_SECRET_KEY'] = 'ini kunci rahasia tekmo yang sangat rahasia' 

 # --- KONFIGURASI WAKTU TOKEN ---
    # Atur token agar berlaku selama 1 hari.
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    
 # --- KONFIGURASI FLASK-MAIL ---
    # (PENTING: Gunakan environment variables untuk data sensitif ini di produksi)
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    # Ganti dengan email dan "App Password" Anda
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'aqilzaki54@gmail.com' 
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'nlvw krpu akjg rtqa'

    # Hubungkan ekstensi dengan aplikasi
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app) # Inisialisasi mail dengan app

    # Impor dan daftarkan blueprint
    from app.routes.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Impor model agar terdeteksi oleh Flask-Migrate
    with app.app_context():
        from .models import models

    return app  