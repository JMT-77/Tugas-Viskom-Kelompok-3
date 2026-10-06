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
python src/main.py edge data/input/deteksi_tepi/input.jpg data/output/deteksi_tepi/output.png --low 50 --high 150
python src/main.py denoise data/input/noise_reduction/input.jpg data/output/noise_reduction/output.jpg --method median --kernel 5
```

Format input umum seperti JPG, JPEG, PNG, BMP, dan TIFF dapat dibaca OpenCV.
