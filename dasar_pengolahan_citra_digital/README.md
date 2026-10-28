# Dasar Pengolahan Citra Digital

Semua perhitungan memakai rumus dan loop Python. Pillow hanya digunakan untuk membuka gambar menjadi nilai RGB. Kuantisasi, resize, rotasi, gambar pembanding, label bitmap, dan encoder PNG/PPM/PGM/BMP ditulis manual dengan standard library. Fungsi inti tidak menggunakan OpenCV atau NumPy. Modul fitur_warna.py adalah tambahan HSV dari kode lama dan masih membutuhkan OpenCV/NumPy; modul opsional ini tidak dijalankan oleh run_all.py.

## Menjalankan

Dari root proyek:

```powershell
python -m pip install -r dasar_pengolahan_citra_digital/requirements.txt
python dasar_pengolahan_citra_digital/src/run_all.py
python -m unittest discover -s dasar_pengolahan_citra_digital/tests -v
```

Input default adalah `data/input/sample_asymmetric.png`: gradien RGB, kotak kuning di kiri atas, lingkaran gelap di kanan bawah, serta panah ke kanan. Input tidak simetris agar 90 dan 270 derajat mudah dibedakan, dan gradien memperlihatkan pengurangan level warna. Ini citra sintetis untuk pengujian, bukan foto internet. Input sintetis lama yang lebih simetris sudah diarsipkan di backup.

Membuat ulang input secara manual:

```powershell
python dasar_pengolahan_citra_digital/src/create_sample.py
```

## Fungsi dan rumus

| Fungsi | Rumus / perilaku |
|---|---|
| `properties(image)` | W×H piksel; megapiksel=W×H/10^6; level=2^8; bit/piksel=8×kanal; kombinasi=2^(8×kanal); memori mentah=W×H×kanal byte. |
| `color_depth(image,bits)` | L=2^bits−1; q=round(R/255×L); hasil=round(q/L×255), diulang untuk R/G/B. |
| `resize_nearest(image,W,H)` | sx=floor(x×W_input/W_output); sy=floor(y×H_input/H_output). |
| `rotate(image,90)` | (x,y) → (H−1−y,x). |
| `rotate(image,180)` | (x,y) → (W−1−x,H−1−y). |
| `rotate(image,270)` | (x,y) → (y,W−1−x). |

Koordinat layar ditulis (x,y); akses matriks `pixels[y][x]`. Contoh matriks kanal R 5×5 dan substitusi satu piksel untuk kuantisasi, resize, dan ketiga rotasi dicatat dalam `perhitungan.json`. Program memeriksa hasil hitung contoh terhadap keluaran fungsi dengan assert.

Properti menggambarkan citra yang sudah didekode menjadi kanal 8 bit, bukan bit-depth asli semua format sumber. Kanal grayscale tetap ditandai L walaupun nilai disimpan sebagai tuple RGB untuk menyeragamkan operasi. Memori mentah adalah ukuran representasi kanal padat, bukan ukuran berkas terkompresi atau konsumsi objek list Python.

Kuantisasi 4 bit menghasilkan 16 level efektif per kanal, tetapi encoder PNG tetap menyimpan 8 bit/kanal. Jadi kuantisasi mengurangi keragaman warna, bukan otomatis ukuran/bit-depth penyimpanan PNG.

## Hasil per fungsi

Semua PNG pembanding mempertahankan piksel pada ukuran aslinya: sebelum di kiri, sesudah di kanan, disertai label parameter dan dimensi. Pada resolusi, gambar yang lebih kecil benar-benar ditampilkan lebih kecil.

| Berkas di `data/output/` | Isi |
|---|---|
| `properti.png` | Citra input dan ringkasan depth/resolusi. |
| `color_depth_1bit.png` | Input vs 2 level/kanal. |
| `color_depth_4bit.png` | Input vs 16 level/kanal. |
| `color_depth_8bit.png` | Input vs 256 level/kanal; hasil identik sebagai kontrol. |
| `resolusi.png` | Input 320×200 vs nearest-neighbor 160×100. |
| `rotasi_90.png` | Input vs 90° searah jarum jam. |
| `rotasi_180.png` | Input vs 180°. |
| `rotasi_270.png` | Input vs 270° searah jarum jam. |
| `perhitungan.json` | Properti, contoh koordinat, matriks, substitusi dan hasil verifikasi. |
| `text/color_depth.txt`, `text/resolusi.txt`, `text/rotasi.txt` | Matriks keluaran kuantisasi 4 bit, resize dan rotasi 90, untuk kebutuhan teks Tugas 1. |

Komposit lama `all_results.png` digantikan gambar per fungsi. Tidak ada dua implementasi rotasi atau renderer terpisah di Tugas 1.

## Menjalankan satu fungsi

```powershell
python dasar_pengolahan_citra_digital/src/main.py info dasar_pengolahan_citra_digital/data/input/sample_asymmetric.png
python dasar_pengolahan_citra_digital/src/main.py color-depth dasar_pengolahan_citra_digital/data/input/sample_asymmetric.png dasar_pengolahan_citra_digital/data/output/custom_depth.png --bits 4
python dasar_pengolahan_citra_digital/src/main.py resize dasar_pengolahan_citra_digital/data/input/sample_asymmetric.png dasar_pengolahan_citra_digital/data/output/custom_resize.png --width 160 --height 100
python dasar_pengolahan_citra_digital/src/main.py rotate dasar_pengolahan_citra_digital/data/input/sample_asymmetric.png dasar_pengolahan_citra_digital/data/output/custom_rotate.png --angle 270
```

CLI PNG menyimpan perbandingan sebelum/sesudah. Ekstensi `.txt`, `.ppm`, `.pgm`, dan `.bmp` menyimpan citra hasil saja. `write_image()` selalu menulis citra yang diberikan, tanpa menambahkan panel; hanya CLI/runner yang menyusun perbandingan.

## Analisis yang dapat dipakai pada laporan

- Input RGB 320×200 memiliki 64.000 piksel, 24 bit/piksel, 16.777.216 kombinasi warna yang mungkin, dan 192.000 byte kanal mentah.
- Kuantisasi 1 bit menimbulkan batas warna besar; 4 bit memperlihatkan pita pada gradien; 8 bit mempertahankan nilai input.
- Resize 160×100 mengurangi jumlah piksel menjadi 16.000. Nearest-neighbor mengambil nilai sumber tanpa interpolasi; detail kecil dapat hilang.
- Rotasi 90/270 bertukar dimensi menjadi 200×320; 180 tetap 320×200. Nilai dan jumlah piksel tetap; hanya posisinya berubah.
- Pada input lama yang lebih simetris, 90/270 bisa tampak mirip. Karena itu uji regresi memakai matriks asimetris `[[1,2,3],[4,5,6]]`; keluaran 270 yang benar adalah `[[3,6],[2,5],[1,4]]`.

Pengujian mencakup kuantisasi/rentang level, resize, ketiga rotasi, properti, parameter tidak sah, roundtrip format keluaran, dan PNG pembanding. Tidak mengukur kinerja foto resolusi sangat besar.

## Filter dan intensitas

Folder ini menggabungkan properti/geometri dan filter/intensitas. `src/operations.py` menyimpan properti/geometri; `src/filter_operations.py` menyimpan rumus filter/intensitas. Keduanya memakai satu tipe Image, loader, encoder dan renderer. Tidak ada implementasi rotasi duplikat.

Runner utama juga menjalankan pencerminan horizontal/vertikal, Canny manual, Gaussian, median, bilateral, brightness C=40 dan contrast G=1.5/P=127. Output per fungsi: `mirror_horizontal.png`, `mirror_vertical.png`, `edge.png`, `denoise_gaussian.png`, `denoise_median.png`, `denoise_bilateral.png`, `brightness.png`, `contrast.png`. Input edge/noise telah diganti dengan citra uji yang relevan. Canny memperbaiki pasangan tetangga diagonal pada non-maximum suppression. Materi Bab II lain yang belum tersedia tidak ditambahkan pada perubahan ini.

```powershell
python dasar_pengolahan_citra_digital/src/run_filters.py
python dasar_pengolahan_citra_digital/src/main.py brightness dasar_pengolahan_citra_digital/data/input/brightness_contrast.jpeg dasar_pengolahan_citra_digital/data/output/custom_brightness.png --c 40
```

## Tambahan fitur warna HSV

Kode ekstraksi fitur warna lama ada di `src/fitur_warna.py`, input di `data/input/fitur_warna.jpg`. Modul opsional ini masih menggunakan OpenCV/NumPy. Install requirements proyek lengkap, lalu:

```powershell
python dasar_pengolahan_citra_digital/src/fitur_warna.py > dasar_pengolahan_citra_digital/data/output/feature_summary.txt
```

Input foto lain dipertahankan untuk eksperimen CLI. Sumber unduhan lama ada di `image_sources.md`. Default input/output runner dihitung relatif terhadap lokasi skrip.

## Input edge dan noise terbaru, 15 Oktober 2026

| Operasi | Input | Parameter | Tujuan |
|---|---|---|---|
| Edge | `edge_coins.png` | Canny manual low=40, high=100, blur=5 | Menampilkan batas luar koin. |
| Median | `median_input.png` | kernel 3 | Menghilangkan bintik hitam-putih salt-and-pepper 6%. |
| Gaussian | `gaussian_input.png` | kernel 3 | Mengurangi grain Gaussian SD=20 pada cameraman. |
| Bilateral | `bilateral_input.png` | kernel 5, sigma ruang=2.5, sigma warna=50 | Mengurangi grain Gaussian SD=20 pada koin sambil menjaga batas objek. |

Noise merupakan simulasi manual dengan seed 20261015, bukan kerusakan alami pada foto sumber. `camera_clean.png` dan `coins_clean.png` adalah acuan PSNR. Input landscape/peppers lama yang tidak dipakai lagi dibersihkan. Apel masih dipakai mirror; ilustrasi brightness/contrast tetap digunakan operasi terkait.

Untuk membuat ulang input dan hasil:

```powershell
python dasar_pengolahan_citra_digital/src/create_filter_inputs.py
python dasar_pengolahan_citra_digital/src/run_all.py
```

PSNR dihitung manual: MSE=jumlah kuadrat selisih kanal/(W*H*3), PSNR=10 log10(255^2/MSE). Nilai lebih tinggi berarti hasil lebih dekat ke acuan bersih; bukan persentase akurasi. Runner memeriksa PSNR sesudah filter lebih tinggi pada fixture ini. Detail ada di `data/output/filter_metrics.json` dan label PNG.

| Filter | PSNR sebelum | PSNR sesudah |
|---|---|---|
| Median | 16.97 dB | 26.45 dB |
| Gaussian | 22.43 dB | 25.76 dB |
| Bilateral | 22.20 dB | 26.92 dB |

Gaussian dapat melunakkan detail; bilateral juga tidak mempertahankan setiap detail kecil. Canny hanya mengekstrak tepi, belum menghitung koin atau menjamin setiap kontur tertutup. Ketepatan kontur belum diukur terhadap anotasi ground truth. Uji regresi memeriksa gradien diagonal 45/135 derajat.
