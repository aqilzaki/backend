from app import create_app, db
from app.models.models import Absensi, Kunjungan # <-- Baris ini PENTING

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Absensi': Absensi, 'Kunjungan': Kunjungan}