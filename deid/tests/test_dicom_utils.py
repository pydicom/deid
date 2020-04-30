#!/usr/bin/env python

"""
Test dicom utils

The MIT License (MIT)

Copyright (c) 2016-2020 Vanessa Sochat

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
import json
import os

from deid.utils import get_installdir
from deid.data import get_dataset

global generate_uid


class TestDicomUtils(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("dicom-cookies")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_get_files(self):
        print("Test test_get_files")
        print("Case 1: Test get files from dataset")
        from deid.dicom import get_files
        from deid.config import load_deid

        found = 0
        for dicom_file in get_files(self.dataset):
            found += 1
        expected = 7
        self.assertEqual(found, expected)

        print("Case 2: Ask for files from empty folder")
        found = 0
        for dicom_file in get_files(self.tmpdir):
            found += 1
        expected = 0
        self.assertEqual(found, expected)

    def test_get_files_as_list(self):
        print("Test test_get_files_as_list")
        print("Case 1: Test get files from dataset")
        from deid.dicom import get_files
        from deid.config import load_deid

        dicom_files = list(get_files(self.dataset))
        found = len(dicom_files)
        expected = 7
        self.assertEqual(found, expected)

        print("Case 2: Ask for files from empty folder")
        dicom_files = list(get_files(self.tmpdir))
        found = len(dicom_files)
        expected = 0
        self.assertEqual(found, expected)

    def test_jitter_timestamp(self):

        from deid.dicom.actions import jitter_timestamp

        dicom = get_dicom(self.dataset)

        print("Testing test_jitter_timestamp")

        print("Case 1: Testing jitter_timestamp with DICOM Date (DA)")
        dicom.StudyDate = "20131210"
        dicom.data_element("StudyDate").VR = "DA"
        jitter_timestamp(dicom, "StudyDate", 10)
        expected = "20131220"
        self.assertEqual(dicom.StudyDate, expected)

        print("Case 2: Testing with DICOM timestamp (DT)")
        dicom.AcquisitionDateTime = "20131210081530"
        dicom.data_element("AcquisitionDateTime").VR = "DT"
        jitter_timestamp(dicom, "AcquisitionDateTime", 10)
        expected = "20131220081530.000000"
        self.assertEqual(dicom.AcquisitionDateTime, expected)

        print("Case 3: Testing with non-standard DICOM date (DA)")
        dicom.StudyDate = "2013/12/10"
        dicom.data_element("StudyDate").VR = "DA"
        jitter_timestamp(dicom, "StudyDate", 10)
        expected = "20131220"
        self.assertEqual(dicom.StudyDate, expected)

        print("Case 4: Testing negative jitter value")
        dicom.StudyDate = "20131210"
        jitter_timestamp(dicom, "StudyDate", -5)
        expected = "20131205"
        self.assertEqual(dicom.StudyDate, expected)

        print("Case 5: Testing with empty field")
        dicom.StudyDate = expected = ""
        jitter_timestamp(dicom, "StudyDate", 10)
        self.assertEqual(dicom.StudyDate, expected)

        print("Case 6: Testing with nonexistent field")
        del dicom.StudyDate
        jitter_timestamp(dicom, "StudyDate", 10)
        self.assertTrue("StudyDate" not in dicom)


def get_dicom(dataset):
    """helper function to load a dicom
    """
    from deid.dicom import get_files
    from pydicom import read_file

    dicom_files = get_files(dataset)
    return read_file(next(dicom_files))


if __name__ == "__main__":
    unittest.main()
