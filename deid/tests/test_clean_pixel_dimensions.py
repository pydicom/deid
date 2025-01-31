#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom import utils
from deid.utils import get_installdir


class TestCleanPizelDimensions(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deidpath = os.path.abspath("%s/tests/resources/" % self.pwd)
        self.dataset = get_dataset("ultrasounds")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_4d_RGB_cine_clip(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified
        on "4D" images - RGB cine clips.  Pixel data will have the shape (frames, X, Y, channel)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "RGB_CINE.zip", self.tmpdir)
        deid = os.path.join(self.deidpath, "remove_coordinates_us.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[:, 0:500, 0:500, :] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_3d_Greyscale_cine_clip(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified
        on "3D" images - greyscale cine clips.  Pixel data will have the shape (frames, X, Y)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "GREYSCALE_CINE.zip", self.tmpdir)
        deid = os.path.join(self.deidpath, "remove_coordinates_us.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[:, 0:500, 0:500] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_3d_RGB_image(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified
        on "3D" images - RGB images.  Pixel data will have the shape (X, Y, channel)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "RGB_IMAGE.dcm")
        deid = os.path.join(self.deidpath, "remove_coordinates_us.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[0:500, 0:500, :] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_2d_Greyscale_image(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified
        on "2D" images - Greyscale images.  Pixel data will have the shape (X, Y)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "GREYSCALE_IMAGE.dcm")
        deid = os.path.join(self.deidpath, "remove_coordinates_us.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[0:500, 0:500] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_4d_RGB_cine_clip_all(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified - all keyword -
        on "4D" images - RGB cine clips.  Pixel data will have the shape (frames, X, Y, channel)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "RGB_CINE.zip", self.tmpdir)
        deid = os.path.join(self.deidpath, "remove_coordinates_us_all.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[:, :, :, :] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_3d_Greyscale_cine_clip_all(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified - all keyword -
        on "3D" images - greyscale cine clips.  Pixel data will have the shape (frames, X, Y)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "GREYSCALE_CINE.zip", self.tmpdir)
        deid = os.path.join(self.deidpath, "remove_coordinates_us_all.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[:, :, :] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_3d_RGB_image_all(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified - all keyword -
        on "3D" images - RGB images.  Pixel data will have the shape (X, Y, channel)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "RGB_IMAGE.dcm")
        deid = os.path.join(self.deidpath, "remove_coordinates_us_all.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[:, :, :] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_2d_Greyscale_image_all(self):
        """
        Test the pixel cleaner to ensure pixels are appropriately deidentified - all keyword -
        on "2D" images - Greyscale images.  Pixel data will have the shape (X, Y)
        """
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset, "GREYSCALE_IMAGE.dcm")
        deid = os.path.join(self.deidpath, "remove_coordinates_us_all.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        client.clean()
        cleanedfile = client.save_dicom()

        outputfile = utils.dcmread(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = utils.dcmread(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[:, :] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())


def get_file(dataset, image, tempdir=None):
    """
    Helper to get a dicom file
    """
    from deid.dicom import get_files

    dicom_files = get_files(dataset, pattern=image, tempdir=tempdir)
    return next(dicom_files)


if __name__ == "__main__":
    unittest.main()
