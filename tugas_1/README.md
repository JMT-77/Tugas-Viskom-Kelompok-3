# Tugas 1 — Color Depth, Resolusi, Rotasi

Implementasi pure Python tanpa library eksternal. Hanya modul standard library yang digunakan.

## Struktur data

Satu file input PNG dipakai bersama oleh seluruh operasi. Tidak ada salinan input di dalam folder per operasi.

```text
├── src/
│   ├── image_io.py
│   ├── operations.py
│   ├── main.py
│   └── run_all.py
├── data/
│   ├── input/
│   │   └── sample_color.png
│   └── output/
│       ├── all_results.png
│       └── text/
│           ├── color_depth.txt
│           ├── resolusi.txt
│           └── rotasi.txt
```

## Format

Gunakan PNG sederhana 8-bit non-interlaced, PPM/PGM, atau BMP 24-bit/32-bit sebagai input. PNG grayscale, RGB, grayscale+alpha, dan RGBA didukung. Output visual utama dibuat sebagai satu PNG komposit. Detail matriks RGB tetap disimpan sebagai tiga file `.txt` karena format teks merupakan kebutuhan Tugas 1.

## Operasi

- `color-depth`: kuantisasi setiap kanal RGB ke jumlah bit per kanal.
- `resize`: perubahan resolusi menggunakan nearest-neighbor.
- `rotate`: rotasi 90, 180, atau 270 derajat searah jarum jam.

## Contoh

```bash
python tugas_1/src/main.py color-depth tugas_1/data/input/sample_color.png tugas_1/data/output/text/color_depth.txt --bits 4
python tugas_1/src/main.py resize tugas_1/data/input/sample_color.png tugas_1/data/output/text/resolusi.txt --width 640 --height 480
python tugas_1/src/main.py rotate tugas_1/data/input/sample_color.png tugas_1/data/output/text/rotasi.txt --angle 90
```

Untuk menjalankan semua operasi sekaligus dan membuat satu foto hasil lengkap:

```bash
python tugas_1/src/run_all.py
```

Output komposit `data/output/all_results.png` memiliki urutan panel:

- `P1`: input asli
- `P2`: color depth 4-bit
- `P3`: resize 640 × 480
- `P4`: rotasi 90°

Input dan output dapat berukuran bebas. File contoh dapat dibuat dengan format PPM:

```text
P3
2 2
255
255 0 0   0 255 0
0 0 255   255 255 255
```
