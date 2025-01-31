#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.tests.common import get_dicom
from deid.utils import get_installdir

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
        from deid.dicom.fields import DicomField
        from deid.dicom.tags import get_tag

        dicom = get_dicom(self.dataset)

        print("Testing test_jitter_timestamp")

        print("Case 1: Testing jitter_timestamp with DICOM Date (DA)")
        name = "StudyDate"
        tag = get_tag(name)
        dicom.StudyDate = "20131210"
        dicom.data_element(name).VR = "DA"
        field = DicomField(dicom.data_element(name), name, str(tag["tag"]))
        actual = jitter_timestamp(field, 10)
        expected = "20131220"
        self.assertEqual(actual, expected)

        print("Case 2: Testing with DICOM timestamp (DT)")
        name = "AcquisitionDateTime"
        tag = get_tag(name)
        dicom.AcquisitionDateTime = "20131210081530"
        dicom.data_element(name).VR = "DT"
        field = DicomField(dicom.data_element(name), name, str(tag["tag"]))
        actual = jitter_timestamp(field, 10)
        expected = "20131220081530.000000"
        self.assertEqual(actual, expected)

        print("Case 3: Testing with non-standard DICOM date (DA)")
        name = "StudyDate"
        tag = get_tag(name)
        dicom.StudyDate = "20131210"
        dicom.data_element(name).VR = "DA"
        field = DicomField(dicom.data_element(name), name, str(tag["tag"]))
        actual = jitter_timestamp(field, 10)
        expected = "20131220"
        self.assertEqual(actual, expected)

        print("Case 4: Testing negative jitter value")
        name = "StudyDate"
        tag = get_tag(name)
        dicom.StudyDate = "20131210"
        field = DicomField(dicom.data_element(name), name, str(tag["tag"]))
        actual = jitter_timestamp(field, -5)
        expected = "20131205"
        self.assertEqual(actual, expected)

        print("Case 5: Testing with empty field")
        name = "StudyDate"
        tag = get_tag(name)
        dicom.StudyDate = ""
        field = DicomField(dicom.data_element(name), name, str(tag["tag"]))
        actual = jitter_timestamp(field, 10)
        expected = None
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
