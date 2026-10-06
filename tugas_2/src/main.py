import argparse
from pathlib import Path
from re import sub
from operations import read,write,mirror,rotate,edge,denoise,brightness,contrast

def main():
    p=argparse.ArgumentParser(description='Tugas 2 OpenCV image processing'); sub=p.add_subparsers(dest='command',required=True)
    m=sub.add_parser('mirror'); m.add_argument('input'); m.add_argument('output'); m.add_argument('--direction',choices=['horizontal','vertical'],default='horizontal')
    r=sub.add_parser('rotate'); r.add_argument('input'); r.add_argument('output'); r.add_argument('--angle',type=int,choices=[90,180,270],required=True)
    e=sub.add_parser('edge'); e.add_argument('input'); e.add_argument('output'); e.add_argument('--low',type=int,default=50); e.add_argument('--high',type=int,default=150); e.add_argument('--blur',type=int,choices=[3,5,7],default=5)
    n=sub.add_parser('denoise'); n.add_argument('input'); n.add_argument('output'); n.add_argument('--method',choices=['gaussian','median','bilateral'],default='median'); n.add_argument('--kernel',type=int,default=5)
    b=sub.add_parser('brightness'); b.add_argument('input'); b.add_argument('output'); b.add_argument('--c',type=int,required=True)
    k=sub.add_parser('contrast'); k.add_argument('input'); k.add_argument('output'); k.add_argument('--g',type=float,required=True); k.add_argument('--p',type=float,default=127)
    a=p.parse_args(); image=read(a.input)

    if a.command=='mirror': result=mirror(image,a.direction)
    elif a.command=='rotate': result=rotate(image,a.angle)
    elif a.command=='edge': result=edge(image,a.low,a.high,a.blur)
    elif a.command=='denoise': result=denoise(image,a.method,a.kernel)
    elif a.command=='brightness': result=brightness(image,a.c)
    else: result=contrast(image,a.g,a.p)
    write(a.output,result); print(f'Saved {Path(a.output)}')
if __name__=='__main__': main()
