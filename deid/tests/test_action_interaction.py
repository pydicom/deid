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


class TestRuleInteractions(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_add_add_should_have_second_value(self):
        """RECIPE RULE
        ADD PatientIdentityRemoved No
        ADD PatientIdentityRemoved Yes
        """

        print("Test ADD/ADD Interaction")
        dicom_file = get_file(self.dataset)

        field = "PatientIdentityRemoved"

        action1 = "ADD"
        value1 = "No"

        action2 = "ADD"
        value2 = "Yes"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        with self.assertRaises(KeyError):
            inputfile[field].value

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(value2, outputfile[field].value)

    def test_add_blank_should_be_blank(self):
        """RECIPE RULE
        ADD PregnancyStatus 1
        BLANK PregnancyStatus
        """

        print("Test ADD/BLANK Interaction")
        dicom_file = get_file(self.dataset)

        field = "PregnancyStatus"

        action1 = "ADD"
        value1 = "1"

        action2 = "BLANK"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(1, currentValue)
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
        self.assertEqual(None, outputfile[field].value)

    def test_add_jitter_should_combine(self):
        """RECIPE RULE
        ADD StudyDate 20221128
        JITTER StudyDate 5
        """

        print("Test ADD/JITTER Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "ADD"
        value1 = "20221128"

        action2 = "JITTER"
        value2 = "5"

        valueexpected = "20221203"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_add_keep_should_have_add_value(self):
        """RECIPE RULE
        ADD StudyDate 20221128
        KEEP StudyDate
        """

        print("Test ADD/KEEP Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "ADD"
        value1 = "20221128"

        action2 = "KEEP"

        valueexpected = "20221128"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_add_replace_should_have_replace_value(self):
        """RECIPE RULE
        ADD StudyDate 20221128
        REPLACE StudyDate 20221129
        """

        print("Test ADD/REPLACE Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "ADD"
        value1 = "20221128"

        action2 = "REPLACE"
        value2 = "20221129"

        valueexpected = "20221129"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_add_remove_should_be_removed(self):
        """RECIPE RULE
        ADD StudyDate 20221128
        REMOVE StudyDate
        """

        print("Test ADD/REMOVE Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "ADD"
        value1 = "20221128"

        action2 = "REMOVE"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)

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
            _ = outputfile[field].value

    def test_blank_add_should_have_add_value(self):
        """RECIPE RULE
        BLANK Manufacturer
        ADD Manufacturer Testing
        """

        print("Test BLANK/ADD Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "BLANK"

        action2 = "ADD"
        value2 = "Testing"

        valueexpected = "Testing"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_blank_blank_should_be_blank(self):
        """This is a bit of a nonsensical test, but is included for completeness.
        RECIPE RULE
        BLANK Manufacturer
        BLANK Manufacturer
        """

        print("Test BLANK/BLANK Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "BLANK"
        action2 = "BLANK"

        valueexpected = ""

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_blank_jitter_should_be_blank(self):
        """RECIPE RULE
        BLANK StudyDate
        JITTER StudyDate 1
        """

        print("Test BLANK/JITTER Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "BLANK"

        action2 = "JITTER"
        value2 = "1"

        valueexpected = ""

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_blank_keep_should_be_original_value(self):
        """RECIPE RULE
        BLANK Manufacturer
        KEEP Manufacturer
        """

        print("Test BLANK/KEEP Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "BLANK"
        action2 = "KEEP"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_blank_replace_should_be_replace_value(self):
        """RECIPE RULE
        BLANK Manufacturer
        REPLACE Manufacturer Testing
        """

        print("Test BLANK/REPLACE Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "BLANK"

        action2 = "REPLACE"
        value2 = "Testing"

        valueexpected = "Testing"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_blank_remove_should_be_removed(self):
        """RECIPE RULE
        BLANK StudyDate
        REMOVE StudyDate
        """

        print("Test BLANK/REMOVE Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "BLANK"
        action2 = "REMOVE"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

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
            _ = outputfile[field].value

    def test_jitter_add_should_have_add_value(self):
        """RECIPE RULE
        JITTER StudyDate 1
        ADD StudyDate 20221129
        """

        print("Test JITTER/ADD Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "JITTER"
        value1 = "1"

        action2 = "ADD"
        value2 = "20221129"

        valueexpected = value2

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(valueexpected, currentValue)
        self.assertNotEqual("20221130", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_jitter_blank_should_be_blank(self):
        """RECIPE RULE
        JITTER StudyDate 1
        BLANK StudyDate
        """

        print("Test JITTER/BLANK Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "JITTER"
        value1 = "1"

        action2 = "BLANK"

        valueexpected = ""

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

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
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_jitter_jitter_should_combine(self):
        """RECIPE RULE
        JITTER StudyDate 1
        JITTER StudyDate 2
        """

        print("Test JITTER/JITTER Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "JITTER"
        value1 = "1"

        action2 = "JITTER"
        value2 = "2"

        valueexpected = "20230104"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(valueexpected, currentValue)
        self.assertEqual("20230101", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_jitter_keep_should_be_original_value(self):
        """RECIPE RULE
        JITTER StudyDate 1
        KEEP StudyDate
        """

        print("Test JITTER/KEEP Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "JITTER"
        value1 = "1"

        action2 = "KEEP"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

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
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_jitter_replace_should_have_replace_value(self):
        """RECIPE RULE
        JITTER StudyDate 1
        REPLACE StudyDate 20221129
        """

        print("Test JITTER/REPLACE Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "JITTER"
        value1 = "1"

        action2 = "REPLACE"
        value2 = "20221129"

        valueexpected = value2

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(valueexpected, currentValue)
        self.assertEqual("20230101", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_jitter_remove_should_ignore_remove(self):
        """RECIPE RULE
        JITTER StudyDate 1
        REMOVE StudyDate
        """

        print("Test JITTER/REMOVE Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "JITTER"
        value1 = "1"

        action2 = "REMOVE"
        valueexpected = "20230102"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertEqual("20230101", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_keep_add_should_be_add_value(self):
        """RECIPE RULE
        KEEP Manufacturer
        ADD Manufacturer Testing
        """

        print("Test KEEP/ADD Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "KEEP"

        action2 = "ADD"
        value2 = "Testing"

        valueexpected = value2

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_keep_blank_should_be_original_value(self):
        """RECIPE RULE
        KEEP Manufacturer
        BLANK Manufacturer
        """

        print("Test KEEP/BLANK Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "KEEP"
        action2 = "BLANK"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

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
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_keep_jitter_should_be_original_value(self):
        """RECIPE RULE
        KEEP StudyDate
        JITTER StudyDate 1
        """

        print("Test KEEP/JITTER Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "KEEP"

        action2 = "JITTER"
        value2 = "1"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("20230102", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_keep_keep_should_be_original_value(self):
        """This is a bit of a nonsensical test, but is included for completeness.
        RECIPE RULE
        KEEP Manufacturer
        KEEP Manufacturer
        """

        print("Test KEEP/KEEP Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "KEEP"
        action2 = "KEEP"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_keep_replace_should_be_original_value(self):
        """RECIPE RULE
        KEEP Manufacturer
        REPLACE Manufacturer Testing
        """

        print("Test KEEP/REPLACE Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "KEEP"

        action2 = "REPLACE"
        value2 = "Testing"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

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
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_keep_remove_should_be_original_value(self):
        """RECIPE RULE
        KEEP StudyDate
        REMOVE StudyDate
        """

        print("Test KEEP/REMOVE Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "KEEP"
        action2 = "REMOVE"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

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
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_replace_add_should_have_add_value(self):
        """RECIPE RULE
        REPLACE Manufacturer TestingReplace
        ADD Manufacturer TestingAdd
        """

        print("Test REPLACE/ADD Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "REPLACE"
        value1 = "TestingReplace"

        action2 = "ADD"
        value2 = "TestingAdd"

        valueexpected = value2

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_replace_blank_should_be_blank(self):
        """RECIPE RULE
        REPLACE Manufacturer TestingReplace
        BLANK Manufacturer
        """

        print("Test REPLACE/BLANK Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "REPLACE"
        value1 = "TestingReplace"

        action2 = "BLANK"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertNotEqual(None, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual("", outputfile[field].value)

    def test_replace_jitter_should_combine(self):
        """RECIPE RULE
        REPLACE StudyDate 20221128
        JITTER StudyDate 5
        """

        print("Test REPLACE/JITTER Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "REPLACE"
        value1 = "20221128"

        action2 = "JITTER"
        value2 = "5"

        valueexpected = "20221203"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_replace_keep_should_have_original_value(self):
        """RECIPE RULE
        REPLACE StudyDate 20221128
        KEEP StudyDate
        """

        print("Test REPLACE/KEEP Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "REPLACE"
        value1 = "20221128"

        action2 = "KEEP"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

        self.assertNotEqual(value1, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_replace_replace_should_have_second_replace_value(self):
        """RECIPE RULE
        REPLACE StudyDate 20221128
        REPLACE StudyDate 20221129
        """

        print("Test REPLACE/REPLACE Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "REPLACE"
        value1 = "20221128"

        action2 = "REPLACE"
        value2 = "20221129"

        valueexpected = "20221129"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_replace_remove_should_be_replace_value(self):
        """RECIPE RULE
        REPLACE StudyDate 20221128
        REMOVE StudyDate
        """

        print("Test REPLACE/REMOVE Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "REPLACE"
        value1 = "20221128"

        action2 = "REMOVE"

        actions = [
            {"action": action1, "field": field, "value": value1},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(value1, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(value1, outputfile[field].value)

    def test_remove_add_should_be_add_value(self):
        """RECIPE RULE
        REMOVE Manufacturer
        ADD Manufacturer Testing
        """

        print("Test REMOVE/ADD Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "REMOVE"

        action2 = "ADD"
        value2 = "Testing"

        valueexpected = value2

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertNotEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_remove_blank_should_be_removed(self):
        """RECIPE RULE
        REMOVE Manufacturer
        BLANK Manufacturer
        """

        print("Test REMOVE/BLANK Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "REMOVE"
        action2 = "BLANK"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

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
            _ = outputfile[field].value

    def test_remove_jitter_should_jittered_date(self):
        """RECIPE RULE
        REMOVE StudyDate
        JITTER StudyDate 1
        """

        print("Test REMOVE/JITTER Interaction")
        dicom_file = get_file(self.dataset)

        field = "StudyDate"

        action1 = "REMOVE"

        action2 = "JITTER"
        value2 = "1"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("20230102", currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual("20230102", outputfile[field].value)

    def test_remove_keep_should_be_original_value(self):
        """RECIPE RULE
        REMOVE Manufacturer
        KEEP Manufacturer
        """

        print("Test REMOVE/KEEP Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "REMOVE"
        action2 = "KEEP"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        valueexpected = currentValue

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertEqual(valueexpected, currentValue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_remove_replace_should_be_replace_value(self):
        """RECIPE RULE
        REMOVE Manufacturer
        REPLACE Manufacturer Testing
        """

        print("Test REMOVE/REPLACE Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "REMOVE"

        action2 = "REPLACE"
        value2 = "Testing"
        valueexpected = value2

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field, "value": value2},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

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
        self.assertEqual(valueexpected, outputfile[field].value)

    def test_remove_remove_should_remove(self):
        """This is a bit of a nonsensical test, but is included for completeness.
        RECIPE RULE
        REMOVE StudyDate
        REMOVE StudyDate
        """

        print("Test REMOVE/REMOVE Interaction")
        dicom_file = get_file(self.dataset)

        field = "Manufacturer"

        action1 = "REMOVE"
        action2 = "REMOVE"

        actions = [
            {"action": action1, "field": field},
            {"action": action2, "field": field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value

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
            _ = outputfile[field].value


if __name__ == "__main__":
    unittest.main()
