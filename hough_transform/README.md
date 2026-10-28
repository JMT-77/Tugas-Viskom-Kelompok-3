# Hough Transform

Kode di `src/main.py`, input contoh di `data/input/janin.jpg`, dan hasil di `data/output/`. Default memakai lokasi skrip sehingga tidak bergantung pada current working directory.

```powershell
python -m pip install -r hough_transform/requirements.txt
python hough_transform/src/main.py --tanpa-tampilan
python hough_transform/src/main.py --help
```

Untuk gambar lain, berikan path sebagai argumen pertama; tersedia opsi `--roi X1 Y1 X2 Y2` dan `--output FOLDER`.

Algoritma asli dipertahankan: praproses, Hough garis/lingkaran/elips, penyaringan kandidat, dan visualisasi. Output: enam PNG, `parameter_dan_hasil.json`, `ringkasan.csv`, serta ZIP di `data/output.zip`. Hasil lama dipindahkan bersama data tanpa diklaim sebagai pengujian ulang terbaru.

Accumulator adalah suara kandidat, bukan persentase akurasi. Kode mendeteksi bentuk geometri; belum otomatis mengenali anatomi atau menghitung usia janin.
