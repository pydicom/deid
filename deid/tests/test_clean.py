#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest
from copy import deepcopy

from deid.config import DeidRecipe
from deid.data import get_dataset
from deid.dicom import utils
from deid.dicom.pixels import clean_pixel_data, has_burned_pixels
from deid.tests.common import get_file
from deid.utils import get_installdir

global generate_uid


class TestClean(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deidpath = os.path.abspath("%s/tests/resources/" % self.pwd)
        self.dataset = get_dataset("animals")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_pixel_cleaner_remove_coordinates(self):
        """Test the pixel cleaner to ensure it appropriately clears specified pixels."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "remove_coordinates.dicom")

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

        inputpixels[0:1024, 0:1024] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_pixel_cleaner_remove_coordinates_dicom_file(self):
        """Test the pixel cleaner to ensure it appropriately clears specified pixels."""
        dicom_file_data = utils.dcmread(get_file(self.dataset))
        inputpixels = deepcopy(dicom_file_data.pixel_array)

        deid_path = os.path.join(self.deidpath, "remove_coordinates.dicom")
        deid = DeidRecipe(deid_path)

        out = has_burned_pixels(dicom_file_data, deid=deid)
        self.assertTrue(out["flagged"])

        outputpixels = clean_pixel_data(dicom_file=dicom_file_data, results=out)

        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[0:1024, 0:1024] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_pixel_cleaner_remove_all(self):
        """Test the pixel cleaner to ensure it appropriately clears all pixels."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "remove_all.dicom")

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

    def test_pixel_cleaner_keepcoordinates_noaction(self):
        """Test the pixel cleaner to ensure that a keepcoordinates with no removecoordinates has no impact on the pixels."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "keepcoordinates_noaction.dicom")

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
        self.assertTrue(compare.all())

    def test_pixel_cleaner_keepcoordinates(self):
        """Test the pixel cleaner to ensure that a keepcoordinates retains appropriate pixels."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "keepcoordinates.dicom")

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

        compare = inputpixels[0:1024, 0:1024] == outputpixels[0:1024, 0:1024]
        self.assertTrue(compare.all())

    def test_pixel_cleaner_remove_multiple(self):
        """Test the pixel cleaner to ensure that multiple remove coordinates in the same filter remove the appropriate pixels."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "remove_coordinates_multiple.dicom")

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

        inputpixels[0:10, 0:10] = 0
        inputpixels[10:20, 10:20] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_pixel_cleaner_remove_multiple_filters(self):
        """Test the pixel cleaner to ensure that multiple remove coordinates in different filters remove the appropriate pixels."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "remove_coordinates_multiple_filters.dicom")

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

        inputpixels[0:10, 0:10] = 0
        inputpixels[10:20, 10:20] = 0
        compare = inputpixels == outputpixels
        self.assertTrue(compare.all())

    def test_pixel_cleaner_keepcoordinates_from(self):
        """Test the pixel cleaner to ensure that multiple keep coordinates retrieved from a dicom field are appropriately retained."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "keepcoordinates_from.dicom")

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

        inputpixels[1000:2000, 0:1000] = 0
        inputpixels[0:1000, 1000:2000] = 0

        compare = inputpixels[0:2000, 0:2000] == outputpixels[0:2000, 0:2000]
        self.assertTrue(compare.all())


if __name__ == "__main__":
    unittest.main()
