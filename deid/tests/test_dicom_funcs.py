#!/usr/bin/env python

import os
import re
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom import get_files, replace_identifiers
from deid.dicom.parser import DicomParser
from deid.tests.common import create_recipe, get_file, get_same_file
from deid.utils import get_installdir
from deid.utils.actions import MissingLookupError

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
        dicom_file = next(get_files(self.dataset, pattern="ctbrain1.dcm"))

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

        self.assertEqual(174, len(parser.dicom))
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

    def test_missing_lookup_raises(self):
        """
        %header
        REMOVE ALL
        REPLACE PatientID var:new_id

        A var:, func: or deid_func: that cannot be found must not leave the
        original value in place. REPLACE and JITTER fields are kept by
        REMOVE ALL, so skipping them kept the original value.
        """
        print("Test missing var/func lookups raise")
        dicom_file = get_file(self.dataset)

        cases = [
            [
                {"action": "REMOVE", "field": "ALL"},
                {"action": "REPLACE", "field": "PatientID", "value": "var:new_id"},
            ],
            [{"action": "REPLACE", "field": "PatientName", "value": "func:pseudonym"}],
            [
                {
                    "action": "REPLACE",
                    "field": "PatientName",
                    "value": "deid_func:no_such_func",
                }
            ],
            [
                {"action": "REMOVE", "field": "ALL"},
                {"action": "JITTER", "field": "StudyDate", "value": "var:shift"},
            ],
            [{"action": "REMOVE", "field": "ALL", "value": "func:keep_or_remove"}],
        ]
        for actions in cases:
            parser = DicomParser(dicom_file, recipe=create_recipe(actions))
            with self.assertRaises(ValueError):
                parser.parse()

    def test_missing_lookup_replace_identifiers(self):
        """
        %header
        REPLACE PatientName var:new_name

        replace_identifiers raises before writing a file that still has the
        original PatientName.
        """
        print("Test missing var raises in replace_identifiers")
        dicom_file = get_file(self.dataset)
        recipe = create_recipe(
            [{"action": "REPLACE", "field": "PatientName", "value": "var:new_name"}]
        )
        message = "var:new_name .* Field: PatientName, file: %s" % re.escape(
            os.path.basename(dicom_file)
        )
        with self.assertRaisesRegex(ValueError, message):
            replace_identifiers(
                dicom_files=dicom_file,
                deid=recipe,
                save=True,
                output_folder=self.tmpdir,
            )
        self.assertEqual([], os.listdir(self.tmpdir))

        # With the variable provided, the name is replaced
        ids = {dicom_file: {"new_name": "ANON"}}
        result = replace_identifiers(dicom_files=dicom_file, deid=recipe, ids=ids)
        self.assertEqual("ANON", str(result[0].PatientName))

    def test_missing_lookup_skips_file_in_batch(self):
        """
        %header
        REPLACE PatientName var:new_name

        A file with a missing var is skipped, the rest of the batch is still
        written, and the error names the skipped file.
        """
        print("Test missing var skips only that file in replace_identifiers")
        dicom_files = list(get_files(self.dataset))
        self.assertEqual(2, len(dicom_files))
        recipe = create_recipe(
            [{"action": "REPLACE", "field": "PatientName", "value": "var:new_name"}]
        )
        ids = {dicom_files[0]: {"new_name": "ANON"}}
        skipped = os.path.basename(dicom_files[1])
        with self.assertRaisesRegex(MissingLookupError, "1 of 2 files") as error:
            replace_identifiers(
                dicom_files=dicom_files,
                deid=recipe,
                ids=ids,
                save=True,
                output_folder=self.tmpdir,
            )
        self.assertIn("file: %s" % skipped, str(error.exception))
        self.assertEqual([os.path.basename(dicom_files[0])], os.listdir(self.tmpdir))

    def test_missing_lookup_add_skips(self):
        """
        %header
        ADD PatientIdentityRemoved var:missing

        ADD still skips a missing var:, as the default recipe relies on it.
        """
        print("Test missing var is skipped for ADD")
        dicom_file = get_file(self.dataset)
        actions = [
            {
                "action": "ADD",
                "field": "PatientIdentityRemoved",
                "value": "var:missing",
            }
        ]
        parser = DicomParser(dicom_file, recipe=create_recipe(actions))
        parser.parse()
        self.assertNotIn("PatientIdentityRemoved", parser.dicom)


if __name__ == "__main__":
    unittest.main()
