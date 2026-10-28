"""Create a deterministic, non-personal document-scan fixture in PNG format."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def create_sample(path: str | Path) -> None:
    rng = np.random.default_rng(20260917)
    height, width = 480, 720
    base = np.full((height, width), 246, dtype=np.uint8)
    background_noise = rng.normal(0, 3.5, (height, width))
    document = np.clip(base.astype(np.float32) + background_noise, 0, 255).astype(np.uint8)

    ink = 35
    cv2.rectangle(document, (24, 22), (width - 24, height - 24), ink, 3)
    cv2.putText(
        document,
        "FORMULIR LAYANAN PUBLIK",
        (58, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        ink,
        2,
        cv2.LINE_AA,
    )
    cv2.line(document, (52, 92), (width - 52, 92), ink, 2)

    labels = ((58, 140, "NAMA"), (58, 205, "NOMOR IDENTITAS"), (58, 270, "ALAMAT"))
    for x, y, label in labels:
        cv2.putText(document, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, ink, 2, cv2.LINE_AA)
        cv2.line(document, (260, y + 4), (650, y + 4), ink, 2)

    cv2.putText(document, "JENIS LAYANAN", (58, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.75, ink, 2, cv2.LINE_AA)
    for x, label in ((300, "INFORMASI"), (480, "PENGADUAN")):
        cv2.rectangle(document, (x, 315), (x + 24, 339), ink, 2)
        cv2.putText(document, label, (x + 34, 337), cv2.FONT_HERSHEY_SIMPLEX, 0.52, ink, 1, cv2.LINE_AA)
    cv2.putText(document, "TANDA TANGAN", (58, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.68, ink, 2, cv2.LINE_AA)
    cv2.line(document, (260, 424), (650, 424), ink, 2)

    # Simulate a scan: dark speckles and small gaps in strokes.
    for _ in range(260):
        x = int(rng.integers(30, width - 30))
        y = int(rng.integers(30, height - 30))
        radius = int(rng.choice((1, 1, 1, 2)))
        cv2.circle(document, (x, y), radius, int(rng.integers(25, 100)), -1)
    for x, y in ((355, 144), (516, 209), (390, 274), (568, 424)):
        cv2.rectangle(document, (x, y), (x + 9, y + 4), 246, -1)

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), document):
        raise IOError(f"Cannot write sample image: {destination}")
    print(f"Saved sample PNG: {destination}")


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "data" / "input" / "document_scan.png"
    create_sample(target)
