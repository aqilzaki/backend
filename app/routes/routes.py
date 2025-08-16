from flask import Blueprint
from app.controllers import outlet_controller, izin_controller, tracking_controller, report_controller, auth_controller,  absensi_controller, kunjungan_controller, export_controller, profile_controller
from flask_jwt_extended import jwt_required
from app.decorators import admin_required
import os
from flask import jsonify, request, current_app

bp = Blueprint('main', __name__)

# --- Rute untuk Otentikasi & User Management ---
@bp.route('/register', methods=['POST'])
@jwt_required()
@admin_required()
def register_route():
    return auth_controller.register_user()

@bp.route('/login', methods=['POST'])
def login_route():
    return auth_controller.login_user()

@bp.route('/update_password_by_sales/<username>', methods=['PUT'])
@jwt_required()
@admin_required()  # Hanya admin yang bisa akses
def update_password_by_admin_route(username):   
    return auth_controller.update_password(username)

#  --- Rute untuk Izin ---
@bp.route('/izin', methods=['GET'])
@jwt_required()
def get_all_izin_route():
    return izin_controller.get_all_izin()

@bp.route('/izin/<int:id>', methods=['GET'])
@jwt_required()
def get_izin_by_id_route(id):
    return izin_controller.get_izin_by_id(id)

@bp.route('/izin', methods=['POST'])
@jwt_required() 
def create_izin_route():
    return izin_controller.create_izin()

@bp.route('/izin/<int:id>/<string:newStatus>', methods=['PUT'])
@jwt_required()
@admin_required()  # Hanya admin yang bisa akses
def update_izin_status_route(id,newStatus):
    return izin_controller.update_izin_status(id, newStatus)

@bp.route('/izin/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()  # Hanya admin yang bisa akses
def delete_izin_route(id):
    return izin_controller.delete_izin(id)


# --- Rute untuk Absensi ---
@bp.route('/absensi/personal', methods=['GET'])
@jwt_required()
def absensi_personal_route():
    return absensi_controller.get_all_absensi_by_user()

@bp.route('/absensi', methods=['POST'])
@jwt_required()
def create_absensi_route():
    return absensi_controller.create_absensi()

@bp.route('/absensi', methods=['GET'])
@jwt_required()
def get_all_absensi_route():
    return absensi_controller.get_all_absensi()

@bp.route('/absensi/<int:id>', methods=['GET'])
@jwt_required()
def get_absensi_by_id_route(id):
    return absensi_controller.get_absensi_by_id(id)

@bp.route('/absensi/<int:id>', methods=['PUT'])
@jwt_required()
def update_absensi_route(id):
    return absensi_controller.update_absensi(id)

@bp.route('/absensi/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_absensi_route(id):
    return absensi_controller.delete_absensi(id)


# --- Rute untuk Kunjungan ---
@bp.route('/kunjungan', methods=['POST'])
@jwt_required()
def create_kunjungan_route():
    return kunjungan_controller.create_kunjungan()

@bp.route('/kunjungan', methods=['GET'])
@jwt_required()
def get_all_kunjungan_route():
    return kunjungan_controller.get_all_kunjungan()

@bp.route('/kunjungan/<int:id>', methods=['GET'])
@jwt_required()
def get_kunjungan_by_id_route(id):
    return kunjungan_controller.get_kunjungan_by_id(id)

@bp.route('/kunjungan/<int:id>', methods=['PUT'])
@jwt_required()
def update_kunjungan_route(id):
    return kunjungan_controller.update_kunjungan(id)

@bp.route('/kunjungan/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_kunjungan_route(id):
    return kunjungan_controller.delete_kunjungan(id)

@bp.route('/kunjungan/personal', methods=['GET'])
@jwt_required()
def get_kunjungan_by_username_route():
    return kunjungan_controller.get_kunjungan_by_username()

#--- rute kunjungan untuk admin ---
@bp.route('/admin/kunjungan-sales/<int:username>', methods=['GET'])
@jwt_required()
@admin_required()  # Hanya admin yang bisa akses
def get_kunjungan_by_sales_route(username):
    return kunjungan_controller.get_kunjungan_by_username_for_admin(username)




# --- Rute untuk Export ---
@bp.route('/export/absensi', methods=['GET'])
@jwt_required()
@admin_required()
def export_absensi_route():
    return export_controller.export_absensi_to_excel()

@bp.route('/export/kunjungan', methods=['GET'])
@jwt_required()
@admin_required()
def export_kunjungan_route():
    return export_controller.export_kunjungan_to_excel()




# --- Rute Laporan Sales (Tidak Berubah) ---
@bp.route('/report/daily', methods=['GET'])
@jwt_required()
def daily_report_route():
    return report_controller.get_daily_report()

@bp.route('/report/monthly/<int:year>/<int:month>', methods=['GET'])
@jwt_required()
def monthly_report_route(year, month):
    return report_controller.get_monthly_report(year, month)

@bp.route('/report/yearly/<int:year>', methods=['GET'])
@jwt_required()
def yearly_report_route(year):
    return report_controller.get_yearly_report(year)

# --- Rute untuk Profil ---
@bp.route('/profile', methods=['GET'])
@jwt_required() # Pastikan hanya user yang sudah login bisa akses
def get_profile_route():
    return profile_controller.get_my_profile()

@bp.route('/profile/update', methods=['PUT'])
@jwt_required()
def update_profile_route():
    return profile_controller.update_my_profile()

@bp.route('/profile/change-password', methods=['PUT'])
@jwt_required()
def change_password_route():
    return profile_controller.change_my_password()


@bp.route('/forgot-password', methods=['POST'])
def forgot_password_route():
    return profile_controller.forgot_password()

@bp.route('/reset-password', methods=['POST'])
def reset_password_route():
    return profile_controller.reset_password()



# --- Rute Laporan KHUSUS ADMIN ---

# Rute untuk melihat laporan bulanan sales tertentu
@bp.route('/admin/report/monthly/<int:year>/<int:month>/<string:username>', methods=['GET'])
@jwt_required()
@admin_required() # Hanya admin yang bisa akses
def admin_user_monthly_report_route(year, month, username):
    return report_controller.get_admin_monthly_report(year, month, username)

@bp.route('/admin/report/daily/all/<string:date_str>', methods=['GET'])
@jwt_required()
@admin_required() # Hanya admin yang bisa akses
def admin_daily_report_route(date_str):
    return report_controller.get_admin_daily_report_all_sales(date_str)

# Rute untuk melihat rekapitulasi semua sales dalam satu bulan
@bp.route('/admin/report/summary/monthly/<int:year>/<int:month>', methods=['GET'])
@jwt_required()
@admin_required() # Hanya admin yang bisa akses
def admin_summary_monthly_report_route(year, month):
    return report_controller.get_admin_all_sales_summary(year, month)

# Rute BARU untuk melihat rekapitulasi tahunan semua sales
@bp.route('/admin/report/summary/yearly/<int:year>', methods=['GET'])
@jwt_required()
@admin_required() # Hanya admin yang bisa akses
def admin_summary_yearly_report_route(year):
    return report_controller.get_admin_yearly_summary(year)

@bp.route('/admin/get-users', methods=['GET'])
@jwt_required()
@admin_required()  # Hanya admin yang bisa akses
def get_all_users_route():
    return auth_controller.get_all_users()

@bp.route('/admin/get-user/<string:username>', methods=['GET'])
@jwt_required()
@admin_required()  # Hanya admin yang bisa akses
def get_user_by_username_route(username):
    return auth_controller.get_user_by_username(username)

@bp.route('/admin/delete-user/<string:username>', methods=['DELETE'])
@jwt_required()
@admin_required()  # Hanya admin yang bisa akses
def delete_user_route(username):
    return auth_controller.delete_user(username)


# --- Rute untuk Tracking & Pemetaan (KHUSUS ADMIN) ---
@bp.route('/admin/tracking/daily/<string:username>/<string:date_str>', methods=['GET'])
@jwt_required()
@admin_required() # Pastikan hanya admin yang bisa akses
def daily_tracking_route(username, date_str):
    return tracking_controller.get_daily_tracking_data(username, date_str)

@bp.route('/admin/tracking/daily/all/<string:date_str>', methods=['GET'])
@jwt_required()
@admin_required() # Pastikan hanya admin yang bisa akses
def daily_tracking_all_route(date_str):
    return tracking_controller.get_daily_tracking_all_data(date_str)


# --- Rute CRUD untuk Outlet (KHUSUS ADMIN) ---

@bp.route('/outlets', methods=['POST'])
@jwt_required()
@admin_required()
def create_outlet_route():
    return outlet_controller.create_outlet()

@bp.route('/outlets', methods=['GET'])
@jwt_required()
def get_all_outlets_route():
    return outlet_controller.get_all_outlets()

@bp.route('/outlets/<int:outlet_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_outlet_by_id_route(outlet_id):
    return outlet_controller.get_outlet_by_id(outlet_id)

@bp.route('/outlets/<int:outlet_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_outlet_route(outlet_id):
    return outlet_controller.update_outlet(outlet_id)

@bp.route('/outlets/<int:outlet_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_outlet_route(outlet_id):
    return outlet_controller.delete_outlet(outlet_id)