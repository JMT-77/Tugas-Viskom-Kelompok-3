"""Shared RGB matrices, input decoding and manual output/visualization.
Pillow is used only inside read_image(). Every other operation uses stdlib.
"""
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
    mode: str = "RGB"

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image dimensions must be positive")
        if len(self.pixels) != self.height or any(len(row) != self.width for row in self.pixels):
            raise ValueError("Pixel matrix dimensions do not match image dimensions")


def _clamp(value):
    return max(0, min(255, round(value)))


def read_image(filename):
    from PIL import Image as Decoder
    with Decoder.open(filename) as decoded:
        mode = "L" if decoded.mode == "L" else "RGB"
        rgb = decoded.convert("RGB")
        width, height = rgb.size
        flat = list(rgb.get_flattened_data() if hasattr(rgb, "get_flattened_data") else rgb.getdata())
    return Image(width, height, [flat[y*width:(y+1)*width] for y in range(height)], mode)


def canvas(width, height, color=(255,255,255)):
    return Image(width,height,[[color]*width for _ in range(height)])


def paste(target, source, left, top):
    for y,row in enumerate(source.pixels):
        target.pixels[top+y][left:left+source.width] = row


# A small bitmap font keeps labels independent of Pillow/OpenCV drawing APIs.
_FONT = {
'A':'010/101/111/101/101','B':'110/101/110/101/110','C':'011/100/100/100/011',
'D':'110/101/101/101/110','E':'111/100/110/100/111','F':'111/100/110/100/100',
'G':'011/100/101/101/011','H':'101/101/111/101/101','I':'111/010/010/010/111',
'J':'001/001/001/101/010','K':'101/101/110/101/101','L':'100/100/100/100/111',
'M':'101/111/111/101/101','N':'101/111/111/111/101','O':'010/101/101/101/010',
'P':'110/101/110/100/100','Q':'010/101/101/111/011','R':'110/101/110/101/101',
'S':'011/100/010/001/110','T':'111/010/010/010/010','U':'101/101/101/101/111',
'V':'101/101/101/101/010','W':'101/101/111/111/101','X':'101/101/010/101/101',
'Y':'101/101/010/010/010','Z':'111/001/010/100/111','0':'111/101/101/101/111',
'1':'010/110/010/010/111','2':'110/001/010/100/111','3':'110/001/010/001/110',
'4':'101/101/111/001/001','5':'111/100/110/001/110','6':'011/100/111/101/111',
'7':'111/001/010/010/010','8':'111/101/111/101/111','9':'111/101/111/001/110',
'.':'000/000/000/000/010',':':'000/010/000/010/000','-':'000/000/111/000/000',
'/':'001/001/010/100/100','=':'000/111/000/111/000','+':'000/010/111/010/000',
'(':'001/010/010/010/001',')':'100/010/010/010/100','%':'101/001/010/100/101',
'_':'000/000/000/000/111',' ':'000/000/000/000/000'
}


def draw_text(image, text, x=12, y=12, color=(25,25,25), scale=2):
    origin=x
    for char in text.upper():
        if char == "\n" or x+3*scale >= image.width-10:
            x=origin; y+=7*scale
            if char == "\n": continue
        for dy,row in enumerate(_FONT.get(char,_FONT[' ']).split('/')):
            for dx,bit in enumerate(row):
                if bit=='1':
                    for sy in range(scale):
                        for sx in range(scale):
                            px=x+dx*scale+sx; py=y+dy*scale+sy
                            if 0<=px<image.width and 0<=py<image.height: image.pixels[py][px]=color
        x+=4*scale


def comparison(images, labels, note=""):
    if not images or len(images)!=len(labels): raise ValueError("Images and labels must match")
    width=max(320,max(i.width for i in images)); height=max(i.height for i in images)
    header=76; footer=48 if note else 0
    output=canvas(width*len(images)+12*(len(images)+1),header+height+footer+12,(235,239,244))
    for index,(img,label) in enumerate(zip(images,labels)):
        left=12+index*(width+12)
        panel=canvas(width,header+height,(255,255,255))
        draw_text(panel,label+f"\n{img.width} X {img.height} PX")
        paste(panel,img,(width-img.width)//2,header+(height-img.height)//2)
        paste(output,panel,left,0)
    if note: draw_text(output,note,12,header+height+10)
    return output


def save_comparison(path, before, after, label, note=""):
    write_image(comparison([before,after],["SEBELUM",label],note),path)


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
