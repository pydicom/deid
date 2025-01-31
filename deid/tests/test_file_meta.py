#!/usr/bin/env python

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
        REPLACE MediaStorageSOPInstanceUID 1.2.3.4.5.4.3.2.1
        """
        print("Test replace filemeta")
        dicom_file = get_file(self.dataset)

        actions = [
            {
                "action": "REPLACE",
                "field": "MediaStorageSOPInstanceUID",
                "value": "1.2.3.4.5.4.3.2.1",
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
            "1.2.3.4.5.4.3.2.1", result[0].file_meta["MediaStorageSOPInstanceUID"].value
        )

    def test_replace_protected_field(self):
        """RECIPE RULE
        REPLACE TransferSyntaxUID 1.2.3.4.5.4.3.2.1
        """
        print("Test replace filemeta")
        dicom_file = get_file(self.dataset)

        actions = [
            {
                "action": "REPLACE",
                "field": "TransferSyntaxUID",
                "value": "1.2.3.4.5.4.3.2.1",
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
        self.assertNotEqual("1.2.3.4.5.4.3.2.1", result[0].file_meta.TransferSyntaxUID)

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
        self.assertEqual("1.2.3.4.5.4.3.2.1", result[0].file_meta.TransferSyntaxUID)


if __name__ == "__main__":
    unittest.main()
