from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# 1. Inisialisasi ekstensi di sini, di luar fungsi
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Factory untuk membuat dan mengkonfigurasi aplikasi Flask."""
    app = Flask(__name__)
    
    # 2. Konfigurasi aplikasi
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/absensi_sales'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads')

    # 3. Hubungkan ekstensi dengan aplikasi
    db.init_app(app)
    migrate.init_app(app, db)

    # 4. (KRUSIAL) Impor dan daftarkan blueprint DI DALAM FUNGSI INI
    from app.routes.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # 5. Impor model agar terdeteksi oleh Flask-Migrate
    with app.app_context():
        from .models import models

    return app