# Tugas-Viskom-Kelompok-3

Kumpulan tugas praktikum Visi Komputer.

## Struktur

```text
viskom/
├── README.md
├── requirements.txt
├── tugas_1/                 # Pure Python, tanpa library eksternal
│   ├── README.md
│   ├── requirements.txt
│   ├── src/
│   │   ├── image_io.py
│   │   ├── operations.py
│   │   └── main.py
│   ├── data/
│   │   ├── input/
│   │   │   ├── color_depth/
│   │   │   ├── resolusi/
│   │   │   └── rotasi/
│   │   └── output/
│   │       ├── color_depth/
│   │       ├── resolusi/
│   │       └── rotasi/
│   └── tests/
└── tugas_2/                 # Rumus manual; OpenCV hanya untuk load input
    ├── README.md
    ├── IMAGE_SOURCES.md
    ├── requirements.txt
    ├── src/
    │   ├── manual_operations.py
    │   ├── operations.py
    │   └── main.py
    ├── data/
    │   ├── input/
    │   │   ├── pencerminan/
    │   │   ├── rotasi/
    │   │   ├── deteksi_tepi/
    │   │   └── noise_reduction/
    │   └── output/
    │       ├── pencerminan/
    │       ├── rotasi/
    │       ├── deteksi_tepi/
    │       └── noise_reduction/
    └── tests/
```

## Catatan format input

- **Tugas 1** tidak memakai library eksternal. Implementasi membaca PNG sederhana, `PPM`, `PGM`, dan BMP (`24-bit`/`32-bit`), lalu menulis output teks.
- **Tugas 2** menggunakan OpenCV hanya untuk membaca input. Seluruh transformasi, rumus, konvolusi, filtering, dan penulisan output dilakukan manual.
- Ukuran gambar bebas selama tersedia memori yang cukup.
- Setiap fungsi mempunyai folder input dan output sendiri.

## Menjalankan

### Tugas 1

```bash
python tugas_1/src/main.py color-depth tugas_1/data/input/color_depth/input.png tugas_1/data/output/color_depth/output.txt --bits 4
python tugas_1/src/main.py resize tugas_1/data/input/resolusi/input.png tugas_1/data/output/resolusi/output.txt --width 640 --height 480
python tugas_1/src/main.py rotate tugas_1/data/input/rotasi/input.png tugas_1/data/output/rotasi/output.txt --angle 90
```

### Tugas 2

```bash
pip install -r tugas_2/requirements.txt
python tugas_2/src/main.py mirror tugas_2/data/input/pencerminan/internet_apple.png tugas_2/data/output/pencerminan/manual_mirror.png --direction horizontal
python tugas_2/src/main.py rotate tugas_2/data/input/rotasi/internet_peppers.png tugas_2/data/output/rotasi/manual_rotate.png --angle 90
python tugas_2/src/main.py edge tugas_2/data/input/deteksi_tepi/internet_landscape.png tugas_2/data/output/deteksi_tepi/manual_edge.png --low 50 --high 150 --blur 5
python tugas_2/src/main.py denoise tugas_2/data/input/noise_reduction/internet_apple.png tugas_2/data/output/noise_reduction/manual_median.png --method median --kernel 5
```

Jalankan `--help` untuk melihat semua opsi.
