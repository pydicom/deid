#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
