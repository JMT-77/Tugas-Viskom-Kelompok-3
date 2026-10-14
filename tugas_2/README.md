# Tugas 2 — Implementasi Manual

Tugas 2 mengimplementasikan pencerminan, rotasi, deteksi tepi, noise reduction, brightness, dan contrast menggunakan rumus serta loop Python manual.

## Aturan library

- OpenCV hanya digunakan pada `read()` untuk mendekode file gambar input.
- Setelah dibaca, gambar diubah menjadi matriks pixel Python `(R, G, B)`.
- Tidak ada `cv2.flip`, `cv2.rotate`, `cv2.Canny`, `cv2.GaussianBlur`, `cv2.medianBlur`, `cv2.bilateralFilter`, atau `cv2.convertScaleAbs` dalam pemrosesan.
- Output PNG ditulis sendiri menggunakan `struct`, `zlib`, dan `binascii`. Output PPM, PGM, dan TXT juga ditulis tanpa library visual-processing.

## Rumus utama

### Grayscale

```text
Y = 0.299R + 0.587G + 0.114B
```

### Gaussian filter

```text
G(x,y) = 1/(2πσ²) × exp(-(x²+y²)/(2σ²))
```

Kernel dinormalisasi sehingga jumlah bobot sama dengan 1. Konvolusi dilakukan dengan menjumlahkan hasil perkalian pixel dan bobot kernel.

### Sobel

```text
Gx = [-1  0  1]       Gy = [-1 -2 -1]
     [-2  0  2]            [ 0  0  0]
     [-1  0  1]            [ 1  2  1]
```

```text
M = sqrt(Gx² + Gy²)
θ = atan2(Gy, Gx)
```

Deteksi tepi kemudian memakai non-maximum suppression, double threshold, dan hysteresis.

### Median filter

Nilai pixel output adalah median nilai pixel pada window kernel.

### Bilateral filter

```text
w = exp(-jarak_spasial²/(2σs²)) × exp(-perbedaan_warna²/(2σr²))
output = Σ(w × pixel) / Σw
```

### Brightness dan contrast

```text
brightness = pixel + c
contrast = g × pixel + p × (1 - g)
```

## Struktur file

```text
src/
├── manual_operations.py  # Image, loader, encoder, dan semua rumus manual
├── operations.py         # wrapper kompatibilitas ke manual_operations.py
├── main.py               # satu operasi per perintah
└── run_all.py             # semua operasi dan satu PNG komposit

data/
├── input/
│   ├── internet_apple.png       # dipakai mirror dan noise reduction
│   ├── internet_peppers.png     # dipakai rotasi
│   ├── internet_landscape.png   # dipakai deteksi tepi
│   └── brightness_contrast.jpeg # dipakai brightness dan contrast
└── output/
    └── all_results.png
```

Satu file yang sama dipakai bersama oleh operasi yang membutuhkan gambar tersebut. Tidak ada salinan input di dalam folder operasi.

## Cara menjalankan

```bash
cd /d/Dev/projects/kuliah/semester_7/viskom
python -m pip install -r tugas_2/requirements.txt
```

OpenCV hanya digunakan untuk decoding input. Pemrosesan dan penulisan output dilakukan oleh kode manual.

### Pencerminan

```bash
python tugas_2/src/main.py mirror tugas_2/data/input/internet_apple.png tugas_2/data/output/mirror.png --direction horizontal
```

### Rotasi

```bash
python tugas_2/src/main.py rotate tugas_2/data/input/internet_peppers.png tugas_2/data/output/rotate.png --angle 90
```

### Deteksi tepi manual

```bash
python tugas_2/src/main.py edge tugas_2/data/input/internet_landscape.png tugas_2/data/output/edge.png --low 50 --high 150 --blur 5
```

Tahapnya adalah grayscale → Gaussian convolution → Sobel → magnitudo/arah gradien → non-maximum suppression → double threshold → hysteresis.

### Noise reduction manual

```bash
python tugas_2/src/main.py denoise tugas_2/data/input/internet_apple.png tugas_2/data/output/denoise_gaussian.png --method gaussian --kernel 5
python tugas_2/src/main.py denoise tugas_2/data/input/internet_apple.png tugas_2/data/output/denoise_median.png --method median --kernel 5
python tugas_2/src/main.py denoise tugas_2/data/input/internet_apple.png tugas_2/data/output/denoise_bilateral.png --method bilateral --kernel 5
```

### Brightness dan contrast

```bash
python tugas_2/src/main.py brightness tugas_2/data/input/brightness_contrast.jpeg tugas_2/data/output/brightness.png --c 40
python tugas_2/src/main.py contrast tugas_2/data/input/brightness_contrast.jpeg tugas_2/data/output/contrast.png --g 1.5 --p 127
```

### Menjalankan semua proses sekaligus

```bash
python tugas_2/src/run_all.py
```

Output utama adalah `tugas_2/data/output/all_results.png`. Urutan panelnya:

- `P01`–`P04`: empat input unik.
- `P05`: pencerminan horizontal.
- `P06`: rotasi 90°.
- `P07`: deteksi tepi manual.
- `P08`: Gaussian noise reduction.
- `P09`: median noise reduction.
- `P10`: bilateral noise reduction.
- `P11`: brightness.
- `P12`: contrast.

## Catatan performa

Implementasi manual menggunakan loop Python sehingga lebih lambat daripada OpenCV, terutama pada bilateral filter dan gambar beresolusi besar. Keterlambatan tersebut merupakan konsekuensi dari tujuan tugas, yaitu memperlihatkan rumus dan proses per pixel secara eksplisit.

Sumber input PNG dari internet dicatat di `IMAGE_SOURCES.md`. File `brightness_contrast.jpeg` adalah input lokal yang sama untuk brightness dan contrast.
