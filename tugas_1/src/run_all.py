"""Run every Tugas 1 operation and create one pure-Python PNG montage."""
from __future__ import annotations

from pathlib import Path

from image_io import Image, read_image, write_image
from operations import color_depth, resize_nearest, rotate


_DIGITS = {
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
}


def _white_canvas(width: int, height: int) -> Image:
    return Image(width, height, [[(255, 255, 255)] * width for _ in range(height)])


def _resize_to_fit(image: Image, width: int, height: int) -> Image:
    scale = min(width / image.width, height / image.height)
    target_width = max(1, round(image.width * scale))
    target_height = max(1, round(image.height * scale))
    from operations import resize_nearest

    return resize_nearest(image, target_width, target_height)


def _paste(destination: Image, source: Image, left: int, top: int) -> None:
    for y, row in enumerate(source.pixels):
        for x, pixel in enumerate(row):
            destination.pixels[top + y][left + x] = pixel


def _draw_marker(image: Image, marker: str) -> None:
    """Draw a compact P1/P2/P3/P4 marker without an external font library."""
    scale = 3
    x0, y0 = 8, 7
    for char_index, character in enumerate(marker):
        pattern = _DIGITS[character]
        x_offset = x0 + char_index * 6 * scale
        for y, row in enumerate(pattern):
            for x, value in enumerate(row):
                if value == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            px = x_offset + x * scale + dx
                            py = y0 + y * scale + dy
                            if px < image.width and py < image.height:
                                image.pixels[py][px] = (25, 25, 25)


def _panel(image: Image, marker: str, width: int = 240, height: int = 180) -> Image:
    panel = _white_canvas(width, height + 30)
    fitted = _resize_to_fit(image, width - 12, height - 12)
    left = (width - fitted.width) // 2
    top = 30 + (height - fitted.height) // 2
    _paste(panel, fitted, left, top)
    _draw_marker(panel, marker)
    return panel


def make_montage(images: list[tuple[str, Image]], columns: int = 2) -> Image:
    if not images:
        raise ValueError("At least one image is required")
    panels = [_panel(image, marker) for marker, image in images]
    rows = []
    row_width = columns * panels[0].width
    for start in range(0, len(panels), columns):
        row_panels = panels[start : start + columns]
        while len(row_panels) < columns:
            row_panels.append(_white_canvas(panels[0].width, panels[0].height))
        row = []
        for y in range(panels[0].height):
            row.append([pixel for panel in row_panels for pixel in panel.pixels[y]])
        rows.extend(row)
    return Image(row_width, len(rows), rows)


def run_all(input_path: str | Path, output_path: str | Path) -> None:
    source = read_image(input_path)
    color_result = color_depth(source, bits=4)
    resize_result = resize_nearest(source, width=640, height=480)
    rotate_result = rotate(source, angle=90)

    text_output = Path(output_path).parent / "text"
    write_image(color_result, text_output / "color_depth.txt")
    write_image(resize_result, text_output / "resolusi.txt")
    write_image(rotate_result, text_output / "rotasi.txt")

    montage = make_montage(
        [
            ("P1", source),
            ("P2", color_result),
            ("P3", resize_result),
            ("P4", rotate_result),
        ]
    )
    write_image(montage, output_path)
    print(f"Processed 3 operations from {input_path}")
    print(f"Saved composite PNG: {output_path}")
    print(f"Saved text details: {text_output}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    run_all(root / "data" / "input" / "sample_color.png", root / "data" / "output" / "all_results.png")
