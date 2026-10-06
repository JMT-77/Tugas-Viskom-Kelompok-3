"""Pure-Python image operations for Tugas 1."""
from __future__ import annotations
try:
    from .image_io import Image
except ImportError:  # direct execution: python src/main.py
    from image_io import Image

def color_depth(image: Image, bits: int) -> Image:
    if not 1 <= bits <= 8: raise ValueError("bits must be between 1 and 8")
    levels=(1<<bits)-1
    def q(c): return round(round(c/255*levels)/levels*255)
    return Image(image.width,image.height,[[(q(r),q(g),q(b)) for r,g,b in row] for row in image.pixels])

def resize_nearest(image: Image, width: int, height: int) -> Image:
    if width<=0 or height<=0: raise ValueError("width and height must be positive")
    rows=[]
    for y in range(height):
        sy=min(image.height-1,int(y*image.height/height)); row=[]
        for x in range(width): row.append(image.pixels[sy][min(image.width-1,int(x*image.width/width))])
        rows.append(row)
    return Image(width,height,rows)

def rotate(image: Image, angle: int) -> Image:
    angle%=360
    if angle not in (0,90,180,270): raise ValueError("angle must be 0, 90, 180, or 270")
    if angle==0: return image
    if angle==90: rows=[[image.pixels[image.height-1-y][x] for y in range(image.height)] for x in range(image.width)]
    elif angle==180: rows=[list(reversed(row)) for row in reversed(image.pixels)]
    else: rows=[[image.pixels[y][image.width-1-x] for y in range(image.height-1,-1,-1)] for x in range(image.width-1,-1,-1)]
    return Image(len(rows[0]),len(rows),rows)
