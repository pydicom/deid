#!/usr/bin/env python

"""
Testing groups for a deid recipe (values and fields)

Copyright (c) 2020 Vanessa Sochat

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
from deid.config import DeidRecipe
from deid.dicom.fields import get_fields
from deid.dicom import get_identifiers, replace_identifiers


class TestDicomGroups(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom-groups" % self.pwd)
        self.dataset = get_dataset("dicom-cookies")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_extract_groups(self):
        print("Test deid.dicom.groups extract_values_list")
        from deid.dicom.groups import extract_values_list, extract_fields_list

        dicom = get_dicom(self.dataset)
        fields = get_fields(dicom)  # removes empty / null

        # Test split action
        actions = [
            {"action": "SPLIT", "field": "PatientID", "value": 'by="^";minlength=4'}
        ]
        expected_names = dicom.get("PatientID").split("^")
        actual = extract_values_list(dicom, actions)
        self.assertEqual(actual, expected_names)

        # Test field action
        actions = [{"action": "FIELD", "field": "startswith:Operator"}]
        expected_operator = [dicom.get(x) for x in fields if x.startswith("Operator")]
        actual = extract_values_list(dicom, actions)
        self.assertEqual(actual, expected_operator)

        print("Test deid.dicom.groups extract_fields_list")
        actions = [{"action": "FIELD", "field": "contains:Instance"}]
        expected = [x for x in fields if "Instance" in x]
        actual = extract_fields_list(dicom, actions)
        self.assertEqual(actual, expected)

        # Get identifiers for file
        ids = get_identifiers(dicom)
        self.assertTrue(isinstance(ids, dict))

        # Add keys to be used for replace to ids - these first are for values
        ids[dicom.filename]["cookie_names"] = expected_names
        ids[dicom.filename]["operator_names"] = expected_operator

        # This is for fields
        ids[dicom.filename]["instance_fields"] = expected
        ids[dicom.filename]["id"] = "new-cookie-id"
        ids[dicom.filename]["source_id"] = "new-operator-id"

        replaced = replace_identifiers(dicom, ids=ids, save=False, deid=self.deid)
        cleaned = replaced.pop()
        self.assertEqual(cleaned.get("PatientID"), "new-cookie-id")
        self.assertEqual(cleaned.get("OperatorsName"), "new-operator-id")

        # Currently we don't well handle tag types, so we convert to string
        for field in expected_operator:
            self.assertTrue(str(field) not in cleaned)


def get_dicom(dataset):
    """helper function to load a dicom
    """
    from deid.dicom import get_files
    from pydicom import read_file

    dicom_files = get_files(dataset)
    return read_file(next(dicom_files))


if __name__ == "__main__":
    unittest.main()
