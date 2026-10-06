"""CLI for Tugas 1. Run from the repository root."""
import argparse
from pathlib import Path
from image_io import read_image, write_image
from operations import color_depth, resize_nearest, rotate

def main():
    p=argparse.ArgumentParser(description="Tugas 1 pure Python image processing")
    sub=p.add_subparsers(dest="command",required=True)
    c=sub.add_parser("color-depth"); c.add_argument("input"); c.add_argument("output"); c.add_argument("--bits",type=int,default=4)
    r=sub.add_parser("resize"); r.add_argument("input"); r.add_argument("output"); r.add_argument("--width",type=int,required=True); r.add_argument("--height",type=int,required=True)
    t=sub.add_parser("rotate"); t.add_argument("input"); t.add_argument("output"); t.add_argument("--angle",type=int,choices=[0,90,180,270],required=True)
    a=p.parse_args(); image=read_image(a.input)
    result={"color-depth":lambda:color_depth(image,a.bits),"resize":lambda:resize_nearest(image,a.width,a.height),"rotate":lambda:rotate(image,a.angle)}[a.command]()
    write_image(result,a.output); print(f"Saved {Path(a.output)} ({result.width}x{result.height})")
if __name__=="__main__": main()
