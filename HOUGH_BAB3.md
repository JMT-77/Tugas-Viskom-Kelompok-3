# Hough Bab 3

Install dependensi dari root proyek:

```powershell
python -m pip install -r requirements.txt
python hough_bab3.py
```

Mode default `janin` membaca `citra/388_HC.png`, menghasilkan PNG dan JSON di `hasil/`, lalu menampilkan gambar. Ubah `MODE` pada skrip untuk `garis`, `lingkaran`, `elips`, atau `semua`; mode lain memerlukan `building.jpg` (868×600), `coins.png` (384×303), dan `coffee.png` (600×400) di folder `citra`. ROI dan parameter hanya cocok untuk gambar yang sesuai konfigurasi.

Empat gambar input tersedia di `citra/`; hasil proses di `hasil/` tetap lokal dan tidak di-commit.

## Sumber gambar

- `388_HC.png`: van den Heuvel, de Bruijn, de Korte, dan van Ginneken, [dataset HC18](https://doi.org/10.5281/zenodo.1327317), CC BY 4.0 ([lisensi](https://creativecommons.org/licenses/by/4.0/)). Gambar tidak dimodifikasi; SHA-256: `5bec66540df57bab374f442d7e978591754b0aae9f6b302c45e6dae12a2b125d`. `metadata_hc18.csv` khusus untuk gambar ini; jangan gunakan nilainya untuk gambar lain.
- `coffee.png`: Rachel Michetti / Pikolo Espresso Bar, CC0; `coins.png`: Brooklyn Museum Collection, tanpa pembatasan hak cipta yang diketahui. Keduanya dari [data contoh scikit-image](https://scikit-image.org/docs/0.20.x/api/skimage.data.html).
- `building.jpg`: gambar referensi yang disediakan pengguna; sumber asal belum diketahui.

Hasil biometri adalah demonstrasi geometris untuk pembelajaran, bukan pengukuran klinis.
