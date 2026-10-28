import unittest
from unittest.mock import patch
import math
from dasar_pengolahan_citra_digital.src.image_io import Image
from dasar_pengolahan_citra_digital.src.filter_operations import mirror,brightness,contrast,denoise,edge

class FilterTests(unittest.TestCase):
    def test_shared_image_type_and_clamping(self):
        image=Image(1,1,[[(10,100,250)]])
        self.assertEqual(brightness(image,-40).pixels,[[(0,60,210)]])
        self.assertEqual(contrast(image,1.5,127).pixels,[[(0,86,255)]])
        self.assertEqual(image.pixels,[[(10,100,250)]])

    def test_mirror_mapping(self):
        image=Image(2,2,[[(1,1,1),(2,2,2)],[(3,3,3),(4,4,4)]])
        self.assertEqual(mirror(image,'horizontal').pixels[0],[(2,2,2),(1,1,1)])
        self.assertEqual(mirror(image,'vertical').pixels[0],[(3,3,3),(4,4,4)])

    def test_filters_keep_constant_image(self):
        image=Image(5,5,[[(73,73,73)]*5 for _ in range(5)])
        for method in ('gaussian','median','bilateral'):
            self.assertEqual(denoise(image,method,3).pixels,image.pixels)
        self.assertTrue(all(pixel==(0,0,0) for row in edge(image,50,150,3).pixels for pixel in row))

    def test_diagonal_canny_suppresses_weaker_center(self):
        image=Image(5,5,[[(0,0,0)]*5 for _ in range(5)])
        for slope in (1,-1):
            magnitude=[[0.0]*5 for _ in range(5)]
            magnitude[2][2]=100
            for y,x,value in ([(1,1,200),(3,3,200),(1,3,10),(3,1,10)] if slope==1 else [(1,3,200),(3,1,200),(1,1,10),(3,3,10)]):
                magnitude[y][x]=value
            gx=[[v/math.sqrt(2) for v in row] for row in magnitude]
            gy=[[slope*v/math.sqrt(2) for v in row] for row in magnitude]
            with patch('dasar_pengolahan_citra_digital.src.filter_operations._sobel',return_value=(gx,gy)):
                self.assertEqual(edge(image,20,80,3).pixels[2][2],(0,0,0))

    def test_synthetic_noise_is_repeatable_and_bounded(self):
        from dasar_pengolahan_citra_digital.src.create_filter_inputs import add_noise
        image=Image(20,20,[[(128,128,128)]*20 for _ in range(20)])
        for kind in ('salt-pepper','gaussian'):
            result=add_noise(image,kind)
            self.assertEqual(result.pixels,add_noise(image,kind).pixels)
            self.assertNotEqual(result.pixels,image.pixels)
            self.assertTrue(all(0<=v<=255 for row in result.pixels for p in row for v in p))
        impulse=add_noise(image,'salt-pepper')
        self.assertTrue(all(p in ((0,0,0),(128,128,128),(255,255,255)) for row in impulse.pixels for p in row))

    def test_psnr_known_difference(self):
        from dasar_pengolahan_citra_digital.src.run_filters import psnr
        reference=Image(1,1,[[(100,100,100)]])
        altered=Image(1,1,[[(110,110,110)]])
        self.assertTrue(math.isinf(psnr(reference,reference)))
        self.assertAlmostEqual(psnr(reference,altered),20*math.log10(255/10))
        with self.assertRaises(ValueError): psnr(reference,Image(2,1,[[(100,100,100)]*2]))

if __name__=='__main__': unittest.main()
