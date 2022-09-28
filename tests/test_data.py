#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"


"""
Test data functions
"""

import os
import unittest

from tests.common import get_dataset


class TestUtils(unittest.TestCase):
    def setUp(self):
        print("\n######################START######################")

    def tearDown(self):
        print("\n######################END########################")

    def test_get_dataset(self):
        """test_get_dataset will make sure we can load provided datasets"""
        print("Case 1: Ask for existing dataset.")

        dataset = get_dataset("dicom-cookies")
        self.assertTrue(os.path.exists(dataset))

        print("Case 2: Ask for non existing dataset")
        dataset = get_dataset("other-cookies")
        self.assertEqual(dataset, None)


if __name__ == "__main__":
    unittest.main()
