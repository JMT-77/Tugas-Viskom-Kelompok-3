#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUGAS 3: HOUGH TRANSFORM GARIS, LINGKARAN, DAN ELIPS PADA USG JANIN
Nama: ...
NIM: ...
Kelas: ...

Persiapan (Python 3.10 atau lebih baru):
    python -m pip install numpy scipy scikit-image matplotlib Pillow

Cara menjalankan:
    python Tugas_3_Hough_Transform_Janin.py janin.jpg
    python Tugas_3_Hough_Transform_Janin.py

Tanpa argumen, program menggunakan janin.jpg di folder skrip jika tersedia.
Jika tidak tersedia, program membuka dialog pemilihan gambar atau meminta path.
Gunakan JPG/PNG USG janin milik Anda; gambar belum disertakan dalam skrip.

Pilihan tambahan:
    --roi X1 Y1 X2 Y2    Batasi pencarian pada koordinat gambar asli.
    --tanpa-tampilan    Simpan semua hasil tanpa membuka jendela grafik.
    --output FOLDER     Tentukan folder hasil.

Hasil: gambar asli, praproses, garis, lingkaran, elips, perbandingan,
ringkasan CSV, parameter JSON, dan arsip ZIP. Satu jendela perbandingan
dibuka setelah seluruh hasil tersimpan. Parameter deteksi dapat diubah
pada bagian KONFIGURASI dalam fungsi proses_gambar().

Garis: rho = x*cos(theta) + y*sin(theta).
Lingkaran: (x-xc)**2 + (y-yc)**2 = r**2.
Elips: x'**2/a**2 + y'**2/b**2 = 1 pada koordinat setelah rotasi.
Accumulator menyimpan suara kandidat, bukan persentase akurasi.
ROI yang bersih membantu mengurangi deteksi tulisan dan skala pada USG.
Hasil adalah bentuk geometri; belum otomatis mengenali anatomi janin.

Referensi:
https://scikit-image.org/docs/stable/api/skimage.transform.html
https://scikit-image.org/docs/stable/auto_examples/edges/plot_circular_elliptical_hough_transform.html
"""

import argparse
from pathlib import Path
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Tugas 3 — Hough Transform pada gambar USG janin.")
    parser.add_argument("gambar", nargs="?", help="Path gambar JPG/PNG; gunakan tanda kutip jika ada spasi.")
    parser.add_argument("--roi", nargs=4, type=int, metavar=("X1", "Y1", "X2", "Y2"),
                        help="Kotak ROI pada gambar asli; default seluruh gambar.")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "hasil_hough_janin",
                        help="Folder hasil; default di samping skrip.")
    parser.add_argument("--tanpa-tampilan", action="store_true", help="Simpan hasil tanpa membuka grafik.")
    return parser.parse_args()


def pilih_gambar(path_input):
    if path_input:
        return Path(path_input).expanduser().resolve()
    default = Path(__file__).resolve().parent / "janin.jpg"
    if default.is_file():
        return default
    # Tkinter bawaan Python dapat menyediakan dialog pilih file di desktop.
    root = None
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        selected = filedialog.askopenfilename(
            title="Pilih gambar USG janin",
            filetypes=[("Gambar", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"), ("Semua file", "*.*")],
        )
    except Exception as exc:
        # Tidak semua lingkungan Python menyediakan Tk atau layar desktop.
        try:
            selected = input("Masukkan path gambar USG janin: ").strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            raise ValueError("Berikan gambar: python Tugas_3_Hough_Transform_Janin.py janin.jpg") from exc
    finally:
        if root is not None:
            root.destroy()
    if not selected:
        print("Pemilihan gambar dibatalkan.")
        raise SystemExit(0)
    return Path(selected).expanduser().resolve()


def proses_gambar(image_path, args):
    # IMPOR PUSTAKA
    from pathlib import Path
    from time import perf_counter
    import csv
    import json
    import zipfile

    import numpy as np
    import matplotlib
    if args.tanpa_tampilan:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    from PIL import Image, ImageOps
    from scipy import ndimage as ndi
    from skimage import color, exposure, filters, morphology, transform
    from skimage.feature import canny
    from skimage.draw import ellipse_perimeter
    from skimage.transform import (
        hough_line, hough_line_peaks,
        hough_circle, hough_circle_peaks, hough_ellipse,
    )
    import skimage

    plt.rcParams["figure.dpi"] = 110
    print("scikit-image:", skimage.__version__)

    # KONFIGURASI — sesuaikan dengan gambar
    ROI = tuple(args.roi) if args.roi else None
    MAX_SIDE = 320   # Batas sisi terbesar ROI untuk garis/lingkaran.

    CLAHE_CLIP = 0.02
    CANNY_SIGMA = 2.0
    CANNY_LOW = 0.10
    CANNY_HIGH = 0.25
    MIN_EDGE_COMPONENT = 12

    LINE_PEAK_RATIO = 0.45  # Ambang relatif terhadap puncak accumulator garis.
    MAX_LINES = 6
    CIRCLE_RADIUS_FRACTION = (0.15, 0.48)
    CIRCLE_RADIUS_STEP = 2
    CIRCLE_VOTE_THRESHOLD = 0.35  # Ambang accumulator ternormalisasi.
    MAX_CIRCLES = 3

    ELLIPSE_MAX_SIDE = 128
    ELLIPSE_MAX_EDGE_POINTS = 450  # Membatasi biaya komputasi; dapat mengurangi detail.
    ELLIPSE_ACCURACY = 5          # Lebar bin; lebih besar = estimasi lebih kasar.
    ELLIPSE_VOTE_THRESHOLD = 12
    ELLIPSE_MIN_SIZE_FRACTION = 0.30
    ELLIPSE_MAX_SIZE_FRACTION = 0.50
    ELLIPSE_MIN_AXIS_RATIO = 0.35
    ELLIPSE_MIN_EDGE_SUPPORT = 0.65  # Proporsi perimeter dekat tepi Canny (toleransi 1.5 px).
    RANDOM_SEED = 42

    OUTPUT_DIR = args.output.expanduser().resolve()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. MEMBACA GAMBAR
    if not image_path.is_file():
        raise FileNotFoundError(f"Gambar tidak ditemukan: {image_path}")
    with Image.open(image_path) as im:
        rgb_original = np.array(ImageOps.exif_transpose(im).convert("RGB"))

    original_h, original_w = rgb_original.shape[:2]
    print(f"Ukuran gambar asli: {original_w} × {original_h} piksel")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.imshow(rgb_original)
    ax.set(title="Gambar USG asli — gunakan koordinat ini untuk ROI", xlabel="x (piksel)", ylabel="y (piksel)")
    ax.grid(alpha=0.2)
    fig.savefig(OUTPUT_DIR / "00_gambar_asli.png", bbox_inches="tight")
    plt.close(fig)

    # 2. ROI, GRAYSCALE, MEDIAN, CLAHE, DAN CANNY
    if ROI is None:
        x1, y1, x2, y2 = 0, 0, original_w, original_h
    else:
        if len(ROI) != 4 or any(int(v) != v for v in ROI):
            raise ValueError("ROI harus berisi empat bilangan bulat (x1, y1, x2, y2).")
        x1, y1, x2, y2 = map(int, ROI)
    if not (0 <= x1 < x2 <= original_w and 0 <= y1 < y2 <= original_h):
        raise ValueError("ROI tidak valid atau berada di luar gambar.")
    if min(x2 - x1, y2 - y1) < 32:
        raise ValueError("ROI terlalu kecil. Gunakan lebar dan tinggi minimal 32 piksel.")
    if not (0 <= CANNY_LOW < CANNY_HIGH <= 1):
        raise ValueError("Gunakan 0 <= CANNY_LOW < CANNY_HIGH <= 1.")

    roi_original = rgb_original[y1:y2, x1:x2]
    ratio = min(1.0, MAX_SIDE / max(roi_original.shape[:2]))
    work_h, work_w = [max(1, round(s * ratio)) for s in roi_original.shape[:2]]
    rgb = transform.resize(roi_original, (work_h, work_w, 3), anti_aliasing=True)
    gray = color.rgb2gray(rgb)
    denoised = filters.median(gray, footprint=morphology.disk(2))
    # Citra konstan dipertahankan agar tidak dibuat seolah memiliki tepi.
    enhanced = (exposure.equalize_adapthist(denoised, clip_limit=CLAHE_CLIP)
                if np.ptp(denoised) > 1e-8 else denoised.copy())

    def clean_edges(edge_map, min_size):
        labels, _ = ndi.label(edge_map, structure=np.ones((3, 3)))
        sizes = np.bincount(labels.ravel())
        keep = sizes >= min_size
        keep[0] = False
        return keep[labels]

    edges = canny(enhanced, sigma=CANNY_SIGMA,
                  low_threshold=CANNY_LOW, high_threshold=CANNY_HIGH)
    edges = clean_edges(edges, MIN_EDGE_COMPONENT)
    print(f"ROI kerja: {work_w} × {work_h}; jumlah piksel tepi: {edges.sum()}")
    print("Koordinat hasil garis/lingkaran memakai piksel ROI kerja, bukan gambar asli.")

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, image, title in zip(axes, [rgb, gray, enhanced, edges],
                              ["ROI", "Grayscale", "Median + CLAHE", "Canny"]):
        ax.imshow(image, cmap="gray")
        ax.set_title(title)
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "01_praproses.png", bbox_inches="tight")
    plt.close(fig)

    # 3. HOUGH TRANSFORM GARIS
    t0 = perf_counter()
    tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    hspace, angles, distances = hough_line(edges, theta=tested_angles)
    line_records = []
    if hspace.max() > 0:
        votes, peak_angles, peak_distances = hough_line_peaks(
            hspace, angles, distances,
            threshold=max(1, LINE_PEAK_RATIO * hspace.max()),
            num_peaks=MAX_LINES,
        )
        for vote, theta, rho in zip(votes, peak_angles, peak_distances):
            line_records.append({"votes": int(vote), "rho_px": float(rho),
                                 "theta_normal_deg": float(np.rad2deg(theta))})
    line_seconds = perf_counter() - t0

    def draw_lines(ax):
        for item in line_records:
            theta = np.deg2rad(item["theta_normal_deg"])
            rho = item["rho_px"]
            if abs(np.sin(theta)) > 1e-8:
                xs = np.array([0, work_w - 1])
                ys = (rho - xs * np.cos(theta)) / np.sin(theta)
                ax.plot(xs, ys, color="lime", linewidth=1.5)
            else:
                ax.axvline(rho / np.cos(theta), color="lime", linewidth=1.5)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(rgb)
    draw_lines(axes[0])
    axes[0].set(xlim=(0, work_w - 1), ylim=(work_h - 1, 0), title="Kandidat garis")
    axes[0].axis("off")
    axes[1].imshow(np.log1p(hspace), cmap="magma", aspect="auto",
                   extent=[np.rad2deg(angles[0]), np.rad2deg(angles[-1]), distances[-1], distances[0]])
    axes[1].set(title="Accumulator garis (log1p)", xlabel="theta normal (derajat)", ylabel="rho (piksel)")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "02_hough_garis.png", bbox_inches="tight")
    plt.close(fig)
    print(f"Jumlah kandidat garis: {len(line_records)}; waktu: {line_seconds:.3f} detik")
    for item in line_records:
        print(item)

    # 4. HOUGH TRANSFORM LINGKARAN
    rmin = max(4, round(min(work_h, work_w) * CIRCLE_RADIUS_FRACTION[0]))
    rmax = round(min(work_h, work_w) * CIRCLE_RADIUS_FRACTION[1])
    if rmax <= rmin or CIRCLE_RADIUS_STEP < 1:
        raise ValueError("Rentang radius atau langkah radius tidak valid.")
    radii_to_test = np.arange(rmin, rmax + 1, CIRCLE_RADIUS_STEP)
    t0 = perf_counter()
    circle_records = []
    if edges.any():
        circle_hspace = hough_circle(edges, radii_to_test, normalize=True)
        accum, centers_x, centers_y, radii = hough_circle_peaks(
            circle_hspace, radii_to_test,
            threshold=CIRCLE_VOTE_THRESHOLD,
            min_xdistance=max(5, rmin // 2), min_ydistance=max(5, rmin // 2),
            total_num_peaks=MAX_CIRCLES,
        )
        for score, cx, cy, radius in zip(accum, centers_x, centers_y, radii):
            circle_records.append({"center_x_px": int(cx), "center_y_px": int(cy),
                                   "radius_px": int(radius), "normalized_votes": float(score)})
        del circle_hspace  # Lepaskan accumulator besar setelah pengambilan puncak.
    circle_seconds = perf_counter() - t0

    def draw_circles(ax):
        for index, item in enumerate(circle_records, start=1):
            cx, cy, radius = item["center_x_px"], item["center_y_px"], item["radius_px"]
            ax.add_patch(Circle((cx, cy), radius, fill=False, edgecolor="cyan", linewidth=2))
            ax.plot(cx, cy, "r+", markersize=7)
            ax.text(cx, cy, f" C{index}", color="yellow", fontsize=9)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.imshow(rgb)
    draw_circles(ax)
    ax.set(xlim=(0, work_w - 1), ylim=(work_h - 1, 0), title="Kandidat lingkaran")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "03_hough_lingkaran.png", bbox_inches="tight")
    plt.close(fig)
    print(f"Radius diuji: {rmin}–{rmax} piksel; jumlah kandidat: {len(circle_records)}")
    print(f"Waktu: {circle_seconds:.3f} detik")
    for item in circle_records:
        print(item)
    if not circle_records:
        print("Tidak ada kandidat melewati ambang. Periksa ROI, Canny, radius, atau ambang suara.")

    # 5. HOUGH TRANSFORM ELIPS
    small_ratio = min(1.0, ELLIPSE_MAX_SIDE / max(work_h, work_w))
    ellipse_h, ellipse_w = [max(1, round(s * small_ratio)) for s in (work_h, work_w)]
    small_enhanced = transform.resize(enhanced, (ellipse_h, ellipse_w), anti_aliasing=True)
    ellipse_edges = canny(small_enhanced, sigma=max(1.0, CANNY_SIGMA * small_ratio),
                          low_threshold=CANNY_LOW, high_threshold=CANNY_HIGH)
    ellipse_edges = clean_edges(ellipse_edges, max(3, round(MIN_EDGE_COMPONENT * small_ratio)))
    ellipse_reference_edges = ellipse_edges.copy()
    edge_distance = ndi.distance_transform_edt(~ellipse_reference_edges)
    all_points = np.argwhere(ellipse_edges)
    if len(all_points) > ELLIPSE_MAX_EDGE_POINTS:
        rng = np.random.default_rng(RANDOM_SEED)
        chosen = rng.choice(len(all_points), size=ELLIPSE_MAX_EDGE_POINTS, replace=False)
        points = all_points[chosen]
        ellipse_edges = np.zeros_like(ellipse_edges)
        ellipse_edges[points[:, 0], points[:, 1]] = True
        print(f"Titik tepi dikurangi: {len(all_points)} → {len(points)} untuk mempercepat Hough elips.")

    ellipse_min_size = max(8, round(min(ellipse_h, ellipse_w) * ELLIPSE_MIN_SIZE_FRACTION))
    ellipse_max_size = max(6, round(min(ellipse_h, ellipse_w) * ELLIPSE_MAX_SIZE_FRACTION))
    ellipse_record = None
    ellipse_curve = None
    t0 = perf_counter()
    if ellipse_edges.sum() >= 5:
        candidates = hough_ellipse(
            ellipse_edges, accuracy=ELLIPSE_ACCURACY,
            threshold=ELLIPSE_VOTE_THRESHOLD,
            min_size=ellipse_min_size, max_size=ellipse_max_size,
        )
        # Saring kandidat sangat pipih dan kandidat dengan pusat di luar gambar.
        valid = candidates[
            (candidates["a"] >= 6) & (candidates["b"] >= 6)
            & (np.minimum(candidates["a"], candidates["b"])
               / np.maximum(np.maximum(candidates["a"], candidates["b"]), 1e-9)
               >= ELLIPSE_MIN_AXIS_RATIO)
            & (candidates["xc"] >= 0) & (candidates["xc"] < ellipse_w)
            & (candidates["yc"] >= 0) & (candidates["yc"] < ellipse_h)
        ]
        for item in valid[np.argsort(valid["accumulator"])[::-1]]:
            yc, xc, a, b = [int(round(float(item[key]))) for key in ("yc", "xc", "a", "b")]
            orientation = float(item["orientation"])
            rr, cc = ellipse_perimeter(yc, xc, a, b, orientation=orientation)
            inside = (rr >= 0) & (rr < ellipse_h) & (cc >= 0) & (cc < ellipse_w)
            if inside.mean() < 0.90:
                continue
            edge_support = float(np.mean(edge_distance[rr[inside], cc[inside]] <= 1.5))
            if edge_support < ELLIPSE_MIN_EDGE_SUPPORT:
                continue
            # Petakan piksel gambar elips kecil ke ROI kerja, termasuk offset pusat piksel.
            curve_x = (cc[inside] + 0.5) * work_w / ellipse_w - 0.5
            curve_y = (rr[inside] + 0.5) * work_h / ellipse_h - 0.5
            ellipse_curve = (curve_x, curve_y)
            ellipse_record = {
                "votes": int(item["accumulator"]), "edge_support_fraction": edge_support,
                "center_x_small_px": float(item["xc"]), "center_y_small_px": float(item["yc"]),
                "a_small_px": float(item["a"]), "b_small_px": float(item["b"]),
                "orientation_skimage_rad": orientation,
                "center_x_work_px": float((item["xc"] + 0.5) * work_w / ellipse_w - 0.5),
                "center_y_work_px": float((item["yc"] + 0.5) * work_h / ellipse_h - 0.5),
            }
            break
    ellipse_seconds = perf_counter() - t0

    def draw_ellipse(ax):
        if ellipse_curve is not None:
            # Scatter dipakai karena urutan keluaran ellipse_perimeter bukan lintasan terurut.
            ax.scatter(*ellipse_curve, c="yellow", s=5, linewidths=0)
            ax.plot(ellipse_record["center_x_work_px"], ellipse_record["center_y_work_px"], "r+")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(ellipse_edges, cmap="gray")
    axes[0].set_title(f"Tepi input Hough elips ({ellipse_w} × {ellipse_h})")
    axes[1].imshow(rgb)
    draw_ellipse(axes[1])
    axes[1].set(xlim=(0, work_w - 1), ylim=(work_h - 1, 0), title="Kandidat elips pada ROI")
    for ax in axes:
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "04_hough_elips.png", bbox_inches="tight")
    plt.close(fig)
    print(f"Waktu Hough elips: {ellipse_seconds:.3f} detik")
    if ellipse_record is None:
        print("Tidak ada kandidat elips valid. Persempit ROI pada kontur kepala dan sesuaikan parameter.")
    else:
        print(ellipse_record)
        print("a dan b menggunakan piksel gambar kecil; orientasi mengikuti konvensi scikit-image.")

    # 6. PERBANDINGAN HASIL
    summary = [
        {"metode": "Garis", "jumlah_kandidat": len(line_records), "waktu_hough_detik": line_seconds},
        {"metode": "Lingkaran", "jumlah_kandidat": len(circle_records), "waktu_hough_detik": circle_seconds},
        {"metode": "Elips", "jumlah_kandidat": int(ellipse_record is not None), "waktu_hough_detik": ellipse_seconds},
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, item, draw in zip(axes, summary, [draw_lines, draw_circles, draw_ellipse]):
        ax.imshow(rgb)
        draw(ax)
        ax.set(xlim=(0, work_w - 1), ylim=(work_h - 1, 0),
               title=f"{item['metode']} — {item['jumlah_kandidat']} kandidat")
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "05_perbandingan.png", bbox_inches="tight")
    comparison_figure = fig
    for item in summary:
        print(f"{item['metode']:10s} | {item['jumlah_kandidat']} kandidat | {item['waktu_hough_detik']:.3f} detik")
    print("Waktu mengukur tahap Hough dan pemilihan kandidat, tidak termasuk unggahan/praproses/grafik.")
    print("Elips menggunakan resolusi dan jumlah titik berbeda, sehingga waktu bukan benchmark setara.")

    # 7. MENYIMPAN HASIL
    metadata = {
        "image_name": image_path.name,
        "original_shape_hw": [original_h, original_w],
        "roi_original_xyxy": [x1, y1, x2, y2],
        "working_shape_hw": [work_h, work_w],
        "ellipse_shape_hw": [ellipse_h, ellipse_w],
        "coordinate_notes": {
            "lines_circles": "pixels in resized working ROI; x right, y down",
            "ellipse_axes": "pixels in small ellipse input; a,b follow ellipse_perimeter convention",
            "ellipse_center_work": "center mapped to working ROI",
            "votes": "accumulator scores; not accuracy or clinical confidence",
        },
        "parameters": {
            "max_side": MAX_SIDE, "clahe_clip": CLAHE_CLIP,
            "canny_sigma": CANNY_SIGMA, "canny_low": CANNY_LOW, "canny_high": CANNY_HIGH,
            "min_edge_component": MIN_EDGE_COMPONENT,
            "line_peak_ratio": LINE_PEAK_RATIO, "max_lines": MAX_LINES,
            "circle_radius_fraction": CIRCLE_RADIUS_FRACTION,
            "circle_radius_step": CIRCLE_RADIUS_STEP,
            "circle_vote_threshold": CIRCLE_VOTE_THRESHOLD, "max_circles": MAX_CIRCLES,
            "ellipse_max_side": ELLIPSE_MAX_SIDE,
            "ellipse_max_edge_points": ELLIPSE_MAX_EDGE_POINTS,
            "ellipse_accuracy": ELLIPSE_ACCURACY, "ellipse_vote_threshold": ELLIPSE_VOTE_THRESHOLD,
            "ellipse_min_size": ellipse_min_size, "ellipse_max_size": ellipse_max_size,
            "ellipse_min_axis_ratio": ELLIPSE_MIN_AXIS_RATIO,
            "ellipse_min_edge_support": ELLIPSE_MIN_EDGE_SUPPORT, "random_seed": RANDOM_SEED,
        },
        "versions": {"numpy": np.__version__, "scikit_image": skimage.__version__},
        "lines": line_records, "circles": circle_records, "ellipse": ellipse_record,
        "summary": summary,
    }
    (OUTPUT_DIR / "parameter_dan_hasil.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    with (OUTPUT_DIR / "ringkasan.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    archive_path = OUTPUT_DIR.with_suffix(".zip")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUTPUT_DIR.iterdir()):
            if path.is_file():
                archive.write(path, arcname=f"{OUTPUT_DIR.name}/{path.name}")
    print("Hasil tersimpan di:", OUTPUT_DIR.resolve())
    print("ZIP:", archive_path.resolve())

    # 8. TAMPILKAN PERBANDINGAN SETELAH HASIL TERSIMPAN
    if args.tanpa_tampilan:
        plt.close(comparison_figure)
    else:
        print("Tutup jendela perbandingan untuk mengakhiri program.")
        plt.show()
    return metadata


def main():
    args = parse_args()
    try:
        image_path = pilih_gambar(args.gambar)
        proses_gambar(image_path, args)
    except ModuleNotFoundError as exc:
        print(f"Pustaka belum tersedia: {exc.name}", file=sys.stderr)
        print("Instal dengan: python -m pip install numpy scipy scikit-image matplotlib Pillow", file=sys.stderr)
        return 1
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Gagal: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
