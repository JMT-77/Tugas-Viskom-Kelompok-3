import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import argparse
import json
from dasar_pengolahan_citra_digital.src.image_io import read_image,write_image,save_comparison
from dasar_pengolahan_citra_digital.src.operations import properties,color_depth,resize_nearest,rotate
from dasar_pengolahan_citra_digital.src.filter_operations import mirror,edge,denoise,brightness,contrast


def main():
    p=argparse.ArgumentParser(description='Dasar pengolahan citra digital: rumus manual')
    sub=p.add_subparsers(dest='command',required=True)
    info=sub.add_parser('info'); info.add_argument('input')
    c=sub.add_parser('color-depth'); c.add_argument('--bits',type=int,default=4)
    r=sub.add_parser('resize'); r.add_argument('--width',type=int,required=True); r.add_argument('--height',type=int,required=True)
    t=sub.add_parser('rotate'); t.add_argument('--angle',type=int,choices=[0,90,180,270],required=True)
    m=sub.add_parser('mirror'); m.add_argument('--direction',choices=['horizontal','vertical'],default='horizontal')
    e=sub.add_parser('edge'); e.add_argument('--low',type=int,default=50); e.add_argument('--high',type=int,default=150); e.add_argument('--blur',type=int,choices=[3,5,7],default=5)
    n=sub.add_parser('denoise'); n.add_argument('--method',choices=['gaussian','median','bilateral'],default='median'); n.add_argument('--kernel',type=int,default=5)
    b=sub.add_parser('brightness'); b.add_argument('--c',type=int,required=True)
    k=sub.add_parser('contrast'); k.add_argument('--g',type=float,required=True); k.add_argument('--p',type=float,default=127)
    for parser in (c,r,t,m,e,n,b,k): parser.add_argument('input'); parser.add_argument('output')
    a=p.parse_args(); image=read_image(a.input)
    if a.command=='info': print(json.dumps(properties(image),indent=2)); return
    if a.command=='color-depth': result=color_depth(image,a.bits)
    elif a.command=='resize': result=resize_nearest(image,a.width,a.height)
    elif a.command=='rotate': result=rotate(image,a.angle)
    elif a.command=='mirror': result=mirror(image,a.direction)
    elif a.command=='edge': result=edge(image,a.low,a.high,a.blur)
    elif a.command=='denoise': result=denoise(image,a.method,a.kernel)
    elif a.command=='brightness': result=brightness(image,a.c)
    else: result=contrast(image,a.g,a.p)
    if Path(a.output).suffix.lower()=='.png': save_comparison(a.output,image,result,a.command)
    else: write_image(result,a.output)
    print('Saved',a.output)

if __name__=='__main__': main()
