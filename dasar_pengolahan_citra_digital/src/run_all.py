import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import json
from dasar_pengolahan_citra_digital.src.image_io import read_image,write_image,save_comparison,comparison,canvas,draw_text
from dasar_pengolahan_citra_digital.src.operations import properties,color_depth,resize_nearest,rotate


def run_all(input_path,output_dir):
    output=Path(output_dir); output.mkdir(parents=True,exist_ok=True)
    image=read_image(input_path); info=properties(image)
    board=canvas(420,max(260,image.height))
    draw_text(board,'PROPERTI CITRA\n'+ '\n'.join(f'{k}: {v}' for k,v in info.items()))
    write_image(comparison([image,board],['CITRA SUMBER','DEPTH DAN RESOLUSI']),output/'properti.png')
    for bits in (1,4,8):
        result=color_depth(image,bits)
        save_comparison(output/f'color_depth_{bits}bit.png',image,result,f'KUANTISASI {bits} BIT',f'{2**bits} LEVEL/KANAL - PNG TETAP 8 BIT/KANAL')
    width=max(1,image.width//2); height=max(1,image.height//2)
    resized=resize_nearest(image,width,height)
    save_comparison(output/'resolusi.png',image,resized,'RESIZE NEAREST',f'{image.width*image.height} KE {width*height} PIKSEL')
    for angle in (90,180,270):
        result=rotate(image,angle)
        save_comparison(output/f'rotasi_{angle}.png',image,result,f'ROTASI {angle} DERAJAT', 'SEARAH JARUM JAM - NILAI RGB TETAP')
    text_output=output/'text'
    for filename,result in [('color_depth',color_depth(image,4)),('resolusi',resized),('rotasi',rotate(image,90))]:
        write_image(result,text_output/f'{filename}.txt')
    x=min(image.width-1,image.width//3+1); y=min(image.height-1,image.height//3+1); value=image.pixels[y][x][0]; levels=15
    report={'properties':info,'coordinate_example':{'x':x,'y':y,'matrix_index':[y,x],'rgb':image.pixels[y][x]},
            'color_depth_example':{'input_R':value,'formula':'round(round(R/255*15)/15*255)',
                                  'manual':round(round(value/255*levels)/levels*255),
                                  'program':color_depth(image,4).pixels[y][x][0]},
            'note':'Properties describe decoded 8-bit pixels; raw_bytes excludes file headers/compression. Quantization changes effective levels, not PNG storage bit depth.'}
    report['red_patch_5x5']=[[image.pixels[min(image.height-1,max(0,y+dy))][min(image.width-1,max(0,x+dx))][0] for dx in range(-2,3)] for dy in range(-2,3)]
    rx=min(resized.width-1,resized.width//3+1); ry=min(resized.height-1,resized.height//3+1)
    sx=rx*image.width//resized.width; sy=ry*image.height//resized.height
    report['resize_example']={'output_xy':[rx,ry],'source_xy':[sx,sy],
                              'formula':'sx=floor(x*W_in/W_out), sy=floor(y*H_in/H_out)',
                              'manual_rgb':image.pixels[sy][sx],'program_rgb':resized.pixels[ry][rx]}
    assert report['resize_example']['manual_rgb']==report['resize_example']['program_rgb']
    report['rotation_examples']={}
    for angle,(tx,ty) in {90:(image.height-1-y,x),180:(image.width-1-x,image.height-1-y),270:(y,image.width-1-x)}.items():
        actual=rotate(image,angle).pixels[ty][tx]
        report['rotation_examples'][str(angle)]={'source_xy':[x,y],'destination_xy':[tx,ty],
                                               'manual_rgb':image.pixels[y][x],'program_rgb':actual}
        assert actual==image.pixels[y][x]
    assert report['color_depth_example']['manual']==report['color_depth_example']['program']
    (output/'perhitungan.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Properti dan geometri selesai:',output)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    run_all(root/'data/input/sample_asymmetric.png',root/'data/output')
    from dasar_pengolahan_citra_digital.src.run_filters import run_all as run_filters
    run_filters(root/'data/input',root/'data/output')
