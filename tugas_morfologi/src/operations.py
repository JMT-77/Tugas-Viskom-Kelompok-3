"""Morphological image processing for a document-cleaning use case.

The input is a dark-ink-on-light-background document scan. The image is
binarized so that foreground ink is white (255) and the background is black.
All eight listed morphology operations are computed in one pipeline and can
be rendered into one labeled PNG montage.
"""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import TypedDict

import cv2
import numpy as np


OperationImage = np.ndarray


class ProcessReport(TypedDict):
    input: np.ndarray
    results: dict[str, np.ndarray]
    montage: np.ndarray


def load_grayscale(path: str | Path) -> np.ndarray:
    """Load a PNG (or another OpenCV-supported image) as one grayscale plane."""
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Cannot read image: {path}")
    if image.ndim != 2 or image.size == 0:
        raise ValueError(f"Input must be a non-empty grayscale image: {path}")
    return image


def binarize_document(gray: np.ndarray) -> np.ndarray:
    """Convert dark document ink to white foreground on a black background."""
    if gray.ndim != 2:
        raise ValueError("gray must be a single-channel image")
    _threshold, binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return binary


def morphology_kernel(size: int = 3) -> np.ndarray:
    """Return a cross-shaped structuring element for document strokes."""
    if size < 3 or size % 2 == 0:
        raise ValueError("kernel size must be an odd integer >= 3")
    return cv2.getStructuringElement(cv2.MORPH_CROSS, (size, size))


def dilation(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Thicken foreground strokes and bridge small gaps."""
    return cv2.dilate(binary, kernel, iterations=1)


def erosion(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Thin foreground strokes and remove structures smaller than the kernel."""
    return cv2.erode(binary, kernel, iterations=1)


def opening(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Erosion followed by dilation; useful for removing small foreground noise."""
    return cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)


def closing(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Dilation followed by erosion; useful for closing small gaps and holes."""
    return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)


def top_hat(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Extract small bright foreground details removed by opening.

    With this pipeline, foreground ink is represented by white pixels. Thus
    top-hat highlights small white components that are not preserved by the
    opening operation.
    """
    return cv2.morphologyEx(binary, cv2.MORPH_TOPHAT, kernel)


def _endpoint_kernels() -> list[np.ndarray]:
    """Build eight hit-or-miss kernels for one-pixel line endpoints."""
    kernels: list[np.ndarray] = []
    for row in range(3):
        for column in range(3):
            if (row, column) == (1, 1):
                continue
            pattern = np.full((3, 3), -1, dtype=np.int8)
            pattern[1, 1] = 1
            pattern[row, column] = 1
            kernels.append(pattern)
    return kernels


def hit_or_miss(binary: np.ndarray) -> np.ndarray:
    """Mark endpoints in a thinned binary image using hit-or-miss patterns."""
    source = (binary > 0).astype(np.uint8)
    result = np.zeros_like(source)
    for pattern in _endpoint_kernels():
        matches = cv2.morphologyEx(source, cv2.MORPH_HITMISS, pattern)
        result = cv2.bitwise_or(result, matches)
    return result * 255


def skeletonization(binary: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Compute a morphological skeleton by iterative erosion and opening."""
    current = binary.copy()
    skeleton = np.zeros_like(binary)
    while cv2.countNonZero(current) > 0:
        opened = cv2.morphologyEx(current, cv2.MORPH_OPEN, kernel)
        residue = cv2.subtract(current, opened)
        skeleton = cv2.bitwise_or(skeleton, residue)
        current = cv2.erode(current, kernel, iterations=1)
    return skeleton


def _zhang_suen_delete_mask(image: np.ndarray, phase: int) -> np.ndarray:
    """Return pixels deleted by one Zhang-Suen thinning sub-iteration."""
    padded = np.pad(image, 1, mode="constant", constant_values=0)
    p2 = padded[:-2, 1:-1]  # north
    p3 = padded[:-2, 2:]  # north-east
    p4 = padded[1:-1, 2:]  # east
    p5 = padded[2:, 2:]  # south-east
    p6 = padded[2:, 1:-1]  # south
    p7 = padded[2:, :-2]  # south-west
    p8 = padded[1:-1, :-2]  # west
    p9 = padded[:-2, :-2]  # north-west
    neighbors = (p2, p3, p4, p5, p6, p7, p8, p9)

    neighbor_count = sum(neighbors)
    transitions = sum(
        ((left == 0) & (right == 1)).astype(np.uint8)
        for left, right in zip(neighbors, neighbors[1:] + neighbors[:1])
    )
    foreground = image == 1
    conditions = foreground & (neighbor_count >= 2) & (neighbor_count <= 6)
    conditions &= transitions == 1

    if phase == 1:
        conditions &= (p2 * p4 * p6) == 0
        conditions &= (p4 * p6 * p8) == 0
    else:
        conditions &= (p2 * p4 * p8) == 0
        conditions &= (p2 * p6 * p8) == 0
    return conditions


def thinning(binary: np.ndarray, max_iterations: int = 1000) -> np.ndarray:
    """Thin foreground strokes using the Zhang-Suen algorithm."""
    image = (binary > 0).astype(np.uint8)
    for _iteration in range(max_iterations):
        changed = False
        for phase in (1, 2):
            delete = _zhang_suen_delete_mask(image, phase)
            if np.any(delete):
                image[delete] = 0
                changed = True
        if not changed:
            return image * 255
    raise RuntimeError("Zhang-Suen thinning did not converge within the iteration limit")


def run_all(gray: np.ndarray, kernel_size: int = 3) -> Mapping[str, np.ndarray]:
    """Run the complete morphology list in one call.

    Hit-or-miss is applied to the thinned image so that its endpoint pattern
    has a meaningful one-pixel structure rather than a thick document stroke.
    """
    binary = binarize_document(gray)
    kernel = morphology_kernel(kernel_size)
    skeleton = skeletonization(binary, kernel)
    thin = thinning(binary)
    return {
        "Original grayscale": gray,
        "Binary input": binary,
        "Dilation": dilation(binary, kernel),
        "Erosion": erosion(binary, kernel),
        "Opening": opening(binary, kernel),
        "Closing": closing(binary, kernel),
        "Top-hat": top_hat(binary, kernel),
        "Hit-or-miss endpoints": hit_or_miss(thin),
        "Skeletonization": skeleton,
        "Thinning": thin,
    }


def _cell(image: np.ndarray, label: str, width: int, height: int) -> np.ndarray:
    """Resize an operation result and place a readable label above it."""
    if image.ndim == 2:
        display = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        display = image.copy()
    display = cv2.resize(display, (width, height), interpolation=cv2.INTER_NEAREST)
    label_bar = np.full((34, width, 3), 245, dtype=np.uint8)
    cv2.putText(
        label_bar,
        label,
        (8, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (25, 25, 25),
        1,
        cv2.LINE_AA,
    )
    return np.vstack((label_bar, display))


def make_montage(
    results: Mapping[str, np.ndarray],
    columns: int = 3,
    cell_width: int = 300,
    cell_height: int = 190,
) -> np.ndarray:
    """Combine every result into one labeled PNG-ready image."""
    if columns < 1:
        raise ValueError("columns must be positive")
    cells = [_cell(image, label, cell_width, cell_height) for label, image in results.items()]
    rows: list[np.ndarray] = []
    blank = np.full_like(cells[0], 230)
    for start in range(0, len(cells), columns):
        row = cells[start : start + columns]
        row.extend([blank] * (columns - len(row)))
        rows.append(np.hstack(row))
    grid = np.vstack(rows)
    title = np.full((48, grid.shape[1], 3), (35, 75, 115), dtype=np.uint8)
    cv2.putText(
        title,
        "MORFOLOGI CITRA - PEMBERSIHAN DOKUMEN UNTUK OCR",
        (16, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return np.vstack((title, grid))


def process_to_montage(
    input_path: str | Path,
    output_path: str | Path,
    kernel_size: int = 3,
) -> ProcessReport:
    """Load, run all operations, and write the single composite PNG."""
    gray = load_grayscale(input_path)
    results = dict(run_all(gray, kernel_size=kernel_size))
    montage = make_montage(results)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), montage):
        raise IOError(f"Cannot write output image: {destination}")
    return {"input": gray, "results": results, "montage": montage}
