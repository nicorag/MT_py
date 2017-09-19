import inspect
import os
import unittest
from unittest import TestCase

from mtpy.utils.shapefiles import create_phase_tensor_shpfiles

edi_paths = [
    "",
    "tests/data/edifiles",
    "examples/data/edi2",
    "examples/data/edi_files",
    "../MT_Datasets/3D_MT_data_edited_fromDuanJM/",
    "../MT_Datasets/GA_UA_edited_10s-10000s/",
    "tests/data/edifiles2"
]

class TestPTShapeFile(TestCase):
    def setUp(self):
        self._temp_dir = "tests/temp"
        if not os.path.isdir(self._temp_dir):
            os.mkdir(self._temp_dir)

    def test_shapefile_01(self):
        edi_path = edi_paths[1]
        self._create_shape_file(edi_path, os.path.join(self._temp_dir, inspect.currentframe().f_code.co_name))

    @unittest.skipUnless(os.path.isdir(edi_paths[2]), "data file not found")
    def test_shapefile_02(self):
        edi_path = edi_paths[2]
        self._create_shape_file(edi_path, os.path.join(self._temp_dir, inspect.currentframe().f_code.co_name))

    @unittest.skipUnless(os.path.isdir(edi_paths[3]), "data file not found")
    def test_shapefile_03(self):
        edi_path = edi_paths[3]
        self._create_shape_file(edi_path, os.path.join(self._temp_dir, inspect.currentframe().f_code.co_name))

    @unittest.skipUnless(os.path.isdir(edi_paths[4]), "data file not found")
    def test_shapefile_04(self):
        edi_path = edi_paths[4]
        self._create_shape_file(edi_path, os.path.join(self._temp_dir, inspect.currentframe().f_code.co_name))

    @unittest.skipUnless(os.path.isdir(edi_paths[5]), "data file not found")
    def test_shapefile_05(self):
        edi_path = edi_paths[5]
        self._create_shape_file(edi_path, os.path.join(self._temp_dir, inspect.currentframe().f_code.co_name))

    @staticmethod
    def _create_shape_file(edi_path, save_path):
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        create_phase_tensor_shpfiles(edi_path, save_path, ellipse_size=6000, every_site=1)
