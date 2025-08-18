#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom import replace_identifiers, utils
from deid.tests.common import create_recipe, get_file
from deid.utils import get_installdir

global generate_uid


class TestRemoveAction(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def run_remove_single_tag_fieldtest(self, Field):
        print(f"Test REMOVE standard tags in format {Field}")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "REMOVE", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile["00100010"].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            _ = outputfile["00100010"].value

    def test_remove_standard_tags_1(self):
        self.run_remove_single_tag_fieldtest(
            "(0010,0010)"
        )  # PatientName in DICOM format

    def test_remove_standard_tags_2(self):
        self.run_remove_single_tag_fieldtest("00100010")  # PatientName in hex format

    def test_remove_standard_tags_3(self):
        self.run_remove_single_tag_fieldtest(
            "PatientName"
        )  # PatientName in keyword format

    def test_remove_standard_field_4(self):
        self.run_remove_single_tag_fieldtest(
            "startswith:PatientN"
        )  # PatientName in startswith: format

    def test_remove_single_private_tag_field(self):
        """RECIPE RULE
        REMOVE 0033101E
        """
        print("Test REMOVE private tag with hex format")
        dicom_file = get_file(self.dataset)

        Field = "0033101E"  # Private tag in hex format
        actions = [
            {"action": "REMOVE", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[Field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )
        outputfile = utils.dcmread(result[0])

        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            _ = outputfile[Field].value

    def test_remove_single_tag_private_creator_syntax_1(self):
        """RECIPE RULE
        REMOVE (0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)
        """
        print("Test REMOVE private tag with private creator syntax")
        dicom_file = get_file(self.dataset)

        Field = '(0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)'
        field_dicom = "0033101E"
        actions = [
            {"action": "REMOVE", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field_dicom].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )
        outputfile = utils.dcmread(result[0])

        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            _ = outputfile[field_dicom].value

    def test_remove_single_tag_private_creator_syntax_2(self):
        """RECIPE RULE
        REMOVE 0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E
        """
        print("Test REMOVE private tag with (stripped) private creator syntax")
        dicom_file = get_file(self.dataset)

        Field = '0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E'
        field_dicom = "0033101E"
        actions = [
            {"action": "REMOVE", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field_dicom].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )
        outputfile = utils.dcmread(result[0])

        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            _ = outputfile[field_dicom].value

    def test_remove_single_tag_private_creator_syntax_3(self):
        """RECIPE RULE
        REMOVE (0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)
        """
        print(
            "Test REMOVE private tag with private creator syntax from external recipe file"
        )
        dicom_file = get_file(self.dataset)

        field_dicom = "0033101E"

        recipe = os.path.abspath(
            "%s/../examples/deid/deid.dicom-private-creator-syntax" % self.pwd
        )

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field_dicom].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )
        outputfile = utils.dcmread(result[0])

        self.assertEqual(1, len(result))
        with self.assertRaises(KeyError):
            _ = outputfile[field_dicom].value

    def test_remove_single_tag_private_creator_no_match(self):
        """RECIPE RULE
        REMOVE 0033,"MITRA OBJECT UTF8 ATTRIBUTES 1",1E
        """
        print(
            "Test REMOVE private tag with mismatched private creator - should NOT remove"
        )
        dicom_file = get_file(self.dataset)

        # Use wrong private creator - should not match existing tag
        Field = '0033,"MITRA OBJECT UTF8 ATTRIBUTES 1",1E'
        field_dicom = "0033101E"
        actions = [
            {"action": "REMOVE", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field_dicom].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )
        outputfile = utils.dcmread(result[0])

        self.assertEqual(1, len(result))
        # Tag should still exist because private creator didn't match
        self.assertEqual(currentValue, outputfile[field_dicom].value)


if __name__ == "__main__":
    unittest.main()
