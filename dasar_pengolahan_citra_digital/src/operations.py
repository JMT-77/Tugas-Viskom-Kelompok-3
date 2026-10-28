"""Depth, resolution and shared geometry, calculated from pixel matrices."""
from dasar_pengolahan_citra_digital.src.image_io import Image


def properties(image):
    channels=1 if image.mode=='L' else 3
    pixels=image.width*image.height
    return {'width':image.width,'height':image.height,'pixels':pixels,
            'megapixels':pixels/1_000_000,'mode':image.mode,'channels':channels,
            'bits_per_channel':8,'bits_per_pixel':8*channels,
            'levels_per_channel':256,'color_combinations':2**(8*channels),
            'raw_bytes':pixels*channels}


def color_depth(image, bits):
    if type(bits) is not int or not 1<=bits<=8: raise ValueError('bits must be 1..8')
    levels=(1<<bits)-1
    def q(v): return round(round(v/255*levels)/levels*255)
    return Image(image.width,image.height,[[tuple(q(v) for v in p) for p in row] for row in image.pixels],image.mode)


def resize_nearest(image,width,height):
    if type(width) is not int or type(height) is not int or width<=0 or height<=0: raise ValueError('Dimensions must be positive')
    return Image(width,height,[[image.pixels[min(image.height-1,y*image.height//height)][min(image.width-1,x*image.width//width)] for x in range(width)] for y in range(height)],image.mode)


def rotate(image,angle):
    if type(angle) is not int: raise ValueError('angle must be an integer')
    angle%=360
    if angle not in (0,90,180,270): raise ValueError('angle must be 0, 90, 180 or 270')
    if angle==0: rows=[row[:] for row in image.pixels]
    elif angle==90: rows=[[image.pixels[y][x] for y in range(image.height-1,-1,-1)] for x in range(image.width)]
    elif angle==180: rows=[row[::-1] for row in image.pixels[::-1]]
    else: rows=[[image.pixels[y][x] for y in range(image.height)] for x in range(image.width-1,-1,-1)]
    return Image(len(rows[0]),len(rows),rows,image.mode)
