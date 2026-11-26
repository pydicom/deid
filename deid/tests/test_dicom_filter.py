#!/usr/bin/env python

import unittest

from pydicom.dataset import Dataset
from pydicom.multival import MultiValue

import deid.dicom.filter  # noqa: F401 (adds the filters to Dataset)


def get_dataset():
    """Get a dataset with a multi-valued and a single-valued attribute."""
    ds = Dataset()
    ds.ImageType = ["DERIVED", "PRIMARY", "AXIAL"]
    ds.Modality = "CT"
    return ds


class TestDicomFilter(unittest.TestCase):
    def test_multi_value_type(self):
        """pydicom gives a multi-valued attribute as a MultiValue, not a list."""
        ds = get_dataset()
        self.assertIsInstance(ds.ImageType, MultiValue)
        self.assertNotIsInstance(ds.ImageType, list)

    def test_equals_multi_value(self):
        ds = get_dataset()
        self.assertTrue(ds.equals("ImageType", "DERIVED"))
        self.assertTrue(ds.equals("ImageType", "axial"))
        self.assertFalse(ds.equals("ImageType", "SECONDARY"))

    def test_not_equals_multi_value(self):
        ds = get_dataset()
        self.assertFalse(ds.notEquals("ImageType", "DERIVED"))
        self.assertTrue(ds.notEquals("ImageType", "SECONDARY"))

    def test_matches_multi_value(self):
        ds = get_dataset()
        self.assertTrue(ds.matches("ImageType", "PRIMARY"))
        self.assertTrue(ds.matches("ImageType", "DER"))
        self.assertFalse(ds.matches("ImageType", "SECONDARY"))

    def test_contains_multi_value(self):
        ds = get_dataset()
        self.assertTrue(ds.contains("ImageType", "AXI"))
        self.assertFalse(ds.contains("ImageType", "SECONDARY"))
        self.assertTrue(ds.notContains("ImageType", "SECONDARY"))

    def test_single_value(self):
        ds = get_dataset()
        self.assertTrue(ds.equals("Modality", "CT"))
        self.assertFalse(ds.equals("Modality", "MR"))
        self.assertTrue(ds.matches("Modality", "C"))


if __name__ == "__main__":
    unittest.main()
