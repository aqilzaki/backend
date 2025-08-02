from flask import send_file
import pandas as pd
import io
from datetime import datetime

# Impor model Anda
from app.models.models import Absensi, Kunjungan

def export_absensi_to_excel():
    """Mengekspor semua data absensi ke file Excel."""
    try:
        absensi_list = Absensi.query.all()
        # Jika tidak ada data, kembalikan pesan
        if not absensi_list:
            return "Tidak ada data absensi untuk diekspor.", 404

        # Ubah data menjadi list of dictionaries
        data_to_export = [{
            'ID Absen': a.id,
            'ID Sales': a.id_mr,
            'Username': a.user.username if a.user else 'N/A',
            'Nama Sales': a.user.name if a.user else 'N/A',
            'Tanggal': a.tanggal.strftime('%Y-%m-%d') if a.tanggal else None,
            'Waktu Absen': a.waktu_absen.strftime('%H:%M:%S') if a.waktu_absen else None,
            'Status': a.status_absen
        } for a in absensi_list]
        
        df = pd.DataFrame(data_to_export)
        
        # Buat file Excel di dalam memori
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Laporan Absensi')
        writer.close() # <-- Ganti dari save() menjadi close() untuk versi pandas yang lebih baru
        output.seek(0)
        
        # Buat nama file yang dinamis dengan tanggal
        filename = f"Laporan_Absensi_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename, # <-- Gunakan download_name
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        # Menangani error jika terjadi
        return str(e), 500

def export_kunjungan_to_excel():
    """Mengekspor semua data kunjungan ke file Excel."""
    try:
        kunjungan_list = Kunjungan.query.all()
        if not kunjungan_list:
            return "Tidak ada data kunjungan untuk diekspor.", 404

        df = pd.DataFrame([{
            'ID Kunjungan': k.id,
            'ID Sales': k.id_mr,
            'Username': k.user.username if k.user else 'N/A',
            'Nama Sales': k.user.name if k.user else 'N/A',
            'No Visit': k.no_visit,
            'Outlet': k.nama_outlet,
            'Lokasi': k.lokasi,
            'Kegiatan': k.kegiatan,
            'Kompetitor': k.kompetitor,
            'Rata-rata Topup': k.rata_rata_topup,
            'Potensi Topup': k.potensi_topup,
            'Pemakaian App (%)': k.presentase_pemakaian,
            'Issue': k.issue,
            'Tanggal Input': k.tanggal_input.strftime('%Y-%m-%d %H:%M:%S') if k.tanggal_input else None
        } for k in kunjungan_list])

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Laporan Kunjungan')
        writer.close()
        output.seek(0)
        
        filename = f"Laporan_Kunjungan_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return str(e), 500