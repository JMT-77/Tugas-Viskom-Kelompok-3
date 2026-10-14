"""Run every current Tugas 2 operation and save one composite PNG."""
from __future__ import annotations

from pathlib import Path

from manual_operations import Image, brightness, contrast, denoise, edge, mirror, read, rotate, write


_DIGITS = {
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
}


def _white_canvas(width: int, height: int) -> Image:
    return Image(width, height, [[(255, 255, 255)] * width for _ in range(height)])


def _resize_nearest(image: Image, width: int, height: int) -> Image:
    pixels = []
    for y in range(height):
        source_y = min(image.height - 1, int(y * image.height / height))
        row = []
        for x in range(width):
            source_x = min(image.width - 1, int(x * image.width / width))
            row.append(image.pixels[source_y][source_x])
        pixels.append(row)
    return Image(width, height, pixels)


def _resize_to_fit(image: Image, width: int, height: int) -> Image:
    scale = min(width / image.width, height / image.height)
    return _resize_nearest(image, max(1, round(image.width * scale)), max(1, round(image.height * scale)))


def _paste(destination: Image, source: Image, left: int, top: int) -> None:
    for y, row in enumerate(source.pixels):
        for x, pixel in enumerate(row):
            destination.pixels[top + y][left + x] = pixel


def _draw_marker(image: Image, marker: str) -> None:
    scale = 2
    for char_index, character in enumerate(marker):
        pattern = _DIGITS[character]
        x_offset = 8 + char_index * 6 * scale
        for y, row in enumerate(pattern):
            for x, value in enumerate(row):
                if value == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            px = x_offset + x * scale + dx
                            py = 6 + y * scale + dy
                            if px < image.width and py < image.height:
                                image.pixels[py][px] = (25, 25, 25)


def _panel(image: Image, marker: str, width: int = 280, height: int = 180) -> Image:
    panel = _white_canvas(width, height + 26)
    fitted = _resize_to_fit(image, width - 10, height - 10)
    _paste(panel, fitted, (width - fitted.width) // 2, 26 + (height - fitted.height) // 2)
    _draw_marker(panel, marker)
    return panel


def make_montage(images: list[tuple[str, Image]], columns: int = 3) -> Image:
    if not images:
        raise ValueError("At least one image is required")
    panels = [_panel(image, marker) for marker, image in images]
    rows = []
    for start in range(0, len(panels), columns):
        row_panels = panels[start : start + columns]
        while len(row_panels) < columns:
            row_panels.append(_white_canvas(panels[0].width, panels[0].height))
        for y in range(panels[0].height):
            rows.append([pixel for panel in row_panels for pixel in panel.pixels[y]])
    return Image(columns * panels[0].width, len(rows), rows)


def run_all(input_dir: str | Path, output_path: str | Path) -> None:
    input_root = Path(input_dir)
    apple = read(input_root / "internet_apple.png")
    peppers = read(input_root / "internet_peppers.png")
    landscape = read(input_root / "internet_landscape.png")
    brightness_contrast_input = read(input_root / "brightness_contrast.jpeg")

    images = [
        ("P01", apple),
        ("P02", peppers),
        ("P03", landscape),
        ("P04", brightness_contrast_input),
        ("P05", mirror(apple, "horizontal")),
        ("P06", rotate(peppers, 90)),
        ("P07", edge(landscape, 50, 150, 5)),
        ("P08", denoise(apple, "gaussian", 5)),
        ("P09", denoise(apple, "median", 5)),
        ("P10", denoise(apple, "bilateral", 5)),
        ("P11", brightness(brightness_contrast_input, 40)),
        ("P12", contrast(brightness_contrast_input, 1.5, 127)),
    ]
    write(output_path, make_montage(images))
    print(f"Processed 8 Tugas 2 result variants from {input_root}")
    print(f"Saved composite PNG: {output_path}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    run_all(root / "data" / "input", root / "data" / "output" / "all_results.png")
