#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

"""
Test file meta
"""

import unittest

from deid.data import get_dataset
from deid.dicom import replace_identifiers
from deid.tests.common import create_recipe, get_file
from deid.utils import get_installdir


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