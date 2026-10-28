"""
Instalasi library:
    python -m pip install numpy scipy pillow matplotlib

Berkas yang digunakan:
    citra/building.jpg
    citra/coins.png
    citra/coffee.png
    citra/388_HC.png
    metadata_hc18.csv

ROI pada kode ini khusus untuk gambar dari paket yang sudah diberikan.
"""

from pathlib import Path
from collections import defaultdict
import csv
import json
import math

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle


# ============================================================
# PENGATURAN
# ============================================================

# Pilihan: "garis", "lingkaran", "elips", "janin", "semua"
MODE = "janin"

ROOT = Path(__file__).resolve().parent
FOLDER_CITRA = ROOT / "citra"
FOLDER_HASIL = ROOT / "hasil"

KONFIGURASI = {
    "garis": {
        "gambar": "building.jpg",
        "ukuran": (868, 600),
        "roi": None,
        "jumlah": 10,
    },
    "lingkaran": {
        "gambar": "coins.png",
        "ukuran": (384, 303),
        "roi": None,
        "jumlah": 24,
        "rmin": 15,
        "rmax": 35,
    },
    "elips": {
        "gambar": "coffee.png",
        "ukuran": (600, 400),
        # x kiri, y atas, x kanan, y bawah.
        # Membatasi pencarian pada bibir cangkir.
        "roi": (165, 10, 425, 218),
        "iterasi": 20000,
    },
    "janin": {
        "gambar": "388_HC.png",
        "ukuran": (800, 540),
        "roi": (190, 190, 570, 440),
        "iterasi": 25000,
    },
}


# ============================================================
# 1. MEMBACA CITRA
# ============================================================

def baca_citra(path):
    gambar = Image.open(path).convert("RGBA")

    # Bagian transparan dilapisi putih.
    latar = Image.new("RGBA", gambar.size, "white")
    latar.alpha_composite(gambar)

    return np.array(latar.convert("RGB"))


# ============================================================
# 2. DETEKSI TEPI
# ============================================================

def deteksi_tepi(rgb, sigma=1.2):
    # RGB menjadi grayscale.
    gray = rgb.astype(float) @ np.array([0.299, 0.587, 0.114])

    # Mengurangi noise.
    smooth = ndi.gaussian_filter(gray, sigma)

    # Gradien horizontal dan vertikal.
    gx = ndi.sobel(smooth, axis=1)
    gy = ndi.sobel(smooth, axis=0)
    mag = np.hypot(gx, gy)

    yy, xx = np.indices(gray.shape)

    nx = gx / np.maximum(mag, 1e-9)
    ny = gy / np.maximum(mag, 1e-9)

    # Membandingkan gradien dengan tetangganya untuk menipiskan tepi.
    depan = ndi.map_coordinates(
        mag, [yy + ny, xx + nx], order=1
    )
    belakang = ndi.map_coordinates(
        mag, [yy - ny, xx - nx], order=1
    )

    tipis = (mag >= depan) & (mag >= belakang)

    # Ambang tepi kuat dan lemah.
    tinggi = max(30.0, 0.18 * float(mag.max()))

    kuat = tipis & (mag >= tinggi)
    lemah = tipis & (mag >= 0.5 * tinggi)

    # Mempertahankan tepi lemah yang terhubung dengan tepi kuat.
    edges = ndi.binary_propagation(kuat, mask=lemah)

    edges[[0, -1], :] = False
    edges[:, [0, -1]] = False

    return gray, edges, gx, gy


# ============================================================
# 3. HOUGH TRANSFORM GARIS
# ============================================================

def hough_garis(edges, jumlah=10):
    h, w = edges.shape
    batas = int(np.ceil(np.hypot(h, w)))

    theta = np.deg2rad(np.arange(-90, 90))
    acc = np.zeros((2 * batas + 1, len(theta)), np.int32)

    ys, xs = np.nonzero(edges)

    for k, t in enumerate(theta):
        rho = np.rint(
            xs * np.cos(t) + ys * np.sin(t)
        ).astype(int)

        np.add.at(acc[:, k], rho + batas, 1)

    work = acc.copy()
    hasil = []

    for _ in range(jumlah):
        ri, ti = np.unravel_index(
            np.argmax(work), work.shape
        )
        suara = int(work[ri, ti])

        if suara < 20:
            break

        hasil.append({
            "rho": int(ri - batas),
            "theta_derajat": int(ti - 90),
            "suara": suara,
        })

        # Menekan puncak tetangga agar tidak mendeteksi garis berulang.
        for dt in range(-6, 7):
            idx = ti + dt

            if 0 <= idx < len(theta):
                rr = ri
            else:
                rr = 2 * batas - ri

            work[
                max(0, rr - 10):rr + 11,
                idx % len(theta),
            ] = 0

    return hasil


# ============================================================
# 4. HOUGH TRANSFORM LINGKARAN
# ============================================================

def hough_lingkaran(
    edges, gx, gy, rmin=15, rmax=35, jumlah=24
):
    h, w = edges.shape
    ys, xs = np.nonzero(edges)

    panjang = np.maximum(
        np.hypot(gx[ys, xs], gy[ys, xs]),
        1e-9,
    )

    nx = gx[ys, xs] / panjang
    ny = gy[ys, xs] / panjang

    radii = np.arange(rmin, rmax + 1)
    acc = np.zeros((len(radii), h, w), np.uint32)

    for k, r in enumerate(radii):
        for tanda in (-1, 1):
            cx = np.rint(xs + tanda * r * nx).astype(int)
            cy = np.rint(ys + tanda * r * ny).astype(int)

            valid = (
                (cx >= 0) & (cx < w)
                & (cy >= 0) & (cy < h)
            )

            np.add.at(
                acc[k],
                (cy[valid], cx[valid]),
                1,
            )

    smooth = ndi.uniform_filter(
        acc.astype(float),
        size=(3, 5, 5),
    )

    hasil = []
    yy, xx = np.ogrid[:h, :w]

    for _ in range(jumlah):
        k, cy, cx = np.unravel_index(
            np.argmax(smooth), smooth.shape
        )

        if smooth[k, cy, cx] <= 0.02:
            break

        r = int(radii[k])

        hasil.append({
            "cx": int(cx),
            "cy": int(cy),
            "r": r,
            "skor_akumulator": float(smooth[k, cy, cx]),
        })

        # Mencegah lingkaran ganda pada satu pusat.
        sekitar_pusat = (
            (xx - cx) ** 2 + (yy - cy) ** 2
            < max(20, r * 0.6) ** 2
        )

        smooth[:, sekitar_pusat] = 0

    return hasil


# ============================================================
# 5. MEMBENTUK KANDIDAT ELIPS DARI LIMA TITIK
# ============================================================

def elips_dari_lima_titik(points):
    origin = points.mean(axis=0)
    scale = max(float(points.std()), 1.0)

    x, y = ((points - origin) / scale).T

    design = np.column_stack([
        x * x,
        x * y,
        y * y,
        x,
        y,
        np.ones(5),
    ])

    _, singular, vt = np.linalg.svd(
        design, full_matrices=True
    )

    if singular[-1] < 1e-7:
        return None

    A, B, C, D, E, F = vt[-1]

    # Syarat konik agar berbentuk elips.
    if B * B - 4 * A * C >= 0:
        return None

    Q = np.array([
        [A, B / 2],
        [B / 2, C],
    ])

    try:
        center = -0.5 * np.linalg.solve(Q, [D, E])

        value = (
            center @ Q @ center
            + np.dot([D, E], center)
            + F
        )

        eigen, vectors = np.linalg.eigh(Q)

        if np.any(np.abs(eigen) < 1e-12):
            return None

        axes2 = -value / eigen

        if np.any(axes2 <= 0):
            return None

        axes = np.sqrt(axes2) * scale
        j = int(np.argmax(axes))

        phi = math.atan2(
            vectors[1, j],
            vectors[0, j],
        ) % math.pi

        cx, cy = center * scale + origin

        return np.array([
            cx,
            cy,
            axes[j],
            axes[1 - j],
            phi,
        ])

    except np.linalg.LinAlgError:
        return None


# ============================================================
# 6. MENGUKUR DUKUNGAN TEPI TERHADAP ELIPS
# ============================================================

def dukungan_elips(parameter, distance):
    cx, cy, a, b, phi = parameter

    t = np.linspace(
        0, 2 * math.pi, 360, endpoint=False
    )

    x = (
        cx
        + a * np.cos(t) * np.cos(phi)
        - b * np.sin(t) * np.sin(phi)
    )

    y = (
        cy
        + a * np.cos(t) * np.sin(phi)
        + b * np.sin(t) * np.cos(phi)
    )

    jarak = ndi.map_coordinates(
        distance,
        [y, x],
        order=1,
        mode="constant",
        cval=np.inf,
    )

    # Sampel dianggap didukung jika berjarak maksimal 2,5 piksel.
    return float(np.mean(jarak <= 2.5))


# ============================================================
# 7. RANDOMIZED HOUGH TRANSFORM ELIPS
# ============================================================

def hough_elips(edges, iterasi=20000, seed=42):
    ys, xs = np.nonzero(edges)
    points = np.column_stack([xs, ys]).astype(float)

    if len(points) < 5:
        return None

    h, w = edges.shape
    distance = ndi.distance_transform_edt(~edges)

    rng = np.random.default_rng(seed)
    bins = defaultdict(lambda: [0, None, 0.0])

    for _ in range(iterasi):
        indeks = rng.choice(len(points), 5, replace=False)
        parameter = elips_dari_lima_titik(points[indeks])

        if parameter is None:
            continue

        cx, cy, a, b, phi = parameter

        valid = (
            0 <= cx < w
            and 0 <= cy < h
            and 15 <= b <= a <= 0.55 * max(h, w)
            and b / a >= 0.35
        )

        if not valid:
            continue

        key = tuple(
            np.rint([
                cx / 8,
                cy / 8,
                a / 8,
                b / 8,
                np.rad2deg(phi) / 10,
            ]).astype(int)
        )

        score = dukungan_elips(parameter, distance)

        if score < 0.5:
            continue

        cell = bins[key]
        cell[0] += 1

        if score > cell[2]:
            cell[1] = parameter
            cell[2] = score

    if not bins:
        return None

    suara, parameter, score = max(
        bins.values(),
        key=lambda item: (item[0], item[2]),
    )

    return {
        "cx": float(parameter[0]),
        "cy": float(parameter[1]),
        "a": float(parameter[2]),
        "b": float(parameter[3]),
        "sudut_derajat": float(np.rad2deg(parameter[4])),
        "suara": int(suara),
        "dukungan_tepi": float(score),
    }


# ============================================================
# 8. METADATA DAN PERHITUNGAN HC
# ============================================================

def baca_metadata(gambar):
    lokasi = ROOT / "metadata_hc18.csv"

    if not lokasi.is_file():
        raise FileNotFoundError(
            f"Metadata tidak ditemukan: {lokasi}"
        )

    with lokasi.open(
        newline="", encoding="utf-8-sig"
    ) as file:
        for row in csv.DictReader(file):
            row = {
                k.strip().lower(): v
                for k, v in row.items()
                if k
            }

            if row.get("filename", "").strip() == gambar.name:
                skala = float(row["pixel size(mm)"])
                acuan = float(row["head circumference (mm)"])

                if (
                    not math.isfinite(skala)
                    or not math.isfinite(acuan)
                    or skala <= 0
                    or acuan <= 0
                ):
                    raise ValueError(
                        "Skala dan HC acuan harus positif."
                    )

                return skala, acuan

    raise ValueError(
        f"Metadata {gambar.name} tidak ditemukan."
    )


def hitung_biometri(elips, skala, hc_acuan):
    a = elips["a"]
    b = elips["b"]

    # a dan b adalah setengah panjang sumbu.
    hc_px = math.pi * (
        3 * (a + b)
        - math.sqrt((3 * a + b) * (a + 3 * b))
    )

    hc_mm = hc_px * skala

    hasil = {
        "hc_px": hc_px,
        "hc_mm": hc_mm,
        "hc_acuan_mm": hc_acuan,
        "selisih_hc_mm": abs(hc_mm - hc_acuan),
    }

    # Demonstrasi proksi BPD, bukan pengukuran BPD klinis.
    bpd_cm = 2 * b * skala / 10
    hasil["proksi_bpd_cm"] = bpd_cm
    hasil["catatan"] = (
        "Demonstrasi geometris; bukan pengukuran klinis."
    )

    if 1.4 <= bpd_cm <= 10.17:
        ga = (
            9.54
            + 1.482 * bpd_cm
            + 0.1676 * bpd_cm ** 2
        )

        total_hari = int(round(ga * 7))

        hasil["ga_minggu"] = ga
        hasil["minggu"] = total_hari // 7
        hasil["hari"] = total_hari % 7

    return hasil


# ============================================================
# 9. VISUALISASI
# ============================================================

def tampilkan_hasil(rgb, edges, mode, deteksi, roi, nama):
    h, w = edges.shape

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(rgb)
    axes[1].imshow(edges, cmap="gray", vmin=0, vmax=1)
    axes[2].imshow(rgb)

    axes[0].set_title("Citra asli dan area pencarian")
    axes[1].set_title(
        "Peta tepi dalam ROI" if roi else "Peta tepi"
    )
    axes[2].set_title(f"Hasil {mode}")

    # Kotak cyan memperlihatkan area pencarian.
    if roi:
        x1, y1, x2, y2 = roi

        axes[0].add_patch(Rectangle(
            (x1, y1),
            x2 - x1,
            y2 - y1,
            fill=False,
            edgecolor="cyan",
            linewidth=1.5,
            linestyle="--",
        ))

    for parameter in deteksi:
        if mode == "garis":
            t = math.radians(parameter["theta_derajat"])
            rho = parameter["rho"]

            x0 = rho * math.cos(t)
            y0 = rho * math.sin(t)
            panjang = math.hypot(h, w)

            axes[2].plot(
                [
                    x0 - panjang * math.sin(t),
                    x0 + panjang * math.sin(t),
                ],
                [
                    y0 + panjang * math.cos(t),
                    y0 - panjang * math.cos(t),
                ],
                color="red",
                linewidth=1,
            )

        elif mode == "lingkaran":
            axes[2].add_patch(Circle(
                (parameter["cx"], parameter["cy"]),
                parameter["r"],
                fill=False,
                color="red",
            ))

            axes[2].plot(
                parameter["cx"],
                parameter["cy"],
                "r+",
            )

        else:
            axes[2].add_patch(Ellipse(
                (parameter["cx"], parameter["cy"]),
                width=2 * parameter["a"],
                height=2 * parameter["b"],
                angle=parameter["sudut_derajat"],
                fill=False,
                color="lime",
                linewidth=2,
            ))

    for ax in axes:
        ax.set_xlim(-0.5, w - 0.5)
        ax.set_ylim(h - 0.5, -0.5)
        ax.axis("off")

    fig.tight_layout()

    lokasi = FOLDER_HASIL / f"{nama}_{mode}.png"
    fig.savefig(lokasi, dpi=150)

    plt.show()
    plt.close(fig)


# ============================================================
# 10. PROSES UTAMA
# ============================================================

def jalankan(mode):
    konfigurasi = KONFIGURASI[mode]
    path = FOLDER_CITRA / konfigurasi["gambar"]

    if not path.is_file():
        raise FileNotFoundError(
            f"Gambar tidak ditemukan:\n{path}\n"
            "Pastikan folder citra sejajar dengan file Python."
        )

    rgb = baca_citra(path)
    h, w = rgb.shape[:2]

    # Menghindari penggunaan ROI contoh pada ukuran gambar berbeda.
    if (w, h) != konfigurasi["ukuran"]:
        raise ValueError(
            f"Ukuran {path.name} adalah {w} x {h}, "
            f"sedangkan konfigurasi ini untuk "
            f"{konfigurasi['ukuran']}.\n"
            "Gunakan gambar dari paket atau sesuaikan ROI."
        )

    _, edges, gx, gy = deteksi_tepi(rgb)

    jumlah_tepi_total = int(edges.sum())
    roi = konfigurasi["roi"]

    # PENTING: membatasi titik tepi sebelum proses Hough.
    if roi is not None:
        x1, y1, x2, y2 = roi

        if not (
            0 <= x1 < x2 <= w
            and 0 <= y1 < y2 <= h
        ):
            raise ValueError("ROI berada di luar gambar.")

        mask = np.zeros_like(edges, dtype=bool)
        mask[y1:y2, x1:x2] = True

        edges = edges & mask

    jumlah_tepi_dipakai = int(edges.sum())

    print(f"\nMemproses: {path.name}")
    print(f"Mode: {mode}")
    print(f"Ukuran: {w} x {h}")
    print(f"ROI: {roi}")
    print(f"Tepi total: {jumlah_tepi_total}")
    print(f"Tepi yang dipakai: {jumlah_tepi_dipakai}")

    if jumlah_tepi_dipakai == 0:
        raise ValueError(
            "Peta tepi kosong. Periksa gambar dan ROI."
        )

    informasi = {
        "mode": mode,
        "gambar": path.name,
        "roi": roi,
        "jumlah_tepi_total": jumlah_tepi_total,
        "jumlah_tepi_dipakai": jumlah_tepi_dipakai,
    }

    if mode == "garis":
        deteksi = hough_garis(
            edges,
            jumlah=konfigurasi["jumlah"],
        )

    elif mode == "lingkaran":
        deteksi = hough_lingkaran(
            edges,
            gx,
            gy,
            rmin=konfigurasi["rmin"],
            rmax=konfigurasi["rmax"],
            jumlah=konfigurasi["jumlah"],
        )

    else:
        elips = hough_elips(
            edges,
            iterasi=konfigurasi["iterasi"],
            seed=42,
        )

        deteksi = [] if elips is None else [elips]

        if mode == "janin" and elips is not None:
            skala, acuan = baca_metadata(path)

            informasi["biometri"] = hitung_biometri(
                elips,
                skala,
                acuan,
            )

    informasi["deteksi"] = deteksi

    if not deteksi:
        print(
            "Tidak ada kandidat yang lolos. "
            "Periksa ROI dan parameter."
        )

    FOLDER_HASIL.mkdir(parents=True, exist_ok=True)

    lokasi_json = (
        FOLDER_HASIL / f"{path.stem}_{mode}.json"
    )

    lokasi_json.write_text(
        json.dumps(
            informasi,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    print(json.dumps(
        informasi,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    ))

    tampilkan_hasil(
        rgb,
        edges,
        mode,
        deteksi,
        roi,
        path.stem,
    )


if __name__ == "__main__":
    try:
        if MODE == "semua":
            for pilihan in KONFIGURASI:
                jalankan(pilihan)
        elif MODE in KONFIGURASI:
            jalankan(MODE)
        else:
            raise ValueError(
                "MODE harus garis, lingkaran, elips, "
                "janin, atau semua."
            )

    except (OSError, ValueError, KeyError) as error:
        print(f"\nGAGAL: {error}")
        raise SystemExit(1)
