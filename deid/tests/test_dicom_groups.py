#!/usr/bin/env python

"""
Testing groups for a deid recipe (values and fields)

Copyright (c) 2020-2021 Vanessa Sochat

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
from deid.dicom.parser import DicomParser
from deid.tests.common import get_file, get_dicom


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
        fields = get_fields(dicom)

        # Test split action
        actions = [
            {"action": "SPLIT", "field": "PatientID", "value": 'by="^";minlength=4'}
        ]
        expected_names = dicom.get("PatientID").split("^")
        actual = extract_values_list(dicom, actions)
        self.assertEqual(actual, expected_names)

        # Test field action
        actions = [{"action": "FIELD", "field": "startswith:Operator"}]
        expected_operator = [
            x.element.value
            for uid, x in fields.items()
            if x.element.keyword.startswith("Operator")
        ]
        actual = extract_values_list(dicom, actions)
        self.assertEqual(actual, expected_operator)

        print("Test deid.dicom.groups extract_fields_list")
        actions = [{"action": "FIELD", "field": "contains:Instance"}]
        expected = {
            uid: x for uid, x in fields.items() if "Instance" in x.element.keyword
        }
        actual = extract_fields_list(dicom, actions)
        for uid in expected:
            assert uid in actual

        # Get identifiers for file
        ids = get_identifiers(dicom)
        self.assertTrue(isinstance(ids, dict))

        # Add keys to be used for replace to ids - these first are for values
        parser = DicomParser(dicom, recipe=self.deid)
        parser.define("cookie_names", expected_names)
        parser.define("operator_names", expected_operator)

        # This is for fields
        parser.define("instance_fields", expected)
        parser.define("id", "new-cookie-id")
        parser.define("source_id", "new-operator-id")
        parser.parse()

        # Were the changes made?
        assert parser.dicom.get("PatientID") == "new-cookie-id"
        assert parser.dicom.get("OperatorsName") == "new-operator-id"

        # Instance fields should be removed based on recipe
        for uid, field in parser.lookup["instance_fields"].items():
            self.assertTrue(field.element.keyword not in parser.dicom)

        # Start over
        dicom = get_dicom(self.dataset)

        # We need to provide ids with variables "id" and "source_id"
        ids = {dicom.filename: {"id": "new-cookie-id", "source_id": "new-operator-id"}}

        # Returns list of updated dicom, since save is False
        replaced = replace_identifiers(dicom, save=False, deid=self.deid, ids=ids)
        cleaned = replaced.pop()

        self.assertEqual(cleaned.get("PatientID"), "new-cookie-id")
        self.assertEqual(cleaned.get("OperatorsName"), "new-operator-id")


if __name__ == "__main__":
    unittest.main()
