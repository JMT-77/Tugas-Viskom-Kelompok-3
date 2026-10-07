# Tugas 2 — Pencerminan, Rotasi, Deteksi Tepi, Noise Reduction

Implementasi menggunakan OpenCV.

## Operasi

- `mirror`: pencerminan horizontal atau vertical.
- `rotate`: rotasi 90, 180, atau 270 derajat.
- `edge`: grayscale + Gaussian blur + Canny edge detection.
- `denoise`: Gaussian, median, atau bilateral filtering.

## Contoh

```bash
python src/main.py mirror data/input/pencerminan/input.jpg data/output/pencerminan/output.jpg --direction horizontal
python src/main.py rotate data/input/rotasi/input.jpg data/output/rotasi/output.jpg --angle 90
python src/main.py edge data/input/deteksi_tepi/input.ppm data/output/deteksi_tepi/output.ppm --low 50 --high 150
python src/main.py denoise data/input/noise_reduction/input.ppm data/output/noise_reduction/output.ppm --method median --kernel 5
python src/main.py brightness data/input/brightness/img.jpeg data/output/brightness/output.jpg --c 50
python src/main.py contrast data/input/contrast/img.jpeg data/output/contrast/output.jpg --g 1.5 --p 127
```

## Input PNG dari internet

Contoh input PNG dari Wikimedia Commons dan sumber unduhannya dicatat di `IMAGE_SOURCES.md`.

```bash
python src/main.py mirror data/input/pencerminan/internet_apple.png data/output/pencerminan/internet_apple_mirror.ppm --direction horizontal
python src/main.py rotate data/input/rotasi/internet_peppers.png data/output/rotasi/internet_peppers_rotated.ppm --angle 90
python src/main.py edge data/input/deteksi_tepi/internet_landscape.png data/output/deteksi_tepi/internet_landscape_edges.ppm --low 50 --high 150
python src/main.py denoise data/input/noise_reduction/internet_apple.png data/output/noise_reduction/internet_apple_denoised.ppm --method median --kernel 5
```

Format input umum seperti JPG, JPEG, PNG, BMP, dan TIFF dapat dibaca OpenCV.
