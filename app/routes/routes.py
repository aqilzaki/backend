from flask import Blueprint
from app.controllers.absensi_controller import handle_absen
from app.controllers.kunjungan_controller import handle_kunjungan
from app.controllers.export_controller import export_excel

bp = Blueprint('main', __name__)

bp.route('/absensi', methods=['POST'])(handle_absen)
bp.route('/kunjungan', methods=['POST'])(handle_kunjungan)
bp.route('/laporan/export', methods=['GET'])(export_excel)
