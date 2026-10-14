"""Minimal image I/O for Tugas 1. No third-party packages."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import binascii
import struct
import zlib

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
    if suffix == ".png":
        return _read_png(path)
    raise ValueError("Tugas 1 supports .png, .ppm, .pgm, and .bmp (24/32-bit) only")

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

def _read_png(path: Path) -> Image:
    """Read simple non-interlaced 8-bit PNG using only the standard library."""
    data=path.read_bytes(); signature=b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature): raise ValueError("Not a PNG file")
    pos=len(signature); compressed=bytearray(); width=height=bit_depth=color_type=interlace=None
    while pos < len(data):
        length=struct.unpack_from(">I",data,pos)[0]; pos+=4; kind=data[pos:pos+4]; pos+=4
        chunk=data[pos:pos+length]; pos+=length+4
        if kind==b"IHDR":
            width,height,bit_depth,color_type,compression,filtering,interlace=struct.unpack(">IIBBBBB",chunk)
            if compression!=0 or filtering!=0 or interlace!=0: raise ValueError("Only non-interlaced PNG supported")
            if bit_depth!=8 or color_type not in (0,2,4,6): raise ValueError("PNG must be 8-bit grayscale/RGB/RGBA")
        elif kind==b"IDAT": compressed.extend(chunk)
        elif kind==b"IEND": break
    if width is None or height is None: raise ValueError("PNG is missing IHDR")
    channels={0:1,2:3,4:2,6:4}[color_type]; row_bytes=width*channels; raw=zlib.decompress(bytes(compressed)); stride=row_bytes+1
    if len(raw)!=stride*height: raise ValueError("PNG pixel data has an invalid size")
    rows=[]; previous=bytearray(row_bytes); offset=0
    for _ in range(height):
        filter_type=raw[offset]; current=bytearray(raw[offset+1:offset+stride]); offset+=stride
        for i in range(row_bytes):
            left=current[i-channels] if i>=channels else 0; up=previous[i]; upper_left=previous[i-channels] if i>=channels else 0
            if filter_type==1: current[i]=(current[i]+left)&255
            elif filter_type==2: current[i]=(current[i]+up)&255
            elif filter_type==3: current[i]=(current[i]+((left+up)//2))&255
            elif filter_type==4:
                p=left+up-upper_left; pa=abs(p-left); pb=abs(p-up); pc=abs(p-upper_left); predictor=left if pa<=pb and pa<=pc else (up if pb<=pc else upper_left); current[i]=(current[i]+predictor)&255
            elif filter_type!=0: raise ValueError(f"Unsupported PNG filter: {filter_type}")
        row=[]
        for x in range(width):
            values=current[x*channels:(x+1)*channels]
            row.append((values[0],values[0],values[0]) if color_type in (0,4) else tuple(values[:3]))
        rows.append(row); previous=current
    return Image(width,height,rows)

def write_image(image: Image, filename: str | Path):
    path=Path(filename); path.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix.lower()==".png":
        _write_png(image, path)
    elif path.suffix.lower()==".txt":
        with path.open("w",encoding="utf-8") as f:
            f.write("VISKOM_RGB_TEXT\n")
            f.write(f"width={image.width}\nheight={image.height}\nchannels=RGB\n")
            f.write("pixels=\n")
            for row in image.pixels:
                f.write(" ".join(f"{r},{g},{b}" for r,g,b in row)+"\n")
    elif path.suffix.lower()==".pgm":
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
    else: raise ValueError("Output must use .png, .txt, .ppm, .pgm, or .bmp")


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind + payload) & 0xffffffff
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _write_png(image: Image, path: Path) -> None:
    """Write an 8-bit RGB PNG with only the Python standard library."""
    raw = bytearray()
    for row in image.pixels:
        raw.append(0)
        for red, green, blue in row:
            raw.extend((_clamp(red), _clamp(green), _clamp(blue)))
    ihdr = struct.pack(">IIBBBBB", image.width, image.height, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)
