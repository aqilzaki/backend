from flask import send_file
import pandas as pd
from ..models import Kunjungan

def export_excel():
    kunjungan_list = Kunjungan.query.all()
    df = pd.DataFrame([{
        'ID MR': k.id_mr,
        'No Visit': k.no_visit,
        'Outlet': k.nama_outlet,
        'Lokasi': k.lokasi,
        'Kegiatan': k.kegiatan,
        'Kompetitor': k.kompetitor,
        'Rata-rata Topup': k.rata_rata_topup,
        'Potensi Topup': k.potensi_topup,
        'Pemakaian App (%)': k.presentase_pemakaian,
        'Issue': k.issue,
        'Tanggal': k.tanggal_input
    } for k in kunjungan_list])

    filepath = 'export_laporan_sales.xlsx'
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)
