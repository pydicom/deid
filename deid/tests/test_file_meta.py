#!/usr/bin/env python

"""
Test file meta

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
import json
import os

from deid.utils import get_installdir
from deid.data import get_dataset
from deid.dicom.parser import DicomParser
from deid.dicom import get_identifiers, replace_identifiers
from pydicom import read_file
from pydicom.sequence import Sequence

from deid.tests.common import create_recipe, get_file

from collections import OrderedDict


class TestDicom(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.dataset = get_dataset("animals")

    def test_replace_filemeta(self):
        """RECIPE RULE
        REPLACE MediaStorageSOPInstanceUID new-id
        """
        print("Test replace filemeta")
        dicom_file = get_file(self.dataset)

        actions = [
            {
                "action": "REPLACE",
                "field": "MediaStorageSOPInstanceUID",
                "value": "new-id",
            }
        ]
        recipe = create_recipe(actions)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        self.assertEqual(
            "new-id", result[0].file_meta["MediaStorageSOPInstanceUID"].value
        )

    def test_replace_protected_field(self):
        """RECIPE RULE
        REPLACE TransferSyntaxUID new-id
        """
        print("Test replace filemeta")
        dicom_file = get_file(self.dataset)

        actions = [
            {
                "action": "REPLACE",
                "field": "TransferSyntaxUID",
                "value": "new-id",
            }
        ]
        recipe = create_recipe(actions)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )

        # Here the field is protected by default
        self.assertEqual(1, len(result))
        self.assertNotEqual("new-id", result[0].file_meta.TransferSyntaxUID)

        # Now we will unprotect it!
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
            disable_skip=True,
        )

        # Here the field is protected by default
        self.assertEqual(1, len(result))
        self.assertEqual("new-id", result[0].file_meta.TransferSyntaxUID)


if __name__ == "__main__":
    unittest.main()
