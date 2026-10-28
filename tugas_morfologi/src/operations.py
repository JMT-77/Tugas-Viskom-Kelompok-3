# """Morphological image processing for a document-cleaning use case.

# The input is a dark-ink-on-light-background document scan. The image is
# binarized so that foreground ink is white (255) and the background is black.
# All eight listed morphology operations are computed in one pipeline and can
# be rendered into one labeled PNG montage.
# """
# from __future__ import annotations

# from collections.abc import Mapping
# from pathlib import Path
# from typing import TypedDict

# import cv2
# import numpy as np


# OperationImage = np.ndarray


# class ProcessReport(TypedDict):
#     input: np.ndarray
#     results: dict[str, np.ndarray]
#     montage: np.ndarray


# def load_grayscale(path: str | Path) -> np.ndarray:
#     """Load a PNG (or another OpenCV-supported image) as one grayscale plane."""
#     image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
#     if image is None:
#         raise ValueError(f"Cannot read image: {path}")
#     if image.ndim != 2 or image.size == 0:
#         raise ValueError(f"Input must be a non-empty grayscale image: {path}")
#     return image


# def binarize_document(gray: np.ndarray) -> np.ndarray:
#     """Convert dark document ink to white foreground on a black background."""
#     if gray.ndim != 2:
#         raise ValueError("gray must be a single-channel image")
#     _threshold, binary = cv2.threshold(
#         gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
#     )
#     return binary


# def morphology_kernel(size: int = 3) -> np.ndarray:
#     """Return a cross-shaped structuring element for document strokes."""
#     if size < 3 or size % 2 == 0:
#         raise ValueError("kernel size must be an odd integer >= 3")
#     return cv2.getStructuringElement(cv2.MORPH_CROSS, (size, size))


# def dilation(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
#     """Thicken foreground strokes and bridge small gaps."""
#     return cv2.dilate(binary, kernel, iterations=1)


# def erosion(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
#     """Thin foreground strokes and remove structures smaller than the kernel."""
#     return cv2.erode(binary, kernel, iterations=1)


# def opening(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
#     """Erosion followed by dilation; useful for removing small foreground noise."""
#     return cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)


# def closing(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
#     """Dilation followed by erosion; useful for closing small gaps and holes."""
#     return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)


# def top_hat(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
#     """Extract small bright foreground details removed by opening.

#     With this pipeline, foreground ink is represented by white pixels. Thus
#     top-hat highlights small white components that are not preserved by the
#     opening operation.
#     """
#     return cv2.morphologyEx(binary, cv2.MORPH_TOPHAT, kernel)


# def _endpoint_kernels() -> list[np.ndarray]:
#     """Build eight hit-or-miss kernels for one-pixel line endpoints."""
#     kernels: list[np.ndarray] = []
#     for row in range(3):
#         for column in range(3):
#             if (row, column) == (1, 1):
#                 continue
#             pattern = np.full((3, 3), -1, dtype=np.int8)
#             pattern[1, 1] = 1
#             pattern[row, column] = 1
#             kernels.append(pattern)
#     return kernels


# def hit_or_miss(binary: np.ndarray) -> np.ndarray:
#     """Mark endpoints in a thinned binary image using hit-or-miss patterns."""
#     source = (binary > 0).astype(np.uint8)
#     result = np.zeros_like(source)
#     for pattern in _endpoint_kernels():
#         matches = cv2.morphologyEx(source, cv2.MORPH_HITMISS, pattern)
#         result = cv2.bitwise_or(result, matches)
#     return result * 255


# def skeletonization(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
#     """Compute a morphological skeleton by iterative erosion and opening."""
#     current = binary.copy()
#     skeleton = np.zeros_like(binary)
#     while cv2.countNonZero(current) > 0:
#         opened = cv2.morphologyEx(current, cv2.MORPH_OPEN, kernel)
#         residue = cv2.subtract(current, opened)
#         skeleton = cv2.bitwise_or(skeleton, residue)
#         current = cv2.erode(current, kernel, iterations=1)
#     return skeleton


# def _zhang_suen_delete_mask(image: np.ndarray, phase: int) -> np.ndarray:
#     """Return pixels deleted by one Zhang-Suen thinning sub-iteration."""
#     padded = np.pad(image, 1, mode="constant", constant_values=0)
#     p2 = padded[:-2, 1:-1]  # north
#     p3 = padded[:-2, 2:]  # north-east
#     p4 = padded[1:-1, 2:]  # east
#     p5 = padded[2:, 2:]  # south-east
#     p6 = padded[2:, 1:-1]  # south
#     p7 = padded[2:, :-2]  # south-west
#     p8 = padded[1:-1, :-2]  # west
#     p9 = padded[:-2, :-2]  # north-west
#     neighbors = (p2, p3, p4, p5, p6, p7, p8, p9)

#     neighbor_count = sum(neighbors)
#     transitions = sum(
#         ((left == 0) & (right == 1)).astype(np.uint8)
#         for left, right in zip(neighbors, neighbors[1:] + neighbors[:1])
#     )
#     foreground = image == 1
#     conditions = foreground & (neighbor_count >= 2) & (neighbor_count <= 6)
#     conditions &= transitions == 1

#     if phase == 1:
#         conditions &= (p2 * p4 * p6) == 0
#         conditions &= (p4 * p6 * p8) == 0
#     else:
#         conditions &= (p2 * p4 * p8) == 0
#         conditions &= (p2 * p6 * p8) == 0
#     return conditions


# def thinning(binary: np.ndarray, max_iterations: int = 1000) -> np.ndarray:
#     """Thin foreground strokes using the Zhang-Suen algorithm."""
#     image = (binary > 0).astype(np.uint8)
#     for _iteration in range(max_iterations):
#         changed = False
#         for phase in (1, 2):
#             delete = _zhang_suen_delete_mask(image, phase)
#             if np.any(delete):
#                 image[delete] = 0
#                 changed = True
#         if not changed:
#             return image * 255
#     raise RuntimeError("Zhang-Suen thinning did not converge within the iteration limit")


# def run_all(gray: np.ndarray, kernel_size: int = 3) -> Mapping[str, np.ndarray]:
#     """Run the complete morphology list in one call.

#     Hit-or-miss is applied to the thinned image so that its endpoint pattern
#     has a meaningful one-pixel structure rather than a thick document stroke.
#     """
#     binary = binarize_document(gray)
#     kernel = morphology_kernel(kernel_size)
#     skeleton = skeletonization(binary, kernel)
#     thin = thinning(binary)
#     return {
#         "Original grayscale": gray,
#         "Binary input": binary,
#         "Dilation": dilation(binary, kernel),
#         "Erosion": erosion(binary, kernel),
#         "Opening": opening(binary, kernel),
#         "Closing": closing(binary, kernel),
#         "Top-hat": top_hat(binary, kernel),
#         "Hit-or-miss endpoints": hit_or_miss(thin),
#         "Skeletonization": skeleton,
#         "Thinning": thin,
#     }


# def _cell(image: np.ndarray, label: str, width: int, height: int) -> np.ndarray:
#     """Resize an operation result and place a readable label above it."""
#     if image.ndim == 2:
#         display = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
#     else:
#         display = image.copy()
#     display = cv2.resize(display, (width, height), interpolation=cv2.INTER_NEAREST)
#     label_bar = np.full((34, width, 3), 245, dtype=np.uint8)
#     cv2.putText(
#         label_bar,
#         label,
#         (8, 23),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.48,
#         (25, 25, 25),
#         1,
#         cv2.LINE_AA,
#     )
#     return np.vstack((label_bar, display))


# def make_montage(
#     results: Mapping[str, np.ndarray],
#     columns: int = 3,
#     cell_width: int = 300,
#     cell_height: int = 190,
# ) -> np.ndarray:
#     """Combine every result into one labeled PNG-ready image."""
#     if columns < 1:
#         raise ValueError("columns must be positive")
#     cells = [_cell(image, label, cell_width, cell_height) for label, image in results.items()]
#     rows: list[np.ndarray] = []
#     blank = np.full_like(cells[0], 230)
#     for start in range(0, len(cells), columns):
#         row = cells[start : start + columns]
#         row.extend([blank] * (columns - len(row)))
#         rows.append(np.hstack(row))
#     grid = np.vstack(rows)
#     title = np.full((48, grid.shape[1], 3), (35, 75, 115), dtype=np.uint8)
#     cv2.putText(
#         title,
#         "MORFOLOGI CITRA - PEMBERSIHAN DOKUMEN UNTUK OCR",
#         (16, 32),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.8,
#         (255, 255, 255),
#         2,
#         cv2.LINE_AA,
#     )
#     return np.vstack((title, grid))


# def process_to_montage(
#     input_path: str | Path,
#     output_path: str | Path,
#     kernel_size: int = 3,
# ) -> ProcessReport:
#     """Load, run all operations, and write the single composite PNG."""
#     gray = load_grayscale(input_path)
#     results = dict(run_all(gray, kernel_size=kernel_size))
#     montage = make_montage(results)
#     destination = Path(output_path)
#     destination.parent.mkdir(parents=True, exist_ok=True)
#     if not cv2.imwrite(str(destination), montage):
#         raise IOError(f"Cannot write output image: {destination}")
#     return {"input": gray, "results": results, "montage": montage}

"""Morfologi citra: satu citra uji untuk setiap operasi."""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

SHAPES = {"cross": cv2.MORPH_CROSS, "ellipse": cv2.MORPH_ELLIPSE, "rect": cv2.MORPH_RECT}


# ---------------------------------------------------------------- dasar
def make_kernel(shape: str = "cross", size: int = 3) -> np.ndarray:
    if size < 3 or size % 2 == 0:
        raise ValueError("ukuran kernel harus ganjil dan >= 3")
    return cv2.getStructuringElement(SHAPES[shape], (size, size))


def load_image(path, crop=(0, 0, 0, 0), max_width=None) -> np.ndarray:
    """Baca BGR. crop = (atas, bawah, kiri, kanan) dalam fraksi 0-1."""
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Tidak bisa membaca citra: {path}")
    h, w = img.shape[:2]
    t, b, l, r = crop
    img = img[int(h * t): h - int(h * b), int(w * l): w - int(w * r)]
    if max_width and img.shape[1] > max_width:
        s = max_width / img.shape[1]
        img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    return img


def count_components(binary: np.ndarray, min_area: int = 1) -> int:
    n, _, stats, _ = cv2.connectedComponentsWithStats(binary)
    return sum(1 for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= min_area)


def remove_small(binary: np.ndarray, min_area: int) -> np.ndarray:
    n, labels, stats, _ = cv2.connectedComponentsWithStats(binary)
    keep = np.zeros(n, dtype=bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_area
    return (keep[labels] * 255).astype(np.uint8)


# ---------------------------------------------------------------- praproses
def _gray(bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


def prep_none(bgr):  # tanpa binerisasi (opening, top-hat)
    return _gray(bgr)


def prep_otsu_inv(bgr):  # objek gelap pada latar terang -> objek putih
    return cv2.threshold(_gray(bgr), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]


def prep_otsu(bgr):  # objek terang pada latar gelap -> objek putih
    return cv2.threshold(_gray(bgr), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def prep_otsu_clean(bgr):  # Otsu normal + pembersihan bintik kecil
    k = make_kernel("ellipse", 3)
    b = prep_otsu(bgr)
    return cv2.morphologyEx(cv2.morphologyEx(b, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)


def prep_cracks(bgr):  # retakan: black-hat -> threshold -> buang komponen kecil
    g = cv2.GaussianBlur(_gray(bgr), (5, 5), 0)
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, make_kernel("ellipse", 15))
    return remove_small(cv2.threshold(bh, 35, 255, cv2.THRESH_BINARY)[1], 60)


def prep_water(bgr):  # sungai: segmentasi warna biru
    b, g, r = (c.astype(np.int16) for c in cv2.split(bgr))
    mask = (((b - g) > 20) & (b > r)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, make_kernel("ellipse", 9))
    return remove_small(mask, int(mask.size * 0.0005))


# ---------------------------------------------------------------- operasi
def dilation(img, k, iterations=1):
    return cv2.dilate(img, k, iterations=iterations)


def erosion(img, k, iterations=1):
    return cv2.erode(img, k, iterations=iterations)


def opening(img, k):
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, k)


def closing(img, k):
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, k)


def top_hat(gray, k):
    """Top-hat pada grayscale; kontras diregangkan (persentil 99,9) agar terlihat."""
    th = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, k).astype(np.float32)
    top = max(float(np.percentile(th, 99.9)), 1.0)
    return np.clip(th / top * 255, 0, 255).astype(np.uint8)


def corner_kernels() -> list[np.ndarray]:
    """Empat pola sudut-cembung (1=objek, -1=latar, 0=abaikan)."""
    base = np.array([[0, -1, 0], [-1, 1, 1], [0, 1, 1]], dtype=np.int8)
    return [np.rot90(base, i).copy() for i in range(4)]


def hit_or_miss(binary):
    src = (binary > 0).astype(np.uint8)
    out = np.zeros_like(src)
    for pattern in corner_kernels():
        out |= cv2.morphologyEx(src, cv2.MORPH_HITMISS, pattern)
    return out * 255


def skeletonization(binary, k):
    current, skeleton = binary.copy(), np.zeros_like(binary)
    while cv2.countNonZero(current) > 0:
        opened = cv2.morphologyEx(current, cv2.MORPH_OPEN, k)
        skeleton = cv2.bitwise_or(skeleton, cv2.subtract(current, opened))
        current = cv2.erode(current, k)
    return skeleton


def _zhang_suen_mask(image, phase):
    p = np.pad(image, 1)
    p2, p3, p4, p5 = p[:-2, 1:-1], p[:-2, 2:], p[1:-1, 2:], p[2:, 2:]
    p6, p7, p8, p9 = p[2:, 1:-1], p[2:, :-2], p[1:-1, :-2], p[:-2, :-2]
    nb = (p2, p3, p4, p5, p6, p7, p8, p9)
    count = sum(nb)
    trans = sum(((a == 0) & (b == 1)).astype(np.uint8) for a, b in zip(nb, nb[1:] + nb[:1]))
    cond = (image == 1) & (count >= 2) & (count <= 6) & (trans == 1)
    if phase == 1:
        cond &= ((p2 * p4 * p6) == 0) & ((p4 * p6 * p8) == 0)
    else:
        cond &= ((p2 * p4 * p8) == 0) & ((p2 * p6 * p8) == 0)
    return cond


def thinning(binary, max_iterations=1000):
    image = (binary > 0).astype(np.uint8)
    for _ in range(max_iterations):
        changed = False
        for phase in (1, 2):
            delete = _zhang_suen_mask(image, phase)
            if delete.any():
                image[delete] = 0
                changed = True
        if not changed:
            return image * 255
    raise RuntimeError("Thinning tidak konvergen")


# ---------------------------------------------------------------- konfigurasi
@dataclass(frozen=True)
class Case:
    name: str
    file: str
    prep: Callable
    run: Callable
    shape: str = "cross"
    size: int = 3
    iterations: int = 1
    crop: tuple = (0, 0, 0, 0)   # (atas, bawah, kiri, kanan)
    max_width: int | None = None
    variants: tuple = ()

    @property
    def kernel(self) -> np.ndarray:
        return make_kernel(self.shape, self.size)


def _pct(img) -> str:
    return f"{100 * np.count_nonzero(img) / img.size:.1f}%"


def _overlay(base, mask):
    """Hasil 1-piksel ditebalkan (hanya untuk tampilan) merah di atas latar redup."""
    out = cv2.cvtColor((base // 3).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    out[cv2.dilate(mask, np.ones((3, 3), np.uint8)) > 0] = (0, 0, 255)
    return out


def _run_dilation(img, c):
    out = dilation(img, c.kernel, c.iterations)
    return out, f"foreground {_pct(img)} -> {_pct(out)}"


def _run_erosion(img, c):
    out = erosion(img, c.kernel, c.iterations)
    return out, f"gugus {count_components(img, 20)} -> {count_components(out, 20)}"


def _run_opening(img, c):
    out = opening(img, c.kernel)
    w0, w1 = 100 * (img == 255).mean(), 100 * (out == 255).mean()
    b0, b1 = 100 * (img == 0).mean(), 100 * (out == 0).mean()
    return out, f"putih murni {w0:.1f}->{w1:.1f}%, hitam {b0:.1f}->{b1:.1f}%"


def _run_closing(img, c):
    out = closing(img, c.kernel)
    return out, f"komponen retakan {count_components(img)} -> {count_components(out)}"


def _run_tophat(img, c):
    return top_hat(img, c.kernel), "detail terang kecil"


def _run_hit_or_miss(img, c):
    hits = hit_or_miss(img)
    n, _, _, centers = cv2.connectedComponentsWithStats(cv2.dilate(hits, make_kernel("rect", 5)))
    out = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for x, y in centers[1:]:
        cv2.circle(out, (int(x), int(y)), max(6, img.shape[1] // 60), (0, 0, 255), 2)
    return out, f"{n - 1} sudut terdeteksi"


def _run_skeleton(img, c):
    return _overlay(img, skeletonization(img, c.kernel)), "kerangka (merah)"


def _run_thinning(img, c):
    return _overlay(img, thinning(img)), "garis 1 piksel (merah)"


CASES = [
    Case("Dilation", "dilasi.png", prep_otsu_inv, _run_dilation, "cross", 3,
         variants=((5, 1), (7, 1), (3, 3))),
    Case("Erosion", "erosi.png", prep_otsu, _run_erosion, "ellipse", 5, iterations=3,
         crop=(0, 0.10, 0, 0), variants=((3, 1), (5, 1), (5, 2))),
    Case("Opening", "opening.png", prep_none, _run_opening, "ellipse", 3),
    Case("Closing", "closing.png", prep_cracks, _run_closing, "ellipse", 9,
         variants=((3, 1), (5, 1), (15, 1))),
    Case("Top-hat", "tophat.png", prep_none, _run_tophat, "ellipse", 5,
         variants=((3, 1), (7, 1), (11, 1))),
    # Papan catur baru: sesuaikan crop (atas, bawah, kiri, kanan) agar hanya area 8x8
    Case("Hit-or-miss", "hit_or_miss.png", prep_otsu_clean, _run_hit_or_miss),
    Case("Skeletonization", "skeletonization.png", prep_water, _run_skeleton, "cross", 3, max_width=1000),
    Case("Thinning", "thinning.png", prep_otsu_inv, _run_thinning),
]


# ---------------------------------------------------------------- pipeline & montase
def process_case(case: Case, input_dir) -> dict:
    original = load_image(Path(input_dir) / case.file, case.crop, case.max_width)
    prepared = case.prep(original)
    result, note = case.run(prepared, case)
    variants = []
    for size, iters in case.variants:
        v = replace(case, size=size, iterations=iters)
        img, v_note = v.run(prepared, v)
        variants.append({"label": f"{case.shape} {size}x{size}, iter {iters}", "result": img, "note": v_note})
    params = f"{case.shape} {case.size}x{case.size}, iter {case.iterations}" if case.variants else ""
    return {"name": case.name, "file": case.file, "original": original, "prep": prepared,
            "result": result, "note": note, "params": params, "variants": variants}

def run_all(input_dir, cases=CASES) -> list[dict]:
    return [process_case(c, input_dir) for c in cases]


def _fit(img, w, h):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    s = min(w / img.shape[1], h / img.shape[0])
    nw, nh = max(1, int(img.shape[1] * s)), max(1, int(img.shape[0] * s))
    canvas = np.full((h, w, 3), 200, np.uint8)
    y, x = (h - nh) // 2, (w - nw) // 2
    canvas[y:y + nh, x:x + nw] = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    return canvas


def _cell(img, label, w, h, note=None):
    """Sel berlabel. Jika note diberikan (boleh kosong), label bar dua baris."""
    bar = np.full((30 if note is None else 48, w, 3), 245, np.uint8)
    cv2.putText(bar, label, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (25, 25, 25), 1, cv2.LINE_AA)
    if note:
        cv2.putText(bar, note, (6, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (90, 90, 90), 1, cv2.LINE_AA)
    return np.vstack((bar, _fit(img, w, h)))

def make_montage(results, cell_w=380, cell_h=260) -> np.ndarray:
    rows = []
    for i, r in enumerate(results, 1):
        rows.append(np.hstack((
            _cell(r["original"], f"{i}. {r['name']} - asli", cell_w, cell_h),
            _cell(r["prep"], "praproses", cell_w, cell_h),
            _cell(r["result"], f"hasil: {r['note']}", cell_w, cell_h),
        )))
    grid = np.vstack(rows)
    title = np.full((48, grid.shape[1], 3), (35, 75, 115), np.uint8)
    cv2.putText(title, "MORFOLOGI CITRA - 8 OPERASI PADA 8 CITRA UJI", (16, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    return np.vstack((title, grid))


def process_to_montage(input_dir, output_path) -> list[dict]:
    results = run_all(input_dir)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(out), make_montage(results)):
        raise IOError(f"Gagal menulis: {out}")
    return results

def make_operation_figure(r: dict, columns=3, cell_w=440, cell_h=300) -> np.ndarray:
    """Satu gambar untuk satu operasi: asli, praproses, hasil, lalu variasi kernel."""
    hasil = f"hasil ({r['params']})" if r["params"] else "hasil"
    cells = [
        _cell(r["original"], "asli", cell_w, cell_h, ""),
        _cell(r["prep"], "praproses", cell_w, cell_h, ""),
        _cell(r["result"], hasil, cell_w, cell_h, r["note"]),
    ]
    cells += [_cell(v["result"], f"variasi: {v['label']}", cell_w, cell_h, v["note"])
              for v in r["variants"]]
    blank = np.full_like(cells[0], 230)
    while len(cells) % columns:
        cells.append(blank)
    grid = np.vstack([np.hstack(cells[i:i + columns]) for i in range(0, len(cells), columns)])
    title = np.full((48, grid.shape[1], 3), (35, 75, 115), np.uint8)
    cv2.putText(title, f"{r['name'].upper()}  ({r['file']})", (16, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    return np.vstack((title, grid))


def save_per_operation(results, out_dir) -> list[Path]:
    """Simpan satu PNG per operasi, mis. 01_dilation.png, 02_erosion.png, ..."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, r in enumerate(results, 1):
        path = out_dir / f"{i:02d}_{r['name'].lower().replace('-', '_')}.png"
        if not cv2.imwrite(str(path), make_operation_figure(r)):
            raise IOError(f"Gagal menulis: {path}")
        paths.append(path)
    return paths