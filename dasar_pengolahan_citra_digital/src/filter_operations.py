"""Existing intensity/neighborhood formulas, reusing the shared image type."""
from __future__ import annotations
import math
from dasar_pengolahan_citra_digital.src.image_io import Image,_clamp

def _pixel(image: Image, x: int, y: int) -> tuple[int,int,int]:
    return image.pixels[max(0, min(image.height - 1, y))][max(0, min(image.width - 1, x))]

def mirror(image: Image, direction: str) -> Image:
    if direction not in ("horizontal","vertical"): raise ValueError("direction must be horizontal or vertical")
    rows=[list(reversed(row)) for row in image.pixels] if direction=="horizontal" else list(reversed(image.pixels))
    return Image(image.width,image.height,rows)

def _gray(image: Image) -> list[list[float]]:
    return [[0.299*r+0.587*g+0.114*b for r,g,b in row] for row in image.pixels]

def _from_gray(values: list[list[float]]) -> Image:
    return Image(len(values[0]),len(values),[[( _clamp(value),_clamp(value),_clamp(value)) for value in row] for row in values])

def _kernel_gaussian(size: int, sigma: float|None=None) -> list[list[float]]:
    if size<3 or size%2==0: raise ValueError("kernel must be an odd integer >= 3")
    sigma=sigma or max(0.8,size/3); radius=size//2; kernel=[]; total=0.0
    for y in range(-radius,radius+1):
        row=[]
        for x in range(-radius,radius+1):
            value=math.exp(-(x*x+y*y)/(2*sigma*sigma)); row.append(value); total+=value
        kernel.append(row)
    return [[value/total for value in row] for row in kernel]

def _convolve(values: list[list[float]], kernel: list[list[float]]) -> list[list[float]]:
    height=len(values); width=len(values[0]); radius=len(kernel)//2; output=[]
    for y in range(height):
        row=[]
        for x in range(width):
            total=0.0
            for ky in range(len(kernel)):
                for kx in range(len(kernel)):
                    sy=max(0,min(height-1,y+ky-radius)); sx=max(0,min(width-1,x+kx-radius)); total+=values[sy][sx]*kernel[ky][kx]
            row.append(total)
        output.append(row)
    return output

def _filter_channels(image: Image, kernel: list[list[float]]) -> Image:
    channels=[]
    for channel in range(3):
        values=[[float(image.pixels[y][x][channel]) for x in range(image.width)] for y in range(image.height)]
        channels.append(_convolve(values,kernel))
    rows=[]
    for y in range(image.height):
        row=[]
        for x in range(image.width):
            row.append((_clamp(channels[0][y][x]), _clamp(channels[1][y][x]), _clamp(channels[2][y][x])))
        rows.append(row)
    return Image(image.width,image.height,rows)

def _sobel(values: list[list[float]]) -> tuple[list[list[float]],list[list[float]]]:
    gx_kernel=((-1,0,1),(-2,0,2),(-1,0,1)); gy_kernel=((-1,-2,-1),(0,0,0),(1,2,1)); height=len(values); width=len(values[0]); gx=[]; gy=[]
    for y in range(height):
        row_x=[]; row_y=[]
        for x in range(width):
            total_x=total_y=0.0
            for ky in range(3):
                for kx in range(3):
                    value=values[max(0,min(height-1,y+ky-1))][max(0,min(width-1,x+kx-1))]; total_x+=value*gx_kernel[ky][kx]; total_y+=value*gy_kernel[ky][kx]
            row_x.append(total_x); row_y.append(total_y)
        gx.append(row_x); gy.append(row_y)
    return gx,gy

def edge(image: Image, low: int, high: int, blur: int) -> Image:
    if low<0 or high<=low: raise ValueError("high must be greater than low >= 0")
    blurred=_convolve(_gray(image),_kernel_gaussian(blur)); gx,gy=_sobel(blurred); height=len(blurred); width=len(blurred[0])
    magnitude=[[math.hypot(gx[y][x],gy[y][x]) for x in range(width)] for y in range(height)]; angle=[[math.degrees(math.atan2(gy[y][x],gx[y][x]))%180 for x in range(width)] for y in range(height)]; thin=[[0.0]*width for _ in range(height)]
    for y in range(1,height-1):
        for x in range(1,width-1):
            direction=angle[y][x]
            if direction<22.5 or direction>=157.5: a,b=magnitude[y][x-1],magnitude[y][x+1]
            elif direction<67.5: a,b=magnitude[y-1][x-1],magnitude[y+1][x+1]
            elif direction<112.5: a,b=magnitude[y-1][x],magnitude[y+1][x]
            else: a,b=magnitude[y-1][x+1],magnitude[y+1][x-1]
            if magnitude[y][x]>=a and magnitude[y][x]>=b: thin[y][x]=magnitude[y][x]
    strong=255.0; weak=75.0; classified=[[strong if value>=high else weak if value>=low else 0.0 for value in row] for row in thin]; changed=True
    while changed:
        changed=False
        for y in range(1,height-1):
            for x in range(1,width-1):
                if classified[y][x]==weak and any(classified[ny][nx]==strong for ny in range(y-1,y+2) for nx in range(x-1,x+2)): classified[y][x]=strong; changed=True
    return _from_gray([[strong if value==strong else 0.0 for value in row] for row in classified])

def denoise(image: Image, method: str, kernel: int) -> Image:
    if method not in ("gaussian","median","bilateral"): raise ValueError("Unknown denoise method")
    if kernel<3 or kernel%2==0: raise ValueError("kernel must be an odd integer >= 3")
    if method=="gaussian": return _filter_channels(image,_kernel_gaussian(kernel))
    radius=kernel//2; output=[]
    for y in range(image.height):
        row=[]
        for x in range(image.width):
            samples=[_pixel(image,sx,sy) for sy in range(y-radius,y+radius+1) for sx in range(x-radius,x+radius+1)]
            if method=="median": row.append(tuple(sorted(pixel[c] for pixel in samples)[len(samples)//2] for c in range(3))); continue
            sigma_space=max(1.0,kernel/2); sigma_range=50.0; center=_pixel(image,x,y); weighted=[0.0,0.0,0.0]; total=0.0
            for sy in range(y-radius,y+radius+1):
                for sx in range(x-radius,x+radius+1):
                    pixel=_pixel(image,sx,sy); spatial=math.exp(-((sx-x)**2+(sy-y)**2)/(2*sigma_space*sigma_space)); difference=sum((pixel[c]-center[c])**2 for c in range(3)); weight=spatial*math.exp(-difference/(2*sigma_range*sigma_range)); total+=weight
                    for c in range(3): weighted[c]+=pixel[c]*weight
            row.append(tuple(_clamp(value/total) for value in weighted))
        output.append(row)
    return Image(image.width,image.height,output)

def brightness(image: Image, c: int) -> Image:
    return Image(image.width,image.height,[[( _clamp(r+c),_clamp(g+c),_clamp(b+c)) for r,g,b in row] for row in image.pixels])

def contrast(image: Image, g: float, p: float=127) -> Image:
    return Image(image.width,image.height,[[( _clamp(g*r+p*(1-g)),_clamp(g*green+p*(1-g)),_clamp(g*b+p*(1-g))) for r,green,b in row] for row in image.pixels])
