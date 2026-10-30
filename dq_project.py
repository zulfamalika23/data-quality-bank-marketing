"""
Proyek Portofolio Data Governance: Data Quality Assessment
Dataset : UCI Bank Marketing (bank-additional-full.csv, pemisah ';')
Output  : dq_report.xlsx (kamus data, hasil aturan DQ sebelum/sesudah, lineage)
          bank_clean.csv (data setelah pembersihan)

Versi 2: laporan Excel dirapikan (lebar kolom otomatis) dan sheet Kamus_Data memakai kamus lengkap
(kategori UU PDP, klasifikasi, pemilik CONTOH). Hasil aturan DQ sama dengan versi 1.

Cara pakai:
    pip install pandas openpyxl
    python dq_project.py bank-additional-full.csv
"""
import sys
import pandas as pd
import numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else "bank-additional-full.csv"

# ---------------------------------------------------------------- kamus data
DICT = [
    ('age', 'integer', 'Usia nasabah (tahun)', '17-100', 'V1', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Usia tidak disebut eksplisit di UU; menjadi data pribadi bila digabung dengan atribut lain', 'CONTOH: Data Owner - Retail Banking'),
    ('job', 'kategori', 'Jenis pekerjaan', 'daftar kategori baku', 'K-job', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Sama: bagian dari kombinasi atribut yang dapat mengidentifikasi', 'CONTOH: Data Owner - Retail Banking'),
    ('marital', 'kategori', 'Status perkawinan', 'divorced, married, single', 'K-marital', 'Umum: status perkawinan (Pasal 4 ayat 3)', 'Internal', 'Status perkawinan disebut eksplisit sebagai data pribadi umum', 'CONTOH: Data Owner - Retail Banking'),
    ('education', 'kategori', 'Tingkat pendidikan', 'daftar kategori baku', 'K-education', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Bagian dari kombinasi atribut', 'CONTOH: Data Owner - Retail Banking'),
    ('default', 'kategori', 'Punya kredit macet?', 'no, yes', 'K-default', 'Spesifik: data keuangan pribadi (Pasal 4 ayat 2)', 'Rahasia', 'Menggambarkan riwayat kredit pribadi (interpretasi data keuangan pribadi)', 'CONTOH: Data Owner - Risk Management'),
    ('housing', 'kategori', 'Punya kredit rumah?', 'no, yes', 'K-housing', 'Spesifik: data keuangan pribadi (Pasal 4 ayat 2)', 'Rahasia', 'Menggambarkan kewajiban keuangan pribadi (interpretasi)', 'CONTOH: Data Owner - Risk Management'),
    ('loan', 'kategori', 'Punya pinjaman pribadi?', 'no, yes', 'K-loan', 'Spesifik: data keuangan pribadi (Pasal 4 ayat 2)', 'Rahasia', 'Menggambarkan kewajiban keuangan pribadi (interpretasi)', 'CONTOH: Data Owner - Risk Management'),
    ('contact', 'kategori', 'Jenis kontak kampanye', 'cellular, telephone', '-', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('month', 'kategori', 'Bulan kontak terakhir', 'jan-dec', 'V4', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('day_of_week', 'kategori', 'Hari kontak terakhir', 'mon-fri', 'V5', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('duration', 'integer', 'Durasi kontak terakhir (detik)', '≥ 0', 'V2', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('campaign', 'integer', 'Jumlah kontak pada kampanye ini', '≥ 1', 'V3', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('pdays', 'integer', 'Hari sejak kontak kampanye sebelumnya (999 = belum pernah)', '0-999', 'V7, C1', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('previous', 'integer', 'Jumlah kontak sebelum kampanye ini', '≥ 0', 'C1, C2', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('poutcome', 'kategori', 'Hasil kampanye sebelumnya', 'failure, nonexistent, success', 'C2', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Catatan interaksi pemasaran per nasabah', 'CONTOH: Data Owner - Marketing'),
    ('emp.var.rate', 'desimal', 'Tingkat variasi pekerjaan (indikator makro, kuartalan)', 'numerik', '-', 'Bukan data pribadi', 'Publik', 'Indikator ekonomi makro, bukan atribut individu', 'CONTOH: Data Steward - Riset Ekonomi'),
    ('cons.price.idx', 'desimal', 'Indeks harga konsumen (bulanan)', 'numerik', '-', 'Bukan data pribadi', 'Publik', 'Indikator ekonomi makro, bukan atribut individu', 'CONTOH: Data Steward - Riset Ekonomi'),
    ('cons.conf.idx', 'desimal', 'Indeks kepercayaan konsumen (bulanan)', 'numerik', '-', 'Bukan data pribadi', 'Publik', 'Indikator ekonomi makro, bukan atribut individu', 'CONTOH: Data Steward - Riset Ekonomi'),
    ('euribor3m', 'desimal', 'Suku bunga Euribor 3 bulan', '≥ 0', '-', 'Bukan data pribadi', 'Publik', 'Indikator pasar, bukan atribut individu', 'CONTOH: Data Steward - Riset Ekonomi'),
    ('nr.employed', 'desimal', 'Jumlah tenaga kerja (kuartalan)', 'numerik', '-', 'Bukan data pribadi', 'Publik', 'Indikator ekonomi makro, bukan atribut individu', 'CONTOH: Data Steward - Riset Ekonomi'),
    ('y', 'kategori', 'Nasabah berlangganan deposito berjangka?', 'no, yes', 'V6', 'Umum: dapat mengidentifikasi bila dikombinasikan (Pasal 4 ayat 3)', 'Internal', 'Keputusan nasabah terhadap penawaran; atribut individu', 'CONTOH: Data Owner - Marketing'),
]

MONTHS = {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"}
DAYS = {"mon", "tue", "wed", "thu", "fri"}
YESNO = {"yes", "no"}


def load(path):
    return pd.read_csv(path, sep=";")


# ---------------------------------------------------------------- aturan DQ
def run_rules(df):
    """Mengembalikan daftar (id, dimensi, aturan, jumlah_gagal) untuk df."""
    n = len(df)
    r = []

    def add(rid, dim, rule, fail):
        r.append((rid, dim, rule, int(fail), n))

    # Keunikan
    add("U1", "Keunikan", "Tidak ada baris duplikat penuh", df.duplicated().sum())

    # Kelengkapan: 'unknown' atau kosong dianggap tidak lengkap
    for col in ["job", "marital", "education", "default", "housing", "loan"]:
        if col in df:
            miss = df[col].isna() | (df[col].astype(str).str.lower() == "unknown")
            add(f"K-{col}", "Kelengkapan", f"{col} terisi (bukan kosong/'unknown')", miss.sum())

    # Validitas
    if "age" in df:
        add("V1", "Validitas", "age di rentang 17-100", (~df["age"].between(17, 100)).sum())
    if "duration" in df:
        add("V2", "Validitas", "duration >= 0", (df["duration"] < 0).sum())
    if "campaign" in df:
        add("V3", "Validitas", "campaign >= 1", (df["campaign"] < 1).sum())
    if "month" in df:
        add("V4", "Validitas", "month bernilai singkatan bulan baku", (~df["month"].isin(MONTHS)).sum())
    if "day_of_week" in df:
        add("V5", "Validitas", "day_of_week bernilai hari kerja baku", (~df["day_of_week"].isin(DAYS)).sum())
    if "y" in df:
        add("V6", "Validitas", "y hanya bernilai yes/no", (~df["y"].isin(YESNO)).sum())
    if "pdays" in df:
        add("V7", "Validitas", "pdays tidak memakai kode sentinel 999", (df["pdays"] == 999).sum())

    # Konsistensi
    if {"pdays", "previous"} <= set(df.columns):
        no_contact = (df["pdays"] == 999) | df["pdays"].isna()
        bad = (df["previous"] > 0) & no_contact
        add("C1", "Konsistensi", "previous > 0 berarti pdays berisi hari nyata (bukan 999)", bad.sum())
    if {"poutcome", "previous"} <= set(df.columns):
        bad = (df["previous"] == 0) & (df["poutcome"] != "nonexistent")
        add("C2", "Konsistensi", "previous = 0 berarti poutcome = nonexistent", bad.sum())

    out = pd.DataFrame(r, columns=["ID", "Dimensi", "Aturan", "Gagal", "Total"])
    out["Lolos_%"] = ((1 - out["Gagal"] / out["Total"]) * 100).round(2)
    return out


# ---------------------------------------------------------------- pembersihan
def clean(df):
    c = df.copy()
    log = []

    before = len(c)
    c = c.drop_duplicates().reset_index(drop=True)
    log.append(("Hapus duplikat penuh", before - len(c)))

    # Standarisasi 'unknown' -> NaN (nilai hilang dicatat eksplisit, bukan teks)
    n_unknown = 0
    for col in c.select_dtypes(include=["object", "string"]).columns:
        mask = c[col].astype(str).str.lower() == "unknown"
        n_unknown += int(mask.sum())
        c.loc[mask, col] = np.nan
    log.append(("Standarisasi 'unknown' menjadi nilai kosong (NaN)", n_unknown))

    # Kode sentinel 999 -> NaN + flag
    if "pdays" in c:
        flag = c["pdays"] == 999
        c["pernah_dikontak_sebelumnya"] = (~flag).astype(int)
        c.loc[flag, "pdays"] = np.nan
        log.append(("pdays 999 diubah ke NaN dan ditambah flag pernah_dikontak_sebelumnya", int(flag.sum())))
    return c, pd.DataFrame(log, columns=["Tindakan", "Jumlah baris/nilai terdampak"])


def format_workbook(path):
    """Merapikan laporan: header tebal, lebar kolom otomatis, teks membungkus, baris pertama dibekukan."""
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = load_workbook(path)
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="305496")
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for col in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(max(width + 2, 12), 60)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "A2"
    wb.save(path)


def main():
    raw = load(SRC)
    rules_before = run_rules(raw)

    cleaned, clog = clean(raw)
    rules_after = run_rules(cleaned)

    cmp_ = rules_before.merge(
        rules_after[["ID", "Gagal", "Total", "Lolos_%"]],
        on="ID", how="left", suffixes=("_sebelum", "_sesudah"),
    )
    # Aturan kelengkapan: NaN dihitung tidak lengkap secara jujur setelah standarisasi
    for col in ["job", "marital", "education", "default", "housing", "loan"]:
        rid = f"K-{col}"
        if rid in rules_after["ID"].values:
            m = cleaned[col].isna().sum()
            cmp_.loc[cmp_["ID"] == rid, "Gagal_sesudah"] = m
            cmp_.loc[cmp_["ID"] == rid, "Lolos_%_sesudah"] = round((1 - m / len(cleaned)) * 100, 2)
    cmp_["Catatan"] = ""
    cmp_.loc[cmp_["ID"].str.startswith("K-"), "Catatan"] = (
        "Nilai kosong tidak diisi tebakan; didokumentasikan sebagai keterbatasan sumber"
    )
    cmp_.loc[cmp_["ID"] == "V7", "Catatan"] = "Sentinel 999 diubah ke NaN + flag"

    dd = pd.DataFrame(DICT, columns=["Field", "Tipe", "Deskripsi", "Nilai/Rentang valid", "Aturan DQ terkait",
                                     "Kategori data pribadi (UU PDP No. 27/2022)", "Klasifikasi data", "Alasan",
                                     "Pemilik (CONTOH, ilustrasi)"])
    dd["Ada di data?"] = dd["Field"].isin(raw.columns).map({True: "Ya", False: "Tidak"})

    lineage = pd.DataFrame({
        "Tahap": [1, 2, 3, 4, 5],
        "Proses": [
            "Sumber: UCI Bank Marketing (bank-additional-full.csv)",
            "Ingest: pd.read_csv(sep=';') tanpa mengubah file asli",
            "Profiling: jalankan aturan DQ (run_rules)",
            "Pembersihan: duplikat, 'unknown', sentinel 999 (clean)",
            "Output: bank_clean.csv + dq_report.xlsx",
        ],
        "Pemilik tahap": ["Data Owner", "Data Engineer", "Data Steward", "Data Steward", "Data Consumer"],
    })

    summary = pd.DataFrame({
        "Metrik": ["Jumlah baris awal", "Jumlah baris akhir", "Jumlah kolom awal", "Jumlah aturan DQ"],
        "Nilai": [len(raw), len(cleaned), raw.shape[1], len(rules_before)],
    })

    with pd.ExcelWriter("dq_report.xlsx") as xw:
        summary.to_excel(xw, sheet_name="Ringkasan", index=False)
        dd.to_excel(xw, sheet_name="Kamus_Data", index=False)
        cmp_.to_excel(xw, sheet_name="Hasil_Aturan_DQ", index=False)
        clog.to_excel(xw, sheet_name="Log_Pembersihan", index=False)
        lineage.to_excel(xw, sheet_name="Lineage", index=False)

    format_workbook("dq_report.xlsx")
    cleaned.to_csv("bank_clean.csv", index=False)
    print(summary.to_string(index=False))
    print()
    print(cmp_[["ID", "Aturan", "Gagal_sebelum", "Gagal_sesudah"]].to_string(index=False))
    print("\nTersimpan: dq_report.xlsx, bank_clean.csv")


if __name__ == "__main__":
    main()
