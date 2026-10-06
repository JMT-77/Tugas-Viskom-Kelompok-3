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
└── tugas_2/                 # OpenCV
    ├── README.md
    ├── requirements.txt
    ├── src/
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

- **Tugas 1** tidak memakai library eksternal. Implementasi membaca/menulis `PPM`, `PGM`, dan BMP sederhana (`24-bit`/`32-bit`). JPG/PNG dapat dipakai pada Tugas 2 melalui OpenCV.
- Ukuran gambar bebas selama tersedia memori yang cukup.
- Setiap fungsi mempunyai folder input dan output sendiri.

## Menjalankan

### Tugas 1

```bash
python tugas_1/src/main.py color-depth tugas_1/data/input/color_depth/input.ppm tugas_1/data/output/color_depth/output.ppm --bits 4
python tugas_1/src/main.py resize tugas_1/data/input/resolusi/input.ppm tugas_1/data/output/resolusi/output.ppm --width 640 --height 480
python tugas_1/src/main.py rotate tugas_1/data/input/rotasi/input.ppm tugas_1/data/output/rotasi/output.ppm --angle 90
```

### Tugas 2

```bash
pip install -r tugas_2/requirements.txt
python tugas_2/src/main.py mirror tugas_2/data/input/pencerminan/input.jpg tugas_2/data/output/pencerminan/output.jpg --direction horizontal
python tugas_2/src/main.py rotate tugas_2/data/input/rotasi/input.jpg tugas_2/data/output/rotasi/output.jpg --angle 90
python tugas_2/src/main.py edge tugas_2/data/input/deteksi_tepi/input.jpg tugas_2/data/output/deteksi_tepi/output.png
python tugas_2/src/main.py denoise tugas_2/data/input/noise_reduction/input.jpg tugas_2/data/output/noise_reduction/output.jpg --method median
```

Jalankan `--help` untuk melihat semua opsi.
