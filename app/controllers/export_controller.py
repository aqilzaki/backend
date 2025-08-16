from flask import send_file
import pandas as pd
import io
from datetime import datetime
from app.models.models import Absensi, Kunjungan
from geopy.geocoders import Nominatim
from functools import lru_cache
import time

# Inisialisasi geolocator
geolocator = Nominatim(user_agent="export_excel_app")

# Cache hasil pencarian supaya koordinat yang sama tidak dipanggil ulang
@lru_cache(maxsize=500)
def get_address_from_coords(lat, lon):
    try:
        # Delay kecil untuk hindari rate limit OSM
        time.sleep(1)
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10, language="id")
        if location and location.address:
            # Ambil hanya nama jalan jika tersedia
            jalan = location.raw.get("address", {}).get("road")
            if jalan:
                return jalan
            return location.address
        return "-"
    except Exception as e:
        print(f"[ERROR] Gagal mendapatkan alamat: {e}")
        return "-"

# ===========================
# Export Data Absensi
# ===========================
def export_absensi_to_excel():
    try:
        absensi_list = Absensi.query.all()
        if not absensi_list:
            return "Tidak ada data absensi untuk diekspor.", 404

        # Data utama
        data_to_export = []
        for idx, a in enumerate(absensi_list, 1):
            data_to_export.append({
                'No': idx,
                'ID Absen': a.id,
                'ID Sales': a.id_mr,
                'Username': a.user.username if a.user else '-',
                'Nama Sales': a.user.name if a.user else '-',
                'Tanggal': a.tanggal.strftime('%d/%m/%Y') if a.tanggal else '-',
                'Hari': a.tanggal.strftime('%A') if a.tanggal else '-',
                'Waktu Absen': a.waktu_absen.strftime('%H:%M:%S') if a.waktu_absen else '-',
                'Status Kehadiran': a.status_absen or '-'
            })

        df = pd.DataFrame(data_to_export)

        # Summary statistik
        total = len(absensi_list)
        hadir = sum(1 for a in absensi_list if a.status_absen == 'Hadir')
        terlambat = sum(1 for a in absensi_list if a.status_absen == 'Terlambat')

        summary_data = [
            {"Metrik": "Total Absensi", "Jumlah": total, "Persentase": "100%"},
            {"Metrik": "Hadir Tepat Waktu", "Jumlah": hadir, "Persentase": f"{(hadir/total*100):.1f}%"},
            {"Metrik": "Terlambat", "Jumlah": terlambat, "Persentase": f"{(terlambat/total*100):.1f}%"}
        ]
        summary_df = pd.DataFrame(summary_data)

        # Buat file Excel multi-sheet
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data Absensi')
            summary_df.to_excel(writer, index=False, sheet_name='Ringkasan')

        output.seek(0)
        filename = f"Laporan_Absensi_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        return send_file(output, as_attachment=True, download_name=filename,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return str(e), 500


# ===========================
# Export Data Kunjungan
# ===========================
def export_kunjungan_to_excel():
    try:
        kunjungan_list = Kunjungan.query.all()
        if not kunjungan_list:
            return "Tidak ada data kunjungan untuk diekspor.", 404

        data_to_export = []
        for idx, k in enumerate(kunjungan_list, 1):
            # Ambil koordinat dari k.lokasi jika formatnya "lat,lon"
            alamat = "-"
            if k.lokasi and "," in k.lokasi:
                try:
                    lat, lon = map(str.strip, k.lokasi.split(","))
                    alamat = get_address_from_coords(lat, lon)
                except:
                    alamat = k.lokasi
            else:
                alamat = k.lokasi or "-"

            data_to_export.append({
                'No': idx,
                'ID Kunjungan': k.id,
                'ID Sales': k.id_mr,
                'Nama Sales': k.user.name if k.user else '-',
                'Outlet': k.outlet.nama_outlet if k.outlet else '-',
                'Lokasi (Koordinat)': k.lokasi or '-',
                'Alamat Jalan': alamat,
                'Kegiatan': k.kegiatan or '-',
                'Kompetitor': k.kompetitor or '-',
                'Rata-rata Topup (Rp)': k.rata_rata_topup or 0,
                'Potensi Topup (Rp)': k.potensi_topup or 0,
                'Pemakaian App (%)': k.presentase_pemakaian or 0,
                'Issue': k.issue or '-',
                'Tanggal Kunjungan': k.tanggal_input.strftime('%d/%m/%Y %H:%M:%S') if k.tanggal_input else '-'
            })

        df = pd.DataFrame(data_to_export)

        # Summary berdasarkan sales
        summary_data = df.groupby('Nama Sales').agg({
            'ID Kunjungan': 'count',
            'Potensi Topup (Rp)': 'sum',
            'Rata-rata Topup (Rp)': 'mean',
            'Pemakaian App (%)': 'mean'
        }).reset_index().rename(columns={
            'ID Kunjungan': 'Total Kunjungan',
            'Potensi Topup (Rp)': 'Total Potensi Topup',
            'Rata-rata Topup (Rp)': 'Rata-rata Topup',
            'Pemakaian App (%)': 'Rata-rata Pemakaian App (%)'
        })

        # Buat file Excel multi-sheet
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data Kunjungan')
            summary_data.to_excel(writer, index=False, sheet_name='Ringkasan Per Sales')

        output.seek(0)
        filename = f"Laporan_Kunjungan_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        return send_file(output, as_attachment=True, download_name=filename,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return str(e), 500
