from flask import Blueprint
from app.controllers import absensi_controller, kunjungan_controller, export_controller

bp = Blueprint('main', __name__)

# --- Rute untuk Absensi ---
@bp.route('/absensi', methods=['POST'])
def create_absensi_route():
    return absensi_controller.create_absensi()

@bp.route('/absensi', methods=['GET'])
def get_all_absensi_route():
    return absensi_controller.get_all_absensi()

@bp.route('/absensi/<int:id>', methods=['GET'])
def get_absensi_by_id_route(id):
    return absensi_controller.get_absensi_by_id(id)

@bp.route('/absensi/<int:id>', methods=['PUT'])
def update_absensi_route(id):
    return absensi_controller.update_absensi(id)

@bp.route('/absensi/<int:id>', methods=['DELETE'])
def delete_absensi_route(id):
    return absensi_controller.delete_absensi(id)


# --- Rute untuk Kunjungan ---
@bp.route('/kunjungan', methods=['POST'])
def create_kunjungan_route():
    return kunjungan_controller.create_kunjungan()

@bp.route('/kunjungan', methods=['GET'])
def get_all_kunjungan_route():
    return kunjungan_controller.get_all_kunjungan()

@bp.route('/kunjungan/<int:id>', methods=['GET'])
def get_kunjungan_by_id_route(id):
    return kunjungan_controller.get_kunjungan_by_id(id)

@bp.route('/kunjungan/<int:id>', methods=['PUT'])
def update_kunjungan_route(id):
    return kunjungan_controller.update_kunjungan(id)

@bp.route('/kunjungan/<int:id>', methods=['DELETE'])
def delete_kunjungan_route(id):
    return kunjungan_controller.delete_kunjungan(id)


# --- Rute untuk Export ---
# (Rute ini sudah ada sebelumnya, kita biarkan saja)
@bp.route('/export/absensi', methods=['GET'])
def export_absensi_route():
    return export_controller.export_absensi_to_excel()

@bp.route('/export/kunjungan', methods=['GET'])
def export_kunjungan_route():
    return export_controller.export_kunjungan_to_excel()