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
│   │   ├── main.py
│   │   └── run_all.py
│   ├── data/
│   │   ├── input/
│   │   │   └── sample_color.png
│   │   └── output/
│   │       ├── all_results.png
│   │       └── text/
│   │           ├── color_depth.txt
│   │           ├── resolusi.txt
│   │           └── rotasi.txt
├── tugas_2/                 # Rumus manual; OpenCV hanya untuk load input
│   ├── README.md
│   ├── IMAGE_SOURCES.md
│   ├── requirements.txt
│   ├── src/
│   │   ├── manual_operations.py
│   │   ├── operations.py
│   │   ├── main.py
│   │   └── run_all.py
│   ├── data/
│   │   ├── input/
│   │   │   ├── internet_apple.png
│   │   │   ├── internet_peppers.png
│   │   │   ├── internet_landscape.png
│   │   │   └── brightness_contrast.jpeg
│   │   └── output/
│   │       └── all_results.png
├── tugas_morfologi/         # Morfologi citra untuk praproses dokumen/OCR
│   ├── README.md
│   ├── REFERENCES.md
│   ├── requirements.txt
│   ├── src/
│   │   ├── create_sample.py
│   │   ├── operations.py
│   │   └── main.py
│   ├── data/
│   │   ├── input/
│   │   │   └── document_scan.png
│   │   └── output/
│   │       └── document_morphology_results.png
│   └── tests/
└── tugas_4/                 # Persiapan ekstraksi fitur warna
    ├── README.md
    ├── main.py
    └── data/
        ├── input/
        │   └── img.jpg
        └── output/
            └── feature_summary.txt
```

Tugas 3 sengaja tidak diubah sesuai permintaan.

## Catatan format input

- **Tugas 1** tidak memakai library eksternal. Implementasi membaca PNG sederhana, `PPM`, `PGM`, dan BMP (`24-bit`/`32-bit`), lalu menulis output teks.
- **Tugas 2** menggunakan OpenCV hanya untuk membaca input. Seluruh transformasi, rumus, konvolusi, filtering, dan penulisan output dilakukan manual.
- Ukuran gambar bebas selama tersedia memori yang cukup.
- Input yang sama disimpan satu kali dan dipakai bersama oleh operasi yang membutuhkannya.
- Tugas 1, Tugas 2, dan Tugas Morfologi menyediakan satu output PNG komposit untuk hasil visual; Tugas 4 menyimpan satu ringkasan fitur teks karena kodenya tidak menghasilkan beberapa citra.

## Menjalankan

### Tugas 1

```bash
python tugas_1/src/run_all.py
```

### Tugas 2

```bash
pip install -r tugas_2/requirements.txt
python tugas_2/src/run_all.py
```

### Tugas Morfologi

```bash
pip install -r tugas_morfologi/requirements.txt
python tugas_morfologi/src/main.py tugas_morfologi/data/input/document_scan.png tugas_morfologi/data/output/document_morphology_results.png --kernel 3
```

Perintah tersebut menjalankan dilation, erosion, opening, closing, top-hat, hit-or-miss, skeletonization, dan thinning secara bersamaan. Hasilnya digabung menjadi satu PNG komposit.

### Tugas 4

```bash
cd tugas_4
python main.py > data/output/feature_summary.txt
cd ..
```

Jalankan `--help` untuk melihat semua opsi.
