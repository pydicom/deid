#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import deid.main
from deid.data import get_dataset
from deid.dicom import get_files, utils
from deid.utils import get_installdir


class TestMainAction(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.example = list(get_files(self.dataset))[0]
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    @patch(
        "sys.argv",
        "deid --outfolder out/ --overwrite identifiers --action all --input ./".split(
            " "
        ),
    )
    def test_deidmain_write_identifiers(self):
        """
        Run example command line call. Expect saved output.
        """
        os.chdir(self.tmpdir)
        # Confirm input data has value that will be scrubbed.
        self.assertNotEqual(None, utils.dcmread(self.example).get("StudyTime"))

        shutil.copyfile(self.example, self.tmpdir + "/example.dicom")
        os.makedirs("out/")
        deid.main.main()

        # Confirm new file was created
        outfile = utils.dcmread("out/example.dicom")

        # Confirm new file was srubbed
        self.assertEqual(None, outfile.get("StudyTime"))

    @patch(
        "sys.argv",
        "deid --outfolder out/ pixels --deid deid.cfg --input ./".split(" "),
    )
    def test_deidmain_clean_pixels(self):
        """
        Run example command line call to clean pixels
        """
        os.chdir(self.tmpdir)
        shutil.copyfile(self.example, self.tmpdir + "/example.dicom")
        # Confirm input data has value that will be scrubbed.
        indcm = utils.dcmread(self.tmpdir + "/example.dicom")
        self.assertEqual(indcm.pixel_array.shape, (456, 510, 3))
        censor_area = indcm.pixel_array[0:250, 0:100, :]  # y,x,z
        # all voxels in region to be scrubbed are valued. lucky us
        self.assertEqual(np.count_nonzero(censor_area != 0), 75000)

        with open(self.tmpdir + "/deid.cfg", "w") as f:
            f.write(
                """FORMAT dicom

%filter greylist

LABEL Censor Top Left
contains SOPInstanceUID .
  coordinates 0,0,100,250
"""
            )

        os.makedirs("out/")
        deid.main.main()

        outfile = utils.dcmread("out/example.dicom")

        # Confirm we changed pixel data
        self.assertTrue(np.any(indcm.pixel_array != outfile.pixel_array))
        # Confirm censor area is all zeros
        # 30126 but expect 75000
        zero_cnt = np.count_nonzero(outfile.pixel_array[0:250, 0:100, :] == 0)
        self.assertEqual(zero_cnt, 100 * 250 * 3)  # 75000


if __name__ == "__main__":
    unittest.main()
