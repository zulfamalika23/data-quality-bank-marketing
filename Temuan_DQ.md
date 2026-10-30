# Temuan Data Quality Assessment: UCI Bank Marketing

**Dataset:** `bank-additional-full.csv`, 41.188 baris dan 21 kolom. Setelah penghapusan 12 duplikat tersisa 41.176 baris.
**Metode:** 16 aturan kualitas data pada empat dimensi (keunikan, kelengkapan, validitas, konsistensi), dijalankan dengan Python (pandas) sebelum dan sesudah pembersihan.

## Ringkasan

Dari 16 aturan, **7 lolos 100%** pada data awal: seluruh aturan validitas rentang dan format (usia, durasi, jumlah kontak, bulan, hari, nilai target) serta aturan konsistensi `previous`-`poutcome`. Masalah kualitas terbesar ada pada **kelengkapan**, terutama kolom `default` yang 20,87% berisi "unknown", dan pada **konsistensi** antara `previous` dan `pdays` yang bermasalah di 9,98% baris. Dua perbaikan (kode 999 dan duplikat) sudah dilakukan, sedangkan nilai "unknown" didokumentasikan tanpa ditebak dan satu temuan konsistensi masih terbuka untuk dikonfirmasi ke pemilik data.

## Tabel temuan

| # | Dimensi | Temuan | Skala | Prioritas | Tindakan | Status |
|---|---|---|---|---|---|---|
| 1 | Kelengkapan | `default` berisi "unknown" | 8.597 baris (20,87%) | Tinggi | Diubah ke nilai kosong, tidak diisi tebakan | Didokumentasikan |
| 2 | Konsistensi | `previous` > 0 tetapi `pdays` = 999 | 4.110 baris (9,98%) | Tinggi | Belum ada, perlu klarifikasi arti kedua kolom | Terbuka, eskalasi ke pemilik data |
| 3 | Kelengkapan | `education` berisi "unknown" | 1.731 baris (4,20%) | Sedang | Diubah ke nilai kosong | Didokumentasikan |
| 4 | Kelengkapan | `housing` dan `loan` berisi "unknown" | masing-masing 990 baris (2,40%) | Sedang | Diubah ke nilai kosong | Didokumentasikan |
| 5 | Validitas | `pdays` memakai kode 999 untuk "belum pernah dihubungi" | 39.673 baris (96,32%) | Sedang | Diubah ke kosong dan ditambah kolom `pernah_dikontak_sebelumnya` | Diperbaiki (representasi) |
| 6 | Kelengkapan | `job` berisi "unknown" | 330 baris (0,80%) | Rendah | Diubah ke nilai kosong | Didokumentasikan |
| 7 | Kelengkapan | `marital` berisi "unknown" | 80 baris (0,19%) | Rendah | Diubah ke nilai kosong | Didokumentasikan |
| 8 | Keunikan | Baris duplikat penuh | 12 baris (0,03%) | Rendah | Dihapus | Diperbaiki (dengan asumsi) |

**Dasar prioritas:** *Tinggi* bila skalanya besar atau bila isi data bertentangan secara makna sehingga bisa menyesatkan analisis. *Sedang* bila ada dampak pada analisis tetapi sudah bisa ditangani. *Rendah* bila skalanya kecil dan dampaknya terbatas.

Catatan angka: jumlah pada sheet `Log_Pembersihan` (misalnya 39.661 untuk `pdays`) dihitung setelah duplikat dihapus, sehingga berbeda 12 dari angka di tabel ini.

## Catatan dan keterbatasan

1. **Perbaikan kode 999 hanya memperbaiki representasi.** Mengubah 999 menjadi nilai kosong ditambah penanda tidak menambah informasi baru. Angka lolos 100% setelah perbaikan menunjukkan format yang lebih benar, bukan kualitas sumber yang membaik.
2. **Temuan #2 belum diketahui penyebabnya.** Dokumentasi dataset menyebut 999 berarti nasabah belum pernah dihubungi pada kampanye sebelumnya, sedangkan `previous` > 0 berarti pernah ada kontak sebelum kampanye ini. Kedua kolom bisa saja mengukur periode yang berbeda. Hal itu tidak bisa dipastikan dari data, jadi perlu dikonfirmasi oleh pemilik data.
3. **Penghapusan duplikat adalah asumsi.** Dataset tidak memiliki ID nasabah, sehingga dua baris yang identik bisa saja dua nasabah berbeda dengan atribut sama. Hanya 12 baris (0,03%) yang terdampak.
4. **Nilai "unknown" tidak diimputasi.** Di dataset ini "unknown" mungkin berarti nasabah tidak menjawab, bukan data hilang karena kesalahan. Keduanya diperlakukan sama sebagai nilai kosong, dan perbedaan itu perlu dijelaskan oleh pemilik data.
5. **Aturan dan ambang batas dibuat untuk portofolio ini.** Dataset adalah data publik dari bank Portugal, bukan data BRI, dan aturan yang dipakai adalah usulan analis, bukan standar resmi sebuah bank.

## Rekomendasi

1. **Konfirmasi ke pemilik data** arti "unknown" (tidak menjawab atau tidak tercatat) dan hubungan `previous` dengan `pdays`. Selesaikan temuan #2 lebih dulu.
2. **Standarkan penanganan nilai tidak diketahui di sumber.** Gunakan nilai kosong (null) yang eksplisit, bukan teks "unknown", dan catat artinya di kamus data.
3. **Hindari kode sentinel seperti 999 pada kolom numerik.** Gunakan null dan kolom penanda terpisah, atau definisikan di kamus data.
4. **Tambahkan ID nasabah yang unik** supaya duplikasi dapat dipastikan dan dilacak.
5. **Jalankan aturan DQ ini secara berkala** dengan ambang batas yang disepakati pemilik data, misalnya batas minimal kelengkapan per kolom, dan laporkan hasilnya kepada data steward (dikerjakan di SOP pada langkah berikutnya).
