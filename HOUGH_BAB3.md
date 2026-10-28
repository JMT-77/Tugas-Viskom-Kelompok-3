# Hough Bab 3

Install dependensi dari root proyek:

```powershell
python -m pip install -r requirements.txt
python hough_bab3.py
```

Mode default `janin` membaca `citra/388_HC.png`, menghasilkan PNG dan JSON di `hasil/`, lalu menampilkan gambar. Ubah `MODE` pada skrip untuk `garis`, `lingkaran`, `elips`, atau `semua`; mode lain memerlukan `building.jpg` (868×600), `coins.png` (384×303), dan `coffee.png` (600×400) di folder `citra`. ROI dan parameter hanya cocok untuk gambar yang sesuai konfigurasi.

File gambar referensi dan hasil bersifat lokal dan tidak di-commit. Untuk memperoleh ulang gambar `388_HC.png`, unduh `training_set.zip` dari [dataset HC18 resmi](https://zenodo.org/records/1327317), lalu salin file `388_HC.png` dari dalam arsip ke `citra/`. SHA-256 file yang diuji: `5bec66540df57bab374f442d7e978591754b0aae9f6b302c45e6dae12a2b125d`. `metadata_hc18.csv` mencatat nilai untuk file tersebut; jangan gunakan nilai ini untuk gambar lain.

Contoh koin dan kopi lokal berasal dari data contoh scikit-image. `building.jpg` harus diperoleh dari paket input yang sesuai. Hasil biometri adalah demonstrasi geometris untuk pembelajaran, bukan pengukuran klinis.
