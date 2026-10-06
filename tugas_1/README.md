# Tugas 1 — Color Depth, Resolusi, Rotasi

Implementasi pure Python tanpa library eksternal. Hanya modul standard library yang digunakan.

## Format

Gunakan PPM/PGM atau BMP 24-bit/32-bit. Format PPM/PGM dipilih agar algoritma dan hasil dapat diperiksa tanpa dependency tambahan.

## Operasi

- `color-depth`: kuantisasi setiap kanal RGB ke jumlah bit per kanal.
- `resize`: perubahan resolusi menggunakan nearest-neighbor.
- `rotate`: rotasi 90, 180, atau 270 derajat searah jarum jam.

## Contoh

```bash
python src/main.py color-depth data/input/color_depth/input.ppm data/output/color_depth/output.ppm --bits 4
python src/main.py resize data/input/resolusi/input.ppm data/output/resolusi/output.ppm --width 640 --height 480
python src/main.py rotate data/input/rotasi/input.ppm data/output/rotasi/output.ppm --angle 90
```

Input dan output dapat berukuran bebas. File contoh dapat dibuat dengan format PPM:

```text
P3
2 2
255
255 0 0   0 255 0
0 0 255   255 255 255
```
