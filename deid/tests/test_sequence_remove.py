#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom import get_files, replace_identifiers, utils
from deid.tests.common import create_recipe
from deid.utils import get_installdir

global generate_uid


class TestSequenceRemove(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_remove_single_named_field(self):
        print("Test REMOVE on a single-occurrence named field.")
        field = "PatientName"
        dicom_file = next(get_files(self.dataset, pattern="ctbrain2.dcm"))
        recipe = create_recipe([{"action": "REMOVE", "field": field}])

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        self.assertIsNotNone(currentValue)

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

    def test_remove_single_tag_field(self):
        print("Test REMOVE on a single-occurrence private field.")
        field = "00110002"
        dicom_file = next(get_files(self.dataset, pattern="ctbrain2.dcm"))
        recipe = create_recipe([{"action": "REMOVE", "field": field}])

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        self.assertIsNotNone(currentValue)

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

    def test_remove_one_level_one_occurrence(self):
        print("Test REMOVE one level one occurrence")
        field = "00150002"
        dicom_file = next(get_files(self.dataset, pattern="ctbrain2.dcm"))
        recipe = create_recipe([{"action": "REMOVE", "field": field}])

        inputfile = utils.dcmread(dicom_file)
        currentparent = inputfile["00070001"]
        self.assertEqual(currentparent.VR, "SQ")

        # We know this is a single-occurrence sequence - just target first occurrence
        sequencevalue = currentparent.value[0]
        currentvalue = sequencevalue[field].value

        self.assertIsNotNone(currentvalue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))

        outputparent = outputfile["00070001"]
        self.assertEqual(outputparent.VR, "SQ")

        outputsequence = outputparent.value[0]
        with self.assertRaises(KeyError):
            _ = outputsequence[field].value

    def test_remove_one_level_multiple_occurrences(self):
        print("Test REMOVE one level multiple occurrences")
        field = "00150003"
        dicom_file = next(get_files(self.dataset, pattern="ctbrain2.dcm"))
        recipe = create_recipe([{"action": "REMOVE", "field": field}])

        inputfile = utils.dcmread(dicom_file)
        currentparent = inputfile["00070002"]
        self.assertEqual(currentparent.VR, "SQ")

        for sequencevalue in currentparent:
            currentvalue = sequencevalue[field].value
            self.assertIsNotNone(currentvalue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))

        outputparent = outputfile["00070002"]
        self.assertEqual(outputparent.VR, "SQ")

        for sequencevalue in outputparent:
            with self.assertRaises(KeyError):
                _ = sequencevalue[field].value

    def test_remove_multiple_levels_multiple_occurrences(self):
        print("Test REMOVE multiple levels multiple occurrences")
        field = "00150006"
        dicom_file = next(get_files(self.dataset, pattern="ctbrain2.dcm"))
        recipe = create_recipe([{"action": "REMOVE", "field": field}])

        inputfile = utils.dcmread(dicom_file)
        level1parent = inputfile["00070003"]
        self.assertEqual(level1parent.VR, "SQ")

        for sequenceoccurrence in level1parent:
            for sequence2value in sequenceoccurrence:
                self.assertEqual(sequence2value.VR, "SQ")  # 0007,0004
                level2value = sequence2value.value
                self.assertIsNotNone(level2value)

                for level2dataset in level2value:
                    self.assertIsNotNone(level2dataset[field].value)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))

        outputparent = outputfile["00070003"]
        self.assertEqual(outputparent.VR, "SQ")

        for sequenceoccurrence in outputparent:
            for sequence2value in sequenceoccurrence:
                self.assertEqual(sequence2value.VR, "SQ")  # 0007,0004
                level2value = sequence2value.value
                self.assertIsNotNone(level2value)

                for level2dataset in level2value:
                    with self.assertRaises(KeyError):
                        _ = level2dataset[field].value

    def test_remove_nested_named_field(self):
        print("Test REMOVE on a nested named field.")
        field = "AccessionNumber"
        dicom_file = next(get_files(self.dataset, pattern="ctbrain2.dcm"))
        recipe = create_recipe([{"action": "REMOVE", "field": field}])

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[field].value
        self.assertIsNotNone(currentValue)

        currentparent = inputfile["RequestAttributesSequence"]
        self.assertEqual(currentparent.VR, "SQ")

        for sequencevalue in currentparent:
            currentvalue = sequencevalue[field].value
            self.assertIsNotNone(currentvalue)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))

        outputparent = outputfile["RequestAttributesSequence"]
        self.assertEqual(outputparent.VR, "SQ")
        outputsqvalue = outputparent.value

        for sequencevalue in outputsqvalue:
            with self.assertRaises(KeyError):
                _ = sequencevalue[field].value


if __name__ == "__main__":
    unittest.main()
