#!/usr/bin/env python

"""
Test replace_identifiers

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
from deid.tests.common import create_recipe, get_file
from pydicom import read_file
from pydicom.sequence import Sequence

from collections import OrderedDict

global generate_uid


class TestDicom(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_add_private_constant(self):
        """RECIPE RULE
        ADD 11112221 SIMPSON
        """
        print("Test add private tag constant value")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "ADD", "field": "11112221", "value": "SIMPSON"}]
        recipe = create_recipe(actions)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        self.assertEqual("SIMPSON", result[0]["11112221"].value)

    def test_add_private_constant_save_true(self):
        """RECIPE RULE
        ADD 11112221 SIMPSON
        """
        print("Test add private tag constant value")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "ADD", "field": "11112221", "value": "SIMPSON"}]
        recipe = create_recipe(actions)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
            output_folder=self.tmpdir,
        )
        outputfile = read_file(result[0])

        self.assertEqual(1, len(result))
        self.assertEqual("SIMPSON", outputfile["11112221"].value)

    def test_add_public_constant(self):
        """RECIPE RULE
        ADD PatientIdentityRemoved Yeppers!
        """

        print("Test add public tag constant value")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yeppers!"}
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
        self.assertEqual("Yeppers!", result[0].PatientIdentityRemoved)

    def test_replace_with_constant(self):
        """RECIPE RULE
        REPLACE AccessionNumber 987654321
        REPLACE 00190010 NEWVALUE!
        """

        print("Test replace tags with constant values")
        dicom_file = get_file(self.dataset)

        newfield1 = "AccessionNumber"
        newvalue1 = "987654321"
        newfield2 = "00190010"
        newvalue2 = "NEWVALUE!"

        actions = [
            {"action": "REPLACE", "field": newfield1, "value": newvalue1},
            {"action": "REPLACE", "field": newfield2, "value": newvalue2},
        ]
        recipe = create_recipe(actions)

        # Create a DicomParser to easily find fields
        parser = DicomParser(dicom_file)
        parser.parse()

        # The first in the list is the highest level
        field1 = list(parser.find_by_name(newfield1).values())[0]
        field2 = list(parser.find_by_name(newfield2).values())[0]

        self.assertNotEqual(newvalue1, field1.element.value)
        self.assertNotEqual(newvalue2, field2.element.value)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )

        self.assertEqual(1, len(result))
        self.assertEqual(newvalue1, result[0][newfield1].value)
        self.assertEqual(newvalue2, result[0][newfield2].value)

    def test_jitter_replace_compounding(self):
        """RECIPE RULE
        JITTER AcquisitonDate 1
        REPLACE AcquisitionDate 20210330
        """

        print("Test replace tags with constant values")
        dicom_file = get_file(self.dataset)

        newfield1 = "AcquisitionDate"
        newvalue1 = "20210330"

        actions = [
            {"action": "JITTER", "field": newfield1, "value": "1"},
            {"action": "REPLACE", "field": newfield1, "value": newvalue1},
        ]
        recipe = create_recipe(actions)

        inputfile = read_file(dicom_file)
        currentValue = inputfile[newfield1].value

        self.assertNotEqual(newvalue1, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = read_file(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(newvalue1, outputfile[newfield1].value)

    def test_remove(self):
        """RECIPE RULE
        REMOVE InstitutionName
        REMOVE 00190010
        """

        print("Test remove of public and private tags")
        dicom_file = get_file(self.dataset)

        field1name = "InstitutionName"
        field2name = "00190010"

        actions = [
            {"action": "REMOVE", "field": field1name},
            {"action": "REMOVE", "field": field2name},
        ]
        recipe = create_recipe(actions)
        dicom = read_file(dicom_file)

        # Create a DicomParser to easily find fields
        parser = DicomParser(dicom_file)
        parser.parse()

        # The first in the list is the highest level
        field1 = list(parser.find_by_name(field1name).values())[0]
        field2 = list(parser.find_by_name(field2name).values())[0]

        self.assertIsNotNone(field1.element.value)
        self.assertIsNotNone(field2.element.value)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )

        # Create a DicomParser to easily find fields
        parser = DicomParser(result[0])
        parser.parse()

        # Removed means we don't find them
        assert not parser.find_by_name(field1name)
        assert not parser.find_by_name(field2name)

        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            check1 = result[0][field1name].value
        with self.assertRaises(KeyError):
            check2 = result[0][field2name].value

    def test_add_tag_variable(self):
        """RECIPE RULE
        ADD 11112221 var:myVar
        ADD PatientIdentityRemoved var:myVar
        """

        print("Test add tag constant value from variable")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "ADD", "field": "11112221", "value": "var:myVar"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "var:myVar"},
        ]
        recipe = create_recipe(actions)

        # Method 1, define ids manually
        ids = {dicom_file: {"myVar": "SIMPSON"}}

        result = replace_identifiers(
            dicom_files=dicom_file,
            ids=ids,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        self.assertEqual("SIMPSON", result[0]["11112221"].value)
        self.assertEqual("SIMPSON", result[0]["PatientIdentityRemoved"].value)

    def test_add_tag_variable_save_true(self):
        """RECIPE RULE
        ADD 11112221 var:myVar
        ADD PatientIdentityRemoved var:myVar
        """

        print("Test add tag constant value from variable")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "ADD", "field": "11112221", "value": "var:myVar"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "var:myVar"},
        ]
        recipe = create_recipe(actions)

        # Method 1, define ids manually
        ids = {dicom_file: {"myVar": "SIMPSON"}}

        result = replace_identifiers(
            dicom_files=dicom_file,
            ids=ids,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
            output_folder=self.tmpdir,
        )
        outputfile = read_file(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual("SIMPSON", outputfile["11112221"].value)
        self.assertEqual("SIMPSON", outputfile["PatientIdentityRemoved"].value)

    def test_jitter_date(self):
        # DICOM datatype DA
        """RECIPE RULE
        JITTER StudyDate 1
        """

        print("Test date jitter")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "JITTER", "field": "StudyDate", "value": "1"}]
        recipe = create_recipe(actions)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        self.assertEqual("20230102", result[0]["StudyDate"].value)

    def test_jitter_timestamp(self):
        # DICOM datatype DT
        """RECIPE RULE
        JITTER AcquisitionDateTime 1
        """

        print("Test timestamp jitter")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "JITTER", "field": "AcquisitionDateTime", "value": "1"}]
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
            "20230102011721.621000", result[0]["AcquisitionDateTime"].value
        )

    def test_expanders(self):
        """RECIPE RULES
        REMOVE contains:Collimation
        REMOVE endswith:Diameter
        REMOVE startswith:Exposure
        """

        print("Test contains, endswith, and startswith expanders")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "contains:Collimation"},
            {"action": "REMOVE", "field": "endswith:Diameter"},
            {"action": "REMOVE", "field": "startswith:Exposure"},
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
        self.assertEqual(157, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]["ExposureTime"].value
        with self.assertRaises(KeyError):
            check2 = result[0]["TotalCollimationWidth"].value
        with self.assertRaises(KeyError):
            check3 = result[0]["DataCollectionDiameter"].value

    def test_expander_except(self):
        # Remove all fields except Manufacturer
        """RECIPE RULE
        REMOVE except:Manufacturer
        """

        print("Test except expander")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "REMOVE", "field": "except:Manufacturer"}]
        recipe = create_recipe(actions)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
            disable_skip=True,
        )
        self.assertEqual(1, len(result))
        self.assertEqual(2, len(result[0]))

        self.assertEqual("SIEMENS", result[0]["Manufacturer"].value)
        with self.assertRaises(KeyError):
            check1 = result[0]["ExposureTime"].value
        with self.assertRaises(KeyError):
            check2 = result[0]["TotalCollimationWidth"].value
        with self.assertRaises(KeyError):
            check3 = result[0]["DataCollectionDiameter"].value

    def test_fieldset_remove(self):
        """RECIPE
        %fields field_set1
        FIELD Manufacturer
        FIELD contains:Time
        %header
        REMOVE fields:field_set1
        """

        print("Test public tag fieldset")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "REMOVE", "field": "fields:field_set1"}]
        fields = OrderedDict()
        fields["field_set1"] = [
            {"field": "Manufacturer", "action": "FIELD"},
            {"field": "contains:Collimation", "action": "FIELD"},
        ]

        recipe = create_recipe(actions, fields)

        # Method 1: Use DicomParser
        parser = DicomParser(dicom_file, recipe=recipe)
        number_fields = len(parser.dicom)  # 160
        parser.parse()

        # The number of fields to be removed
        to_remove = len(parser.lookup["field_set1"])

        expected_number = number_fields - to_remove

        # {'field_set1': {'(0008, 0070)': (0008, 0070) Manufacturer                        LO: 'SIEMENS'  [Manufacturer],
        # '(0018, 9306)': (0018, 9306) Single Collimation Width            FD: 1.2  [SingleCollimationWidth],
        # '(0018, 9307)': (0018, 9307) Total Collimation Width             FD: 14.399999999999999  [TotalCollimationWidth]}}

        # Method 2: use replace_identifiers
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        print(len(result[0]))
        self.assertEqual(expected_number, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]["Manufacturer"].value
        with self.assertRaises(KeyError):
            check2 = result[0]["TotalCollimationWidth"].value
        with self.assertRaises(KeyError):
            check3 = result[0]["SingleCollimationWidth"].value

    def test_valueset_remove(self):
        """
        %values value_set1
        FIELD contains:Manufacturer
        SPLIT contains:Physician by="^";minlength=3
        %header REMOVE values:value_set1
        """

        print("Test public tag valueset")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "REMOVE", "field": "values:value_set1"}]
        values = OrderedDict()
        values["value_set1"] = [
            {"field": "contains:Manufacturer", "action": "FIELD"},
            {
                "value": 'by="^";minlength=3',
                "field": "contains:Physician",
                "action": "SPLIT",
            },
        ]
        recipe = create_recipe(actions, values=values)

        # Check that values we want are present using DicomParser
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()
        self.assertTrue("SIEMENS" in parser.lookup["value_set1"])
        self.assertTrue("HIBBARD" in parser.lookup["value_set1"])

        # Perform action
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            check1 = result[0]["00090010"].value
        with self.assertRaises(KeyError):
            check2 = result[0]["Manufacturer"].value
        with self.assertRaises(KeyError):
            check3 = result[0]["PhysiciansOfRecord"].value

    def test_fieldset_remove_private(self):
        """
        %fields field_set2_private
        FIELD 00090010
        FIELD PatientID
        %header
        REMOVE fields:field_set2_private
        """

        print("Test private tag fieldset")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "REMOVE", "field": "fields:field_set2_private"}]
        fields = OrderedDict()
        fields["field_set2_private"] = [
            {"field": "00090010", "action": "FIELD"},
            {"field": "PatientID", "action": "FIELD"},
        ]
        recipe = create_recipe(actions, fields)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()
        self.assertTrue("(0009, 0010)" in parser.lookup["field_set2_private"])
        self.assertTrue("(0010, 0020)" in parser.lookup["field_set2_private"])

        self.assertEqual(162, len(parser.dicom))
        self.assertEqual("SIEMENS CT VA0  COAD", parser.dicom["00190010"].value)
        with self.assertRaises(KeyError):
            check1 = parser.dicom["00090010"].value
        with self.assertRaises(KeyError):
            check2 = parser.dicom["PatientID"].value

    def test_valueset_private(self):
        """
        %values value_set2_private
        FIELD 00311020
        SPLIT 00090010 by=" ";minlength=4
        %header
        REMOVE values:value_set2_private
        """

        print("Test private tag valueset")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "REMOVE", "field": "values:value_set2_private"}]
        values = OrderedDict()
        values["value_set2_private"] = [
            {"field": "00311020", "action": "FIELD"},
            {"value": 'by=" ";minlength=4', "field": "00090010", "action": "SPLIT"},
        ]
        recipe = create_recipe(actions, values=values)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()
        for entry in ["SIEMENS", "M1212121", "DUMMY"]:
            assert entry in parser.lookup["value_set2_private"]

        with self.assertRaises(KeyError):
            check1 = parser.dicom["OtherPatientIDs"].value
        with self.assertRaises(KeyError):
            check2 = parser.dicom["Manufacturer"].value
        with self.assertRaises(KeyError):
            check3 = parser.dicom["00190010"].value

    def test_tag_expanders_taggroup(self):
        # This tests targets the group portion of a tag identifier - 0009 in (0009, 0001)
        """
        %header
        REMOVE contains:0009
        """
        print("Test expanding tag by tag number part (matches group numbers only)")
        dicom_file = get_file(self.dataset)

        actions = [{"action": "REMOVE", "field": "contains:0009"}]
        recipe = create_recipe(actions)
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            check1 = result[0]["00090010"].value

    def test_tag_expanders_midtag(self):
        """REMOVE contains:8103
        Should remove:
        (0008, 103e) Series Description
        """
        dicom_file = get_file(self.dataset)
        actions = [{"action": "REMOVE", "field": "contains:8103"}]
        recipe = create_recipe(actions)

        # Ensure tag is present before removal
        dicom = read_file(dicom_file)
        assert "0008103e" in dicom

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        assert "0008103e" not in result[0]

    def test_tag_expanders_tagelement(self):
        # includes public and private, groups and element numbers
        """
        %header
        REMOVE contains:0010
        """
        print(
            "Test expanding tag by tag number part (matches groups and element numbers)"
        )
        dicom_file = get_file(self.dataset)

        actions = [{"action": "REMOVE", "field": "contains:0010"}]
        recipe = create_recipe(actions)
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
            disable_skip=True,
        )
        self.assertEqual(1, len(result))
        self.assertEqual(139, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]["00090010"].value
        with self.assertRaises(KeyError):
            check2 = result[0]["PatientID"].value

    def test_remove_all_func(self):
        """
        %header
        REMOVE ALL func:contains_hibbard
        """
        print("Test tag removal by")
        dicom_file = get_file(self.dataset)

        def contains_hibbard(dicom, value, field, item):
            from pydicom.tag import Tag

            tag = Tag(field.element.tag)

            if tag in dicom:
                currentvalue = str(dicom.get(tag).value).lower()
                if "hibbard" in currentvalue:
                    return True
                return False

        actions = [
            {"action": "REMOVE", "field": "ALL", "value": "func:contains_hibbard"}
        ]
        recipe = create_recipe(actions)

        # Create a parser, define function for it
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.define("contains_hibbard", contains_hibbard)
        parser.parse()

        self.assertEqual(160, len(parser.dicom))
        with self.assertRaises(KeyError):
            check1 = parser.dicom["ReferringPhysicianName"].value
        with self.assertRaises(KeyError):
            check2 = parser.dicom["PhysiciansOfRecord"].value
        with self.assertRaises(KeyError):
            check3 = parser.dicom["RequestingPhysician"].value
        with self.assertRaises(KeyError):
            check4 = parser.dicom["00331019"].value

    def test_remove_all_keep_field_compounding_should_keep(self):
        """
        %header
        REMOVE ALL
        KEEP StudyDate
        ADD PatientIdentityRemoved Yes
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "ALL"},
            {"action": "KEEP", "field": "StudyDate"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yes"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertEqual("Yes", parser.dicom["PatientIdentityRemoved"].value)
        self.assertIsNotNone(parser.dicom["PixelData"])
        self.assertIsNotNone(parser.dicom["StudyDate"])
        self.assertEqual("20230101", parser.dicom["StudyDate"].value)

    def test_remove_except_field_keep_other_field_compounding_should_keep(self):
        """
        %header
        REMOVE ALL
        ADD PatientIdentityRemoved Yes
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "except:Manufacturer"},
            {"action": "KEEP", "field": "StudyDate"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yes"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertEqual("Yes", parser.dicom["PatientIdentityRemoved"].value)
        self.assertIsNotNone(parser.dicom["PixelData"])
        self.assertIsNotNone(parser.dicom["Manufacturer"])
        self.assertIsNotNone(parser.dicom["ManufacturerModelName"])
        self.assertIsNotNone(parser.dicom["StudyDate"])

    def test_remove_all_add_field_compounding_should_add(self):
        """
        %header
        REMOVE ALL
        ADD PatientIdentityRemoved Yes
        ADD StudyDate 19700101
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "ALL"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yes"},
            {"action": "ADD", "field": "StudyDate", "value": "19700101"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertEqual("Yes", parser.dicom["PatientIdentityRemoved"].value)
        self.assertIsNotNone(parser.dicom["PixelData"])
        self.assertEqual("19700101", parser.dicom["StudyDate"].value)

    def test_remove_all_blank_field_compounding_should_remove(self):
        """
        %header
        REMOVE ALL
        ADD PatientIdentityRemoved Yes
        BLANK StudyDate
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "ALL"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yes"},
            {"action": "BLANK", "field": "StudyDate"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertEqual("Yes", parser.dicom["PatientIdentityRemoved"].value)
        self.assertIsNotNone(parser.dicom["PixelData"])
        with self.assertRaises(KeyError):
            check3 = parser.dicom["StudyDate"].value

    def test_blank_field_keep_field_compounding_should_keep(self):
        """
        %header
        ADD PatientIdentityRemoved Yes
        BLANK StudyDate
        KEEP StudyDate
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yes"},
            {"action": "BLANK", "field": "StudyDate"},
            {"action": "KEEP", "field": "StudyDate"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertEqual("Yes", parser.dicom["PatientIdentityRemoved"].value)
        self.assertIsNotNone(parser.dicom["PixelData"])
        self.assertEqual("20230101", parser.dicom["StudyDate"].value)

    def test_remove_keep_add_field_compounding_should_add(self):
        """
        %header
        REMOVE ALL
        KEEP StudyDate
        ADD StudyDate 19700101
        ADD PatientIdentityRemoved Yes
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "ALL"},
            {"action": "KEEP", "field": "StudyDate"},
            {"action": "ADD", "field": "StudyDate", "value": "19700101"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yes"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertEqual("Yes", parser.dicom["PatientIdentityRemoved"].value)
        self.assertIsNotNone(parser.dicom["PixelData"])
        self.assertEqual("19700101", parser.dicom["StudyDate"].value)

    def test_remove_field_keep_same_field_compounding_should_keep(self):
        """
        %header
        REMOVE StudyDate
        KEEP StudyDate
        ADD PatientIdentityRemoved Yes
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "StudyDate"},
            {"action": "KEEP", "field": "StudyDate"},
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yes"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertEqual("Yes", parser.dicom["PatientIdentityRemoved"].value)
        self.assertIsNotNone(parser.dicom["PixelData"])
        self.assertEqual("20230101", parser.dicom["StudyDate"].value)

    def test_remove_except_is_acting_as_substring(self):
        """
        %header
        REMOVE except:Manufacturer
        """
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "except:Manufacturer"},
        ]
        recipe = create_recipe(actions)

        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()

        self.assertIsNotNone(parser.dicom["Manufacturer"])
        self.assertIsNotNone(parser.dicom["ManufacturerModelName"])

    def test_strip_sequences(self):
        """
        Testing strip sequences: Checks to ensure that the strip_sequences removes all tags of type
        sequence.  Since sequence removal relies on dicom.iterall(), nested sequences previously
        caused exceptions to be thrown when child (or duplicate) sequences existed within the header.

        %header
        ADD PatientIdentityRemoved Yeppers!
        """
        print("Test strip_sequences")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yeppers!"}
        ]
        recipe = create_recipe(actions)
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=True,
        )
        self.assertEqual(1, len(result))
        self.assertEqual(156, len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]["00081110"].value
        for tag in result[0]:
            self.assertFalse(isinstance(tag.value, Sequence))

    def test_nested_replace(self):
        """
        Fields are read into a dictionary lookup that should index back to the
        correct data element. We add this test to ensure this is happening,
        meaning that a replace action to a particular contains: string changes
        both top level and nested fields.

        %header

        REPLACE contains:StudyInstanceUID var:new_val
        """
        print("Test nested_replace")
        dicom_file = get_file(self.dataset)

        actions = [
            {
                "action": "REPLACE",
                "field": "contains:StudyInstanceUID",
                "value": "var:new_val",
            }
        ]
        recipe = create_recipe(actions)

        items = get_identifiers([dicom_file])
        for item in items:
            items[item]["new_val"] = "modified"

        result = replace_identifiers(
            dicom_files=dicom_file,
            ids=items,
            deid=recipe,
            save=False,
        )
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].StudyInstanceUID, "modified")
        self.assertEqual(
            result[0].RequestAttributesSequence[0].StudyInstanceUID, "modified"
        )

    def test_jitter_compounding(self):
        """
        Testing jitter compounding: Checks to ensure that multiple jitter rules applied to the same field result
        in both rules being applied. While in practice this may be somewhat of a nonsensical use case when large recipes
        exist multiple rules may inadvertently be defined.  In prior versions of pydicom/deid rules were additive and
        recipes are built in that manner.  This test ensures consistency with prior versions.

        %header
        JITTER StudyDate 1
        JITTER StudyDate 2
        """
        print("Test jitter compounding")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "JITTER", "field": "StudyDate", "value": "1"},
            {"action": "JITTER", "field": "StudyDate", "value": "2"},
        ]
        recipe = create_recipe(actions)
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=True,
        )

        self.assertEqual(1, len(result))
        self.assertEqual(155, len(result[0]))
        self.assertEqual("20230104", result[0]["StudyDate"].value)

    def test_addremove_compounding(self):
        """
        Testing add/remove compounding: Checks to ensure that multiple rules applied to the same field result
        in both rules being applied. While in practice this may be somewhat of a nonsensical use case when large recipes
        exist multiple rules may inadvertently be defined.  In prior versions of pydicom/deid rules were additive and
        recipes are built in that manner.  This test ensures consistency with prior versions.

        %header
        ADD PatientIdentityRemoved Yeppers!
        REMOVE PatientIdentityRemoved
        """
        print("Test addremove compounding")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "ADD", "field": "PatientIdentityRemoved", "value": "Yeppers!"},
            {"action": "REMOVE", "field": "PatientIdentityRemoved"},
        ]
        recipe = create_recipe(actions)
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=True,
        )

        self.assertEqual(1, len(result))
        self.assertEqual(155, len(result[0]))
        with self.assertRaises(KeyError):
            willerror = result[0]["PatientIdentityRemoved"].value

    def test_removeadd_compounding(self):
        """
        Testing remove/add compounding: Checks to ensure that multiple rules applied to the same field result
        in both rules being applied. While in practice this may be somewhat of a nonsensical use case when large recipes
        exist multiple rules may inadvertently be defined.  In prior versions of pydicom/deid rules were additive and
        recipes are built in that manner.  This test ensures consistency with prior versions.

        %header
        REMOVE StudyDate
        ADD StudyDate 20200805
        """
        print("Test remove/add compounding")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": "PatientID"},
            {"action": "ADD", "field": "PatientID", "value": "123456"},
        ]
        recipe = create_recipe(actions)
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=True,
        )

        self.assertEqual(1, len(result))
        self.assertEqual(155, len(result[0]))
        self.assertEqual("123456", result[0]["PatientID"].value)

    def test_valueset_empty_remove(self):
        """
        Testing to ensure correct actions are taken when a defined valueset contains no data (the field identified has an empty value). Since the
        ConversionType flag contains "No Value", in the test below, value_set1 will be empty and as a result this combination of rules should have no
        impact on the header.  The input header should be identical to the output header.

        %values value_set1
        FIELD ConversionType
        %header
        REMOVE values:value_set1
        """
        import pydicom

        print("Test empty value valueset")
        dicom_file = get_file(self.dataset)
        original_dataset = pydicom.dcmread(dicom_file)

        actions = [{"action": "REMOVE", "field": "values:value_set1"}]
        values = OrderedDict()
        values["value_set1"] = [
            {"field": "ConversionType", "action": "FIELD"},
        ]
        recipe = create_recipe(actions, values=values)

        # Check that values we want are present using DicomParser
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()
        self.assertEqual(len(parser.lookup["value_set1"]), 0)

        # Perform action
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        self.assertEqual(len(original_dataset), len(result[0]))

    def test_valueset_remove_one_empty(self):
        """
        Testing to ensure correct actions are taken when a defined valueset contains a field that has an empty value. Since the
        ConversionType flag contains "No Value", in the test below, value_set1 will only have the value from Manufacturer and should
        only identify the fields which contain "SIEMENS".

        %values value_set1
        FIELD ConversionType
        FIELD Manufacturer
        %header
        REMOVE values:value_set1
        """
        import pydicom

        print("Test one empty value valueset")
        dicom_file = get_file(self.dataset)
        original_dataset = pydicom.dcmread(dicom_file)

        actions = [{"action": "REMOVE", "field": "values:value_set1"}]
        values = OrderedDict()
        values["value_set1"] = [
            {"field": "ConversionType", "action": "FIELD"},
            {"field": "Manufacturer", "action": "FIELD"},
        ]
        recipe = create_recipe(actions, values=values)

        # Check that values we want are present using DicomParser
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()
        self.assertEqual(len(parser.lookup["value_set1"]), 1)
        self.assertTrue("SIEMENS" in parser.lookup["value_set1"])

        # Perform action
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )
        self.assertEqual(1, len(result))
        self.assertNotEqual(len(original_dataset), len(result[0]))
        with self.assertRaises(KeyError):
            check1 = result[0]["00090010"].value
        with self.assertRaises(KeyError):
            check2 = result[0]["Manufacturer"].value

    def test_jitter_values(self):
        """
        Testing to ensure fields (including non-DA/DT VR fields) identified by a values list
        are appropriately jittered

        %values value_set1
        FIELD StudyDate
        %header
        JITTER values:value_set1 1
        """
        import pydicom

        print("Test jitter from values list")
        dicom_file = get_file(self.dataset)
        original_dataset = pydicom.dcmread(dicom_file)

        actions = [{"action": "JITTER", "field": "values:value_set1", "value": "1"}]
        values = OrderedDict()
        values["value_set1"] = [{"field": "StudyDate", "action": "FIELD"}]
        recipe = create_recipe(actions, values=values)

        # Check that values we want are present using DicomParser
        parser = DicomParser(dicom_file, recipe=recipe)
        parser.parse()
        self.assertEqual(len(parser.lookup["value_set1"]), 1)
        self.assertTrue("20230101" in parser.lookup["value_set1"])

        # Perform action
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )

        self.assertEqual(1, len(result))
        self.assertEqual(len(original_dataset), len(result[0]))
        self.assertEqual("20230102", result[0]["StudyDate"].value)
        self.assertEqual("20230102", result[0]["SeriesDate"].value)
        self.assertEqual("20230102", result[0]["AcquisitionDate"].value)
        self.assertEqual("20230102", result[0]["00291019"].value)
        self.assertEqual("20230102011721.621000", result[0]["00291020"].value)
        self.assertEqual(20230102, result[0]["00291021"].value)
        self.assertEqual("20230102011721.621000-0040", result[0]["00291022"].value)

    def test_jitter_private_tag(self):
        """
        Testing to private tags can be jittered

        %header
        JITTER 00291019 1
        """
        import pydicom

        print("Test jitter private tag")
        dicom_file = get_file(self.dataset)
        original_dataset = pydicom.dcmread(dicom_file)

        actions = [{"action": "JITTER", "field": "00291019", "value": "1"}]
        recipe = create_recipe(actions)

        # Perform action
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )

        self.assertEqual(1, len(result))
        self.assertEqual(len(original_dataset), len(result[0]))
        self.assertEqual("20230102", result[0]["00291019"].value)

    def test_jitter_blank_date(self):
        """
        Testing to ensure jittering a date field which contains a blank value does not cause an unhandled exception

        %header
        JITTER ContentDate 1
        """
        import pydicom

        print("Test jitter date field containing space")
        dicom_file = get_file(self.dataset)
        original_dataset = pydicom.dcmread(dicom_file)

        actions = [{"action": "JITTER", "field": "ContentDate", "value": "1"}]
        recipe = create_recipe(actions)

        # Perform action
        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=False,
            remove_private=False,
            strip_sequences=False,
        )

        self.assertEqual(1, len(result))
        self.assertEqual(len(original_dataset), len(result[0]))
        self.assertEqual("", result[0]["ContentDate"].value)


# MORE TESTS NEED TO BE WRITTEN TO TEST SEQUENCES


if __name__ == "__main__":
    unittest.main()
