# Proyek Visi Komputer

Kode dan data dikelompokkan berdasarkan materi dalam tiga folder huruf kecil dengan underscore.

```text
viskom/
  dasar_pengolahan_citra_digital/
    src/           # properti/geometri, filter/intensitas, tambahan fitur warna
    tests/
    data/input/
    data/output/   # PNG sebelum/sesudah per fungsi dan perhitungan JSON/TXT
    README.md
    requirements.txt
  morfologi_citra/
    src/
    tests/
    data/input/
    data/output/
    README.md
    REFERENCES.md
    requirements.txt
  hough_transform/
    src/main.py
    data/input/janin.jpg
    data/output/
    README.md
    requirements.txt
  README.md
  requirements.txt
```

## Instalasi

```powershell
python -m pip install -r requirements.txt
```

Untuk operasi dasar saja, cukup install `dasar_pengolahan_citra_digital/requirements.txt`. Pillow hanya membaca gambar; operasi inti dan output dasar manual. Morfologi, Hough dan tambahan HSV masih memakai pustaka implementasi lama. Perapian ini tidak mengganti algoritma tersebut.

## Pengolahan citra dasar

```powershell
python dasar_pengolahan_citra_digital/src/run_all.py
python dasar_pengolahan_citra_digital/src/main.py --help
python -m unittest discover -s dasar_pengolahan_citra_digital/tests -v
```

Output: `dasar_pengolahan_citra_digital/data/output/`. Runner mencakup properti depth/resolusi, kuantisasi, resize, rotasi, pencerminan, deteksi tepi, reduksi noise, brightness dan contrast. PNG dipisah per fungsi. Detail rumus, parameter dan tambahan HSV: [README pengolahan dasar](dasar_pengolahan_citra_digital/README.md).

## Morfologi

```powershell
python morfologi_citra/src/main.py morfologi_citra/data/input/document_scan.png morfologi_citra/data/output/document_morphology_results.png --kernel 3
```

Kode, input dan komposit dipertahankan. Detail: [README morfologi](morfologi_citra/README.md).

## Hough Transform

```powershell
python hough_transform/src/main.py --tanpa-tampilan
```

Default membaca `hough_transform/data/input/janin.jpg` dan menulis ke `hough_transform/data/output/`. Kode Python sudah terpisah dari data input. Detail: [README Hough](hough_transform/README.md).

Folder bernomor, wrapper duplikat, cache, komposit dasar lama, dan dokumen petunjuk yang path-nya usang digantikan struktur ini. Repositori Git dipertahankan; tidak ada merge atau SQL yang dijalankan.

## Jupyter Notebook

Install dependensi proyek dan Jupyter dalam environment Python yang sama: `python -m pip install -r requirements.txt notebook ipykernel`. Dari root proyek jalankan `jupyter notebook` dan buka `viskom.ipynb`. Notebook menyediakan kode dan sel terpisah untuk Hough, pengolahan dasar, fitur warna, dan morfologi. Jalankan sel persiapan serta definisi fungsi yang dibutuhkan sebelum sel operasi. Hasil Hough disimpan ke folder sementara yang ditampilkan di notebook; salin hasil yang ingin disimpan. Sumber gambar Hough ada di [HOUGH_BAB3.md](HOUGH_BAB3.md).
