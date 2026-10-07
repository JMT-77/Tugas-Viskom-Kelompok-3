# Tugas 1 — Color Depth, Resolusi, Rotasi

Implementasi pure Python tanpa library eksternal. Hanya modul standard library yang digunakan.

## Format

Gunakan PNG sederhana 8-bit non-interlaced, PPM/PGM, atau BMP 24-bit/32-bit sebagai input. PNG grayscale, RGB, grayscale+alpha, dan RGBA didukung. Untuk pengumpulan, output utama dibuat dalam format `.txt` berisi metadata ukuran dan matriks RGB setiap pixel.

## Operasi

- `color-depth`: kuantisasi setiap kanal RGB ke jumlah bit per kanal.
- `resize`: perubahan resolusi menggunakan nearest-neighbor.
- `rotate`: rotasi 90, 180, atau 270 derajat searah jarum jam.

## Contoh

```bash
python src/main.py color-depth data/input/color_depth/input.png data/output/color_depth/output.txt --bits 4
python src/main.py resize data/input/resolusi/input.png data/output/resolusi/output.txt --width 640 --height 480
python src/main.py rotate data/input/rotasi/input.png data/output/rotasi/output.txt --angle 90
```

Input dan output dapat berukuran bebas. File contoh dapat dibuat dengan format PPM:

```text
P3
2 2
255
255 0 0   0 255 0
0 0 255   255 255 255
```
