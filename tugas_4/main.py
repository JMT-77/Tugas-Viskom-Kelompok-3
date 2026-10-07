import cv2
import numpy as np

# 1. Baca citra (OpenCV membaca dalam urutan BGR)
path = "data/input/img.jpg"
citra = cv2.imread(path)
if citra is None:
    raise FileNotFoundError("Citra tidak terbaca, periksa path-nya")

# 2. Konversi ke HSV
hsv = cv2.cvtColor(citra, cv2.COLOR_BGR2HSV)

# 3. Momen warna di ruang HSV: rata-rata dan standar deviasi tiap kanal
piksel = hsv.reshape(-1, 3).astype(float)
rata2 = piksel.mean(axis=0)
std = piksel.std(axis=0)
fitur_momen = np.concatenate([rata2, std])  # 6 angka

# 4. Histogram HSV (rentang Hue di OpenCV: 0-180, S dan V: 0-256)
fitur_hist = []
for kanal, rentang in zip(range(3), [180, 256, 256]):
    hist = cv2.calcHist([hsv], [kanal], None, [8], [0, rentang])
    hist = hist / hist.sum()  # normalisasi agar jumlahnya 1
    fitur_hist.extend(hist.flatten())
fitur_hist = np.array(fitur_hist)  # 24 angka

# 5. Gabungkan menjadi satu vektor fitur warna
fitur_warna = np.concatenate([fitur_momen, fitur_hist])

print("Momen warna (H_mean, S_mean, V_mean, H_std, S_std, V_std):")
print(np.round(fitur_momen, 2))
print("\nHistogram HSV (8 bin Hue | 8 bin Saturation | 8 bin Value):")
print(np.round(fitur_hist, 3))
print("\nUkuran vektor fitur warna:", fitur_warna.shape)  # (30,)