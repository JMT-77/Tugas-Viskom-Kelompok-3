# Tugas Morfologi Citra

## Tujuan tugas

Tugas ini menerapkan delapan operasi morfologi sesuai daftar pada materi:

1. Dilation
2. Erosion
3. Opening
4. Closing
5. Top-hat Transform
6. Hit-or-Miss
7. Skeletonization
8. Thinning

Kasus yang dipilih adalah **pembersihan hasil pemindaian dokumen sebelum OCR**. Kasus ini bermanfaat untuk arsip sekolah, formulir layanan publik, administrasi UMKM, dan dokumen lama karena operasi morfologi dapat membantu mengurangi bintik, menyambungkan goresan yang terputus, serta membuat struktur tulisan lebih mudah dianalisis.

Input contoh adalah dokumen sintetis tanpa data pribadi. Dokumen dibuat sebagai PNG agar pengujian dapat diulang tanpa bergantung pada foto atau lisensi gambar dari internet.

## Aturan pemrosesan

OpenCV dan NumPy diperbolehkan pada tugas ini. Semua operasi dijalankan dalam satu pipeline oleh `run_all()` dan hasilnya digabung ke **satu file PNG komposit**. File komposit memuat input asli, citra biner, dan hasil seluruh delapan operasi.

Urutan praproses:

```text
PNG grayscale → threshold Otsu + inverse → foreground tinta = putih
```

## Fungsi dan manfaat setiap operasi

| Operasi | Fungsi | Manfaat pada dokumen |
|---|---|---|
| Dilation | Memperbesar area foreground | Menebalkan huruf dan menyambungkan celah kecil |
| Erosion | Mengurangi area foreground | Menghapus bagian kecil dan menipiskan objek |
| Opening | Erosion lalu dilation | Menghilangkan bintik/noise kecil tanpa mempertahankan noise tersebut |
| Closing | Dilation lalu erosion | Menutup celah kecil pada garis atau tulisan |
| Top-hat | Citra asli dikurangi hasil opening | Menonjolkan detail foreground kecil yang hilang saat opening |
| Hit-or-miss | Mencari pola foreground dan background tertentu | Mendeteksi endpoint pada struktur tulisan yang sudah ditipiskan |
| Skeletonization | Menghasilkan kerangka morfologis objek | Mengurangi bentuk menjadi struktur pusat untuk analisis bentuk |
| Thinning | Menghapus pixel tepi tanpa memutus konektivitas | Menghasilkan garis satu pixel yang berguna untuk OCR, vektorisasi, atau analisis tulisan |

### Catatan interpretasi

- Operasi biner bekerja pada tinta putih di atas latar belakang hitam setelah threshold inverse.
- `Hit-or-miss` diterapkan pada hasil `thinning` agar pola endpoint satu pixel dapat ditemukan secara bermakna.
- `Skeletonization` menggunakan skeleton morfologis iteratif (erosi dan opening).
- `Thinning` menggunakan algoritma Zhang-Suen.
- Top-hat pada input biner menyoroti komponen foreground kecil yang tidak bertahan setelah opening. Untuk mengekstraksi objek terang dari citra grayscale, top-hat dapat diterapkan langsung pada citra grayscale dengan structuring element yang sama.

## Struktur folder

```text
morfologi_citra/
├── README.md
├── REFERENCES.md
├── requirements.txt
├── src/
│   ├── create_sample.py
│   ├── main.py
│   └── operations.py
├── data/
│   ├── input/
│   │   └── document_scan.png
│   └── output/
│       └── document_morphology_results.png
└── tests/
    └── test_operations.py
```

## Instalasi

Jalankan dari root repository:

```bash
cd /d/Dev/projects/kuliah/semester_7/viskom
python -m pip install -r morfologi_citra/requirements.txt
```

## Menjalankan seluruh proses sekaligus

Perintah berikut membaca satu PNG, menjalankan seluruh operasi, dan menghasilkan satu PNG yang berisi semua hasil:

```bash
python morfologi_citra/src/main.py \
  morfologi_citra/data/input/document_scan.png \
  morfologi_citra/data/output/document_morphology_results.png \
  --kernel 3
```

Di Git Bash Windows, gunakan path repository berikut:

```bash
cd /d/Dev/projects/kuliah/semester_7/viskom
```

Untuk membuat ulang input contoh:

```bash
python morfologi_citra/src/create_sample.py
```

Untuk melihat opsi CLI:

```bash
python morfologi_citra/src/main.py --help
```

## Output

Output utama:

```text
morfologi_citra/data/output/document_morphology_results.png
```

File PNG tersebut berisi panel berlabel:

- Original grayscale
- Binary input
- Dilation
- Erosion
- Opening
- Closing
- Top-hat
- Hit-or-miss endpoints
- Skeletonization
- Thinning

Dengan demikian, semua proses dalam tugas morfologi dapat dibandingkan dalam satu foto, bukan tersebar pada banyak file.

## Referensi

Definisi operasi dan algoritma yang digunakan dirangkum pada `REFERENCES.md`.

## Keterbatasan

- Threshold Otsu diasumsikan cocok untuk dokumen dengan tinta gelap dan latar relatif terang.
- Ukuran kernel memengaruhi hasil. Kernel 3 cocok sebagai demonstrasi dasar; kernel 5 atau 7 dapat dipakai untuk noise/celah yang lebih besar.
- Hasil hit-or-miss bergantung pada pola endpoint dan bentuk objek biner.
- Implementasi ditujukan untuk pembelajaran dan praproses sederhana, bukan pengganti pipeline OCR produksi yang memerlukan evaluasi terhadap banyak jenis dokumen.
