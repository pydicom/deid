#!/usr/bin/env python

"""
Test DICOM Cleaner

Copyright (c) 2016-2021 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import unittest
import tempfile
import shutil
import os
import numpy as np

from deid.utils import get_installdir
from deid.data import get_dataset
from deid.tests.common import get_file
from pydicom import read_file

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

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
        inputpixels = inputfile.pixel_array
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

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
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

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
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

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
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

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
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

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
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

        outputfile = read_file(cleanedfile)
        outputpixels = outputfile.pixel_array

        inputfile = read_file(dicom_file)
        inputpixels = inputfile.pixel_array
        compare = inputpixels == outputpixels
        self.assertFalse(compare.all())

        inputpixels[1000:2000, 0:1000] = 0
        inputpixels[0:1000, 1000:2000] = 0

        compare = inputpixels[0:2000, 0:2000] == outputpixels[0:2000, 0:2000]
        self.assertTrue(compare.all())


if __name__ == "__main__":
    unittest.main()
