#!/usr/bin/env python

import json
import os
import shutil
import tempfile
import unittest

from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.sequence import Sequence

from deid.data import get_dataset
from deid.dicom import get_identifiers
from deid.dicom.fields import get_fields_with_lookup
from deid.dicom.parser import DicomParser
from deid.tests.common import get_dicom
from deid.utils import get_installdir


class TestParserFieldExtraction(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name
        self.dataset = FileDataset(
            os.path.join(self.directory, "synthetic.dcm"),
            {},
            file_meta=FileMetaDataset(),
        )
        self.dataset.PatientID = "TOP ORIGINAL"
        nested = Dataset()
        nested.PatientID = "NESTED ORIGINAL"
        self.dataset.OtherPatientIDsSequence = Sequence([nested])
        self.recipe = {
            "format": "dicom",
            "header": [{"action": "REPLACE", "field": "PatientID", "value": "ANON"}],
        }

    def test_repeated_extraction(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        first = parser.get_fields()
        second = parser.get_fields()
        self.assertEqual(list(first), list(second))
        parser.parse()
        self.assertEqual(self.dataset.PatientID, "ANON")
        self.assertEqual(self.dataset.OtherPatientIDsSequence[0].PatientID, "ANON")

    def test_unexpanded_inspection_then_parse(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        self.assertEqual(len(list(parser.get_fields(expand_sequences=False))), 2)
        parser.parse()
        self.assertEqual(self.dataset.PatientID, "ANON")
        self.assertEqual(self.dataset.OtherPatientIDsSequence[0].PatientID, "ANON")

    def test_expansion_option_each_call(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        counts = [
            len(list(parser.get_fields(expand_sequences=expand)))
            for expand in (False, True, False)
        ]
        self.assertEqual(counts, [2, 3, 2])

    def test_skip_context_each_call(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.config["get"]["skip"] = ["PatientID"]
        for disable_skip, expected in ((False, 1), (True, 3), (False, 1)):
            with self.subTest(disable_skip=disable_skip):
                parser.disable_skip = disable_skip
                fields = parser.get_fields()
                self.assertEqual(len(list(fields)), expected)
                patient_ids = [
                    field
                    for field in fields.values()
                    if field.name.endswith("PatientID")
                ]
                self.assertEqual(len(patient_ids), 2 if disable_skip else 0)

    def test_load_clears_previous_fields(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.get_fields()
        second = FileDataset(
            os.path.join(self.directory, "second.dcm"), {}, file_meta=FileMetaDataset()
        )
        second.PatientID = "SECOND"
        parser.load(second)
        self.assertFalse(parser.fields)
        self.assertEqual(parser.seen, [])
        self.assertEqual(parser.find_by_name("PatientID"), {})
        self.assertEqual(
            [field.element.value for field in parser.get_fields().values()], ["SECOND"]
        )
        parser.parse()
        self.assertEqual(second.PatientID, "ANON")
        self.assertEqual(self.dataset.PatientID, "TOP ORIGINAL")

    def test_removed_fields_stay_removed(self):
        self.recipe["header"] = [{"action": "REMOVE", "field": "PatientID"}]
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.parse()
        fields = parser.get_fields()
        self.assertNotIn("PatientID", self.dataset)
        self.assertNotIn("PatientID", self.dataset.OtherPatientIDsSequence[0])
        self.assertEqual(fields.get_exact_matches("PatientID"), [])
        self.assertEqual(
            [field.name for field in fields.values()], ["OtherPatientIDsSequence"]
        )

    def test_contexts_after_removal(self):
        self.recipe["header"] = [{"action": "REMOVE", "field": "PatientID"}]
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.get_fields(False)
        parser.get_fields(True)
        parser.parse()
        for expand in (True, False, True):
            with self.subTest(expand=expand):
                fields = parser.get_fields(expand)
                self.assertEqual(fields.get_exact_matches("PatientID"), [])
                self.assertFalse(
                    any(field.name.endswith("PatientID") for field in fields.values())
                )
        self.assertNotIn("PatientID", self.dataset)
        self.assertNotIn("PatientID", self.dataset.OtherPatientIDsSequence[0])

    def test_contexts_after_add_replace_blank(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.get_fields(False)
        parser.get_fields(True)
        parser.add_field("PatientName", "SYNTHETIC")
        for expand in (False, True):
            fields = parser.get_fields(expand)
            self.assertEqual(
                fields.get_exact_matches("PatientName")[0].element.value, "SYNTHETIC"
            )
        field = parser.fields.get_exact_matches("PatientName")[0]
        parser.replace_field(field, "REPLACED")
        self.assertEqual(
            parser.get_fields(False).get_exact_matches("PatientName")[0].element.value,
            "REPLACED",
        )
        parser.get_fields(True)
        sequence = parser.fields.get_exact_matches("OtherPatientIDsSequence")[0]
        parser.blank_field(sequence)
        for expand in (False, True):
            self.assertFalse(
                any("__" in field.name for field in parser.get_fields(expand).values())
            )

    def test_same_context_reflects_direct_dataset_mutations(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        fields = parser.get_fields(False)
        self.assertEqual(len(list(fields)), 2)
        self.dataset.PatientName = "EXTERNALLY ADDED"
        updated = parser.get_fields(False)
        self.assertIsNot(updated, fields)
        self.assertEqual(len(list(updated)), 3)
        self.assertEqual(
            updated.get_exact_matches("PatientName")[0].element.value,
            "EXTERNALLY ADDED",
        )

    def test_strip_sequences_after_inspection(self):
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.get_fields()
        parser.parse(strip_sequences=True)
        self.assertNotIn("OtherPatientIDsSequence", self.dataset)
        for expand in (False, True):
            self.assertEqual(
                [field.name for field in parser.get_fields(expand).values()],
                ["PatientID"],
            )

    def test_remove_private_after_inspection(self):
        self.dataset.add_new((0x0011, 0x0010), "LO", "SYNTHETIC")
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.get_fields(False)
        parser.get_fields(True)
        parser.remove_private()
        for expand in (True, False):
            self.assertFalse(
                any(
                    field.element.is_private
                    for field in parser.get_fields(expand).values()
                )
            )

    def test_keep_after_adding_field(self):
        self.recipe["header"] = [
            {"action": "KEEP", "field": "PatientName"},
            {"action": "REPLACE", "field": "PatientName", "value": "REPLACED"},
        ]
        parser = DicomParser(self.dataset, recipe=self.recipe)
        parser.get_fields()
        parser.add_field("PatientName", "KEEP ORIGINAL")
        parser.parse()
        self.assertEqual(self.dataset.PatientName, "KEEP ORIGINAL")

    def test_identifier_skip_override(self):
        with tempfile.TemporaryDirectory() as directory:
            config_file = os.path.join(directory, "config.json")
            with open(config_file, "w") as config:
                json.dump(
                    {"get": {"skip": ["PatientID"]}, "put": {"actions": []}}, config
                )
            for options, expected in (
                ({}, 1),
                ({"disable_skip": True}, 3),
                ({"disable_skip": False}, 1),
            ):
                with self.subTest(options=options):
                    identifiers = get_identifiers(
                        self.dataset, config=config_file, **options
                    )
                    fields = identifiers[os.path.abspath(self.dataset.filename)]
                    self.assertEqual(len(fields), expected)
                    patient_ids = [
                        field
                        for field in fields.values()
                        if field.name.endswith("PatientID")
                    ]
                    self.assertEqual(len(patient_ids), 2 if expected == 3 else 0)

    def test_default_protected_fields(self):
        self.dataset.PixelData = b"\0\0"
        self.dataset.file_meta.TransferSyntaxUID = "1.2.840.10008.1.2.1"
        for disable_skip in (False, True):
            with self.subTest(disable_skip=disable_skip):
                identifiers = get_identifiers(self.dataset, disable_skip=disable_skip)
                names = {
                    field.name
                    for fields in identifiers.values()
                    for field in fields.values()
                }
                for name in ("PixelData", "TransferSyntaxUID"):
                    self.assertEqual(name in names, disable_skip)


class TestDicomFields(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("animals")  # includes private tags
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_field_expansion(self):
        print("Test deid.dicom.fields expand_field_expression")
        from deid.dicom.fields import expand_field_expression

        dicom = get_dicom(self.dataset)

        contenders = get_fields_with_lookup(dicom)

        print("Testing that field expansion works for basic tags")
        fields = expand_field_expression(
            dicom=dicom,
            field="endswith:Time",
            contenders=contenders,
        )

        # The fields returned should end in time
        for uid, field in fields.items():
            assert field.name.endswith("Time")

        print("Testing that field expansion works for groups")
        fields = expand_field_expression(
            dicom=dicom,
            field="select:group:0020",
            contenders=contenders,
        )

        # The fields returned should be tag group 0020
        for uid, field in fields.items():
            assert field.element.tag.group == 0x0020

        print("Testing that field expansion works for VR")
        fields = expand_field_expression(
            dicom=dicom,
            field="select:VR:TM",
            contenders=contenders,
        )

        # The fields returned should end in time
        for uid, field in fields.items():
            assert field.name.endswith("Time")
            assert field.element.VR == "TM"

        print("Testing that we can also search private tags based on numbers.")
        fields = expand_field_expression(
            dicom=dicom,
            field="contains:0019",
            contenders=contenders,
        )

        # The fields returned should include tag group or element 0019
        for uid, field in fields.items():
            assert "0019" in uid

        print("Testing nested private tags")
        dataset = get_dataset("animals")  # includes nested private tags
        dicom = get_dicom(dataset)


if __name__ == "__main__":
    unittest.main()
