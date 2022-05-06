#!/usr/bin/env python

"""
Testing deid provided functions

Copyright (c) 2020-2022 Vanessa Sochat

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
import re

from deid.utils import get_installdir
from deid.data import get_dataset
from deid.dicom.parser import DicomParser
from deid.tests.common import get_file, get_same_file, create_recipe

uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"


class TestDicomFuncs(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_user_provided_func(self):
        """
        %header
        REMOVE ALL func:myfunction
        """
        print("Test user provided func")
        dicom_file = get_file(self.dataset)

        def myfunction(dicom, value, field, item):
            from pydicom.tag import Tag

            tag = Tag(field.element.tag)

            if tag in dicom:
                currentvalue = str(dicom.get(tag).value).lower()
                if "hibbard" in currentvalue:
                    return True
                return False

        actions = [{"action": "REMOVE", "field": "ALL", "value": "func:myfunction"}]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.define("myfunction", myfunction)
        parser.parse()

        self.assertEqual(160, len(parser.dicom))
        with self.assertRaises(KeyError):
            parser.dicom["ReferringPhysicianName"].value
        with self.assertRaises(KeyError):
            parser.dicom["PhysiciansOfRecord"].value
        with self.assertRaises(KeyError):
            parser.dicom["RequestingPhysician"].value
        with self.assertRaises(KeyError):
            parser.dicom["00331019"].value

    def test_basic_uuid(self):
        """
        %header
        REPLACE ReferringPhysicianName deid_func:basic_uuid
        """
        print("Test deid_func:basic_uuid")

        dicom_file = get_file(self.dataset)
        actions = [
            {
                "action": "REPLACE",
                "field": "ReferringPhysicianName",
                "value": "deid_func:basic_uuid",
            }
        ]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        # 8905e722-8103-4823-bc8f-8aed967e272d
        print(parser.dicom["ReferringPhysicianName"].value)
        assert re.search(uuid_regex, str(parser.dicom["ReferringPhysicianName"].value))

    def test_pydicom_uuid(self):
        """
        %header
        REPLACE ReferringPhysicianName deid_func:pydicom_uuid
        """
        print("Test deid_func:pydicom_uuid")

        dicom_file = get_file(self.dataset)
        actions = [
            {
                "action": "REPLACE",
                "field": "ReferringPhysicianName",
                "value": "deid_func:pydicom_uuid",
            }
        ]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        # Randomness is anything, but should be all numbers
        print(parser.dicom["ReferringPhysicianName"].value)
        name = str(parser.dicom["ReferringPhysicianName"].value)
        assert re.search("([0-9]|.)+", name)

        # This is the pydicom default, and we default to stable remapping
        assert (
            name == "2.25.39101090714049289438893821151950032074223798085258118413707"
        )

        # Add a custom prefix
        # must match '^(0|[1-9][0-9]*)(\\.(0|[1-9][0-9]*))*\\.$'
        actions = [
            {
                "action": "REPLACE",
                "field": "ReferringPhysicianName",
                "value": "deid_func:pydicom_uuid prefix=1.55.",
            }
        ]
        recipe = create_recipe(actions)
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        # Randomness is anything, but should be all numbers
        print(parser.dicom["ReferringPhysicianName"].value)
        name = str(parser.dicom["ReferringPhysicianName"].value)
        assert name.startswith("1.55.")

        # This should always be consistent if we use the original as entropy
        dicom_file = get_same_file(self.dataset)
        actions = [
            {
                "action": "REPLACE",
                "field": "ReferringPhysicianName",
                "value": "deid_func:pydicom_uuid stable_remapping=false",
            }
        ]
        recipe = create_recipe(actions)
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        # Randomness is anything, but should be all numbers
        print(parser.dicom["ReferringPhysicianName"].value)
        name = str(parser.dicom["ReferringPhysicianName"].value)
        assert (
            name != "2.25.39101090714049289438893821151950032074223798085258118413707"
        )

    def test_suffix_uuid(self):
        """
        %header
        REPLACE ReferringPhysicianName deid_func:suffix_uuid
        """
        print("Test deid_func:basic_uuid")

        dicom_file = get_file(self.dataset)
        actions = [
            {
                "action": "REPLACE",
                "field": "ReferringPhysicianName",
                "value": "deid_func:suffix_uuid",
            }
        ]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        # 8905e722-8103-4823-bc8f-8aed967e272d
        print(parser.dicom["ReferringPhysicianName"].value)
        name = str(parser.dicom["ReferringPhysicianName"].value)
        assert "referringphysicianname-" in name
        assert re.search(uuid_regex, name)

    def test_dicom_uuid(self):
        """
        %header
        REPLACE ReferringPhysicianName deid_func:suffix_uuid org=myorg
        """
        print("Test deid_func:dicom_uuid")

        dicom_file = get_file(self.dataset)
        actions = [
            {
                "action": "REPLACE",
                "field": "ReferringPhysicianName",
                "value": "deid_func:dicom_uuid org_root=1.2.826.0.1.3680043.10.188",
            }
        ]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        # 8905e722-8103-4823-bc8f-8aed967e272d
        print(parser.dicom["ReferringPhysicianName"].value)
        name = str(parser.dicom["ReferringPhysicianName"].value)
        assert "1.2.826.0.1.3680043.10.188" in name
        assert len(name) == 64

    def test_dicom_jitter(self):
        """RECIPE RULE
        REPLACE AcquisitionDate deid_func:jitter days=1
        """
        print("Test deid_func:jitter")

        dicom_file = get_file(self.dataset)
        actions = [
            {
                "action": "REPLACE",
                "field": "AcquisitionDate",
                "value": "deid_func:jitter days=1",
            }
        ]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)

        original_date = parser.dicom.AcquisitionDate
        assert original_date == "20230101"
        parser.parse()
        jittered_date = str(parser.dicom["AcquisitionDate"].value)
        assert jittered_date == "20230102"

        # Add a day and a year
        actions = [
            {
                "action": "REPLACE",
                "field": "AcquisitionDate",
                "value": "deid_func:jitter days=1 years=1",
            }
        ]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()
        jittered_date = str(parser.dicom["AcquisitionDate"].value)
        assert jittered_date == "20240102"


if __name__ == "__main__":
    unittest.main()
