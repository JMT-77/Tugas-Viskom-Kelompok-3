# Sumber dan persiapan input

Pemilik memilih koin untuk edge dan menyetujui tiga input noise pada 15 Oktober 2026.

| Input | Sumber | Persiapan / penggunaan |
|---|---|---|
| `edge_coins.png` | https://github.com/scikit-image/scikit-image/blob/v0.19.3/skimage/data/coins.png | Nearest-neighbor ke 320x252; edge tanpa noise tambahan. |
| `coins_clean.png` | Sumber coins yang sama | Nearest-neighbor ke 256x202; acuan bilateral. |
| `bilateral_input.png` | Turunan coins_clean | Noise Gaussian SD20, seed20261015. |
| `camera_clean.png` | https://github.com/scikit-image/scikit-image/blob/v0.19.3/skimage/data/camera.png | Nearest-neighbor ke 256x256; acuan median/Gaussian. |
| `median_input.png` | Turunan camera_clean | Salt-and-pepper 6%: peluang hitam 3%, putih 3%, seed20261015. |
| `gaussian_input.png` | Turunan camera_clean | Noise Gaussian SD20, seed20261015, clamp 0..255. |
| `internet_apple.png` | https://commons.wikimedia.org/wiki/Special:FilePath/Apple.jpg?width=330 | Tetap dipakai pencerminan, tidak lagi dipakai denoise. |
| `brightness_contrast.jpeg` | Input lokal proyek sebelumnya | Brightness/contrast. |
| `fitur_warna.jpg` | Input lokal proyek sebelumnya | Modul HSV opsional. |
| `sample_asymmetric.png` | `src/create_sample.py` | Input sintetis kuantisasi, resize dan rotasi. |

scikit-image hanya menjadi sumber berkas gambar; tidak diimpor untuk pengolahan. Pillow hanya memuat gambar. Resize, noise, filter, Canny, PSNR, label dan penulisan hasil memakai rumus/loop standard library. Modul HSV opsional tetap merupakan pengecualian kode lama OpenCV/NumPy.

Sumber dataset: https://scikit-image.org/docs/stable/api/skimage.data.html . Noise di sini sintetis, bukan noise alami. Buat ulang dengan `src/create_filter_inputs.py`. PNG hasil filter tidak dipakai kembali sebagai input. Berkas asli diunduh dari tag v0.19.3; turunan diperkecil manual. Metadata dan hash input disimpan dalam `data/input/filter_input_manifest.json`.
