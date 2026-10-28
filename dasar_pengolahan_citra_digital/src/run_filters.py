import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import math
import json
from dasar_pengolahan_citra_digital.src.image_io import read_image,save_comparison
from dasar_pengolahan_citra_digital.src.filter_operations import mirror,edge,denoise,brightness,contrast


def psnr(reference,image):
    if (reference.width,reference.height)!=(image.width,image.height): raise ValueError('PSNR dimensions differ')
    mse=sum((a-b)**2 for r1,r2 in zip(reference.pixels,image.pixels) for p1,p2 in zip(r1,r2) for a,b in zip(p1,p2))/(reference.width*reference.height*3)
    return math.inf if mse==0 else 10*math.log10(255**2/mse)


def run_all(input_dir,output_dir):
    source=Path(input_dir);output=Path(output_dir);output.mkdir(parents=True,exist_ok=True)
    apple=read_image(source/'internet_apple.png')
    coins=read_image(source/'edge_coins.png')
    intensity=read_image(source/'brightness_contrast.jpeg')
    for direction in ('horizontal','vertical'):
        save_comparison(output/f'mirror_{direction}.png',apple,mirror(apple,direction),'MIRROR '+direction)
    edges=edge(coins,40,100,5)
    save_comparison(output/'edge.png',coins,edges,'TEPI KOIN - CANNY MANUAL','LOW=40 HIGH=100 BLUR=5 - KONTUR, BUKAN PENGHITUNGAN KOIN')
    report={'edge':{'input':'edge_coins.png','low':40,'high':100,'blur':5,
                    'edge_pixels':sum(p[0]==255 for row in edges.pixels for p in row),
                    'limitation':'Boundary extraction only; no segmentation/counting or contour accuracy ground truth.'},
            'noise':{}}
    cases=[('median','median_input.png','camera_clean.png',3,'SALT-PEPPER 6%'),
           ('gaussian','gaussian_input.png','camera_clean.png',3,'GAUSSIAN SD20'),
           ('bilateral','bilateral_input.png','coins_clean.png',5,'GAUSSIAN SD20')]
    for method,filename,reference,kernel,kind in cases:
        noisy=read_image(source/filename);clean=read_image(source/reference)
        result=denoise(noisy,method,kernel)
        before=psnr(clean,noisy);after=psnr(clean,result)
        assert after>before,f'{method}: fixture quality did not improve'
        save_comparison(output/f'denoise_{method}.png',noisy,result,method+' FILTER',
                        f'{kind} - KERNEL={kernel} - PSNR {before:.2f} KE {after:.2f} DB')
        report['noise'][method]={'input':filename,'reference':reference,'synthetic_noise':kind,
                                'seed':20261015,'kernel':kernel,'psnr_before_db':before,
                                'psnr_after_db':after,'improvement_db':after-before}
        print(f'{method}: PSNR {before:.2f} -> {after:.2f} dB',flush=True)
    save_comparison(output/'brightness.png',intensity,brightness(intensity,40),'BRIGHTNESS','C=40')
    save_comparison(output/'contrast.png',intensity,contrast(intensity,1.5,127),'CONTRAST','G=1.5 P=127')
    (output/'filter_metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Filter dan intensitas selesai:',output,flush=True)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    run_all(root/'data/input',root/'data/output')
