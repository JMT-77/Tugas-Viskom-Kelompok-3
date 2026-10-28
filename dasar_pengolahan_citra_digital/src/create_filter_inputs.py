import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import random
from dasar_pengolahan_citra_digital.src.image_io import Image,read_image,write_image,_clamp


def add_noise(image,kind,seed=20261015):
    """Reproducible synthetic corruption: 6% impulse noise or Gaussian SD 20."""
    if kind not in ('salt-pepper','gaussian'): raise ValueError('Unknown noise type')
    rng=random.Random(seed);rows=[]
    for row in image.pixels:
        output=[]
        for pixel in row:
            if kind=='salt-pepper':
                chance=rng.random()
                output.append((0,0,0) if chance<0.03 else (255,255,255) if chance<0.06 else pixel)
            else:
                deviation=rng.gauss(0,20)
                output.append(tuple(_clamp(v+deviation) for v in pixel))
        rows.append(output)
    return Image(image.width,image.height,rows,image.mode)


def main():
    folder=Path(__file__).resolve().parents[1]/'data/input'
    camera=read_image(folder/'camera_clean.png');coins=read_image(folder/'coins_clean.png')
    for filename,image,kind in [('median_input.png',camera,'salt-pepper'),
                                ('gaussian_input.png',camera,'gaussian'),
                                ('bilateral_input.png',coins,'gaussian')]:
        write_image(add_noise(image,kind),folder/filename)
    print('Input noise sintetis dibuat ulang dengan seed 20261015')

if __name__=='__main__': main()
