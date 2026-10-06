"""Minimal image I/O for Tugas 1. No third-party packages."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import struct

@dataclass
class Image:
    width: int
    height: int
    pixels: list[list[tuple[int, int, int]]]

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image dimensions must be positive")
        if len(self.pixels) != self.height or any(len(row) != self.width for row in self.pixels):
            raise ValueError("Pixel matrix dimensions do not match image dimensions")

def _clamp(v: int) -> int:
    return max(0, min(255, int(v)))

def _tokens(path: Path):
    data = path.read_bytes()
    if data.startswith((b"P3", b"P6", b"P2", b"P5")):
        return data
    return None

def read_image(filename: str | Path) -> Image:
    path = Path(filename)
    suffix = path.suffix.lower()
    if suffix in {".ppm", ".pgm"}:
        return _read_pnm(path)
    if suffix == ".bmp":
        return _read_bmp(path)
    raise ValueError("Tugas 1 supports .ppm, .pgm, and .bmp (24/32-bit) only")

def _read_pnm(path: Path) -> Image:
    data = path.read_bytes()
    magic = data[:2]
    if magic not in {b"P2", b"P3", b"P5", b"P6"}:
        raise ValueError("Unsupported PNM format")
    if magic in {b"P2", b"P3"}:
        text = data.decode("ascii")
        clean = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
        parts = clean.split(); kind = parts[0]; width, height, maximum = map(int, parts[1:4])
        values = list(map(int, parts[4:]))
    else:
        idx = 0; tokens = []
        while len(tokens) < 4:
            while idx < len(data) and data[idx] in b" \t\r\n": idx += 1
            if idx < len(data) and data[idx] == 35:
                while idx < len(data) and data[idx] not in b"\r\n": idx += 1
                continue
            start = idx
            while idx < len(data) and data[idx] not in b" \t\r\n": idx += 1
            tokens.append(data[start:idx].decode("ascii"))
        kind, width, height, maximum = tokens[0], int(tokens[1]), int(tokens[2]), int(tokens[3])
        while idx < len(data) and data[idx] in b" \t\r\n": idx += 1
        channels = 3 if kind == "P6" else 1
        step = 1 if maximum < 256 else 2
        values = []
        for i in range(width * height * channels):
            raw = data[idx+i*step:idx+(i+1)*step]
            values.append(int.from_bytes(raw, "big"))
    if maximum <= 0: raise ValueError("Invalid PNM maximum value")
    pixels=[]; i=0
    for _ in range(height):
        row=[]
        for _ in range(width):
            if kind in {"P2", "P5"}:
                g=round(values[i]*255/maximum); i+=1; row.append((g,g,g))
            else:
                rgb=tuple(round(values[i+j]*255/maximum) for j in range(3)); i+=3; row.append(rgb)
        pixels.append(row)
    return Image(width,height,pixels)

def _read_bmp(path: Path) -> Image:
    data=path.read_bytes()
    if data[:2] != b"BM": raise ValueError("Not a BMP file")
    pixel_offset=struct.unpack_from("<I",data,10)[0]
    dib_size=struct.unpack_from("<I",data,14)[0]
    if dib_size < 40: raise ValueError("Unsupported BMP header")
    width,height,planes,bits,compression=struct.unpack_from("<iiHHI",data,18)
    if planes != 1 or bits not in (24,32) or compression != 0: raise ValueError("Only uncompressed 24/32-bit BMP supported")
    top_down=height<0; height=abs(height); row_size=((width*bits+31)//32)*4; pixels=[]
    for y in range(height):
        source_y=y if top_down else height-1-y; start=pixel_offset+source_y*row_size; row=[]
        for x in range(width):
            b,g,r=data[start+x*(bits//8):start+x*(bits//8)+3]; row.append((r,g,b))
        pixels.append(row)
    return Image(width,height,pixels)

def write_image(image: Image, filename: str | Path):
    path=Path(filename); path.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix.lower()==".pgm":
        with path.open("wb") as f:
            f.write(f"P5\n{image.width} {image.height}\n255\n".encode("ascii"))
            for row in image.pixels:
                for r,g,b in row: f.write(bytes([round((r+g+b)/3)]))
    elif path.suffix.lower()==".ppm":
        with path.open("wb") as f:
            f.write(f"P6\n{image.width} {image.height}\n255\n".encode("ascii"))
            for row in image.pixels:
                for rgb in row: f.write(bytes(_clamp(c) for c in rgb))
    elif path.suffix.lower()==".bmp":
        row_size=(image.width*3+3)//4*4; pixel_size=row_size*image.height
        header=struct.pack("<2sIHHI",b"BM",54+pixel_size,0,0,54)
        dib=struct.pack("<IiiHHIIiiII",40,image.width,image.height,1,24,0,pixel_size,2835,2835,0,0)
        with path.open("wb") as f:
            f.write(header+dib)
            for row in reversed(image.pixels):
                raw=b"".join(bytes((_clamp(b),_clamp(g),_clamp(r))) for r,g,b in row); f.write(raw+b"\0"*(row_size-len(raw)))
    else: raise ValueError("Output must use .ppm, .pgm, or .bmp")
