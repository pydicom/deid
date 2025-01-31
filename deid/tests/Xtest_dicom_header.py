#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom import utils
from deid.utils import get_installdir


class TestDicomHeader(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("dicom-cookies")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_get_fields(self):
        print("Case 1: Test get fields from dataset")
        from deid.dicom.header import get_fields

        dicom = get_dicom(self.dataset)
        fields = get_fields(dicom)
        self.assertEqual(len(fields), 28)
        self.assertTrue("PatientID" in fields)

    def test_get_identifiers(self):
        print("Testing deid.dicom get_identifiers")
        from deid.dicom import get_identifiers

        dicom_files = get_dicom(self.dataset, return_dir=True)
        ids = get_identifiers(dicom_files)
        self.assertTrue(len(ids) == 1)
        self.assertTrue(isinstance(ids, dict))
        self.assertEqual(len(ids["cookie-47"]), 7)

    def test_replace_identifiers(self):
        print("Testing deid.dicom replace_identifiers")

        from deid.dicom import get_identifiers, replace_identifiers

        dicom_files = get_dicom(self.dataset, return_dir=True)
        ids = get_identifiers(dicom_files)

        # Before blanking, 28 fields don't have blanks
        notblanked = utils.dcmread(dicom_files[0])
        notblanked_fields = [
            x for x in notblanked.dir() if notblanked.get(x) != ""
        ]  # 28
        self.assertTrue(len(notblanked_fields) == 28)

        updated_files = replace_identifiers(dicom_files, ids, output_folder=self.tmpdir)

        # After replacing only 9 don't have blanks
        blanked = utils.dcmread(updated_files[0])
        blanked_fields = [x for x in blanked.dir() if blanked.get(x) != ""]
        self.assertTrue(len(blanked_fields) == 9)


def get_dicom(dataset, return_dir=False):
    """helper function to load a dicom"""

    from deid.dicom import get_files

    dicom_files = get_files(dataset)
    if return_dir:
        return list(dicom_files)
    return utils.dcmread(next(dicom_files))


if __name__ == "__main__":
    unittest.main()
