import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from dasar_pengolahan_citra_digital.src.image_io import Image,draw_text,write_image


def create_sample(path):
    """An asymmetric RGB gradient makes quantization and rotation visible."""
    width,height=320,200
    pixels=[[(round(255*x/(width-1)),round(255*y/(height-1)),round(255*(1-x/(width-1)))) for x in range(width)] for y in range(height)]
    image=Image(width,height,pixels)
    for y in range(20,65):
        for x in range(20,95): image.pixels[y][x]=(255,225,30)
    for y in range(115,180):
        for x in range(240,300):
            if (x-270)**2+(y-147)**2<26**2: image.pixels[y][x]=(30,30,30)
    for y in range(92,108):
        for x in range(120,220): image.pixels[y][x]=(255,255,255)
    for y in range(75,125):
        for x in range(205,245):
            if x-205<=25-abs(y-100): image.pixels[y][x]=(255,255,255)
    draw_text(image,'ATAS KIRI',23,32,scale=2)
    draw_text(image,'KANAN',155,130,scale=2)
    write_image(image,path)
    return image

if __name__=='__main__':
    create_sample(Path(__file__).resolve().parents[1]/'data/input/sample_asymmetric.png')
