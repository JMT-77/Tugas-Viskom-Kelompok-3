"""Run with: python -m unittest discover -s dasar_pengolahan_citra_digital/tests -v."""
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from dasar_pengolahan_citra_digital.src.image_io import Image,read_image,write_image,comparison
from dasar_pengolahan_citra_digital.src.operations import properties,color_depth,resize_nearest,rotate


class OperationsTest(unittest.TestCase):
    def setUp(self):
        self.image=Image(3,2,[[(v,v,v) for v in row] for row in [[1,2,3],[4,5,6]]])

    def test_rotation_asymmetric_matrix(self):
        expected={0:[[1,2,3],[4,5,6]],90:[[4,1],[5,2],[6,3]],
                  180:[[6,5,4],[3,2,1]],270:[[3,6],[2,5],[1,4]]}
        for angle,values in expected.items():
            with self.subTest(angle=angle):
                actual=rotate(self.image,angle)
                self.assertEqual([[p[0] for p in row] for row in actual.pixels],values)
        self.assertEqual(rotate(self.image,-90).pixels,rotate(self.image,270).pixels)
        self.assertEqual(rotate(rotate(self.image,90),270).pixels,self.image.pixels)

    def test_quantization_endpoints_and_levels(self):
        ramp=Image(256,1,[[(v,v,v) for v in range(256)]])
        for bits in (1,4,8):
            result=color_depth(ramp,bits)
            self.assertEqual(len(set(p[0] for p in result.pixels[0])),2**bits)
            self.assertEqual(result.pixels[0][0],(0,0,0))
            self.assertEqual(result.pixels[0][-1],(255,255,255))
        self.assertEqual(color_depth(ramp,8).pixels,ramp.pixels)
        one=color_depth(Image(2,1,[[(127,128,255),(0,254,1)]]),1)
        self.assertEqual(one.pixels,[[(0,255,255),(0,255,0)]])

    def test_resize_mapping(self):
        result=resize_nearest(self.image,2,4)
        self.assertEqual([[p[0] for p in row] for row in result.pixels],[[1,2],[1,2],[4,5],[4,5]])
        self.assertEqual(resize_nearest(self.image,3,2).pixels,self.image.pixels)

    def test_properties_rgb_and_grayscale(self):
        rgb=properties(self.image)
        self.assertEqual((rgb['pixels'],rgb['bits_per_pixel'],rgb['raw_bytes']),(6,24,18))
        gray=properties(Image(3,2,self.image.pixels,'L'))
        self.assertEqual((gray['channels'],gray['bits_per_pixel'],gray['raw_bytes']),(1,8,6))

    def test_invalid_parameters(self):
        for bits in (0,9,2.5,True):
            with self.assertRaises(ValueError): color_depth(self.image,bits)
        for width,height in [(0,2),(2,-1),(1.5,2)]:
            with self.assertRaises(ValueError): resize_nearest(self.image,width,height)
        with self.assertRaises(ValueError): rotate(self.image,45)
        with self.assertRaises(ValueError): Image(2,2,[[(0,0,0)]])

    def test_manual_writer_roundtrip_and_comparison(self):
        with TemporaryDirectory() as directory:
            for extension in ('.png','.ppm','.pgm','.bmp'):
                path=Path(directory)/('test'+extension)
                write_image(self.image,path)
                self.assertEqual(read_image(path).pixels,self.image.pixels)
            preview=comparison([self.image,rotate(self.image,270)],['SEBELUM','ROTASI 270'])
            self.assertGreater(preview.width,self.image.width)
            path=Path(directory)/'preview.png';write_image(preview,path)
            loaded=read_image(path)
            self.assertEqual(loaded.pixels,preview.pixels)

if __name__=='__main__': unittest.main()
