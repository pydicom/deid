#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.config import DeidRecipe
from deid.utils import get_installdir


class TestDeidRecipe(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_load_recipe(self):
        print("Case 1: Test loading default DeidRecipe")

        recipe = DeidRecipe()

        self.assertTrue(isinstance(recipe.deid, dict))

        print("Checking basic sections are loaded")
        print(recipe.deid.keys())
        for section in ["header", "format", "filter"]:
            self.assertTrue(section in recipe.deid)

        print("Case 2: Loading from file")
        recipe = DeidRecipe(self.deid)

    def test_get_functions(self):
        recipe = DeidRecipe(self.deid)

        # Format
        self.assertEqual(recipe.get_format(), "dicom")

        # Actions for header
        print("Testing get_actions")
        actions = recipe.get_actions()
        self.assertTrue(isinstance(actions, list))
        for key in ["action", "field", "value"]:
            self.assertTrue(key in actions[0])
        self.assertTrue(recipe.has_actions())

        # Filters
        print("Testing get_filters")
        filters = recipe.get_filters()
        self.assertTrue(isinstance(filters, dict))

        # whitelist, blacklist, graylist
        for key in recipe.ls_filters():
            self.assertTrue(key in filters)

        recipe = DeidRecipe()
        filters = recipe.get_filters()
        self.assertTrue(isinstance(filters["whitelist"], list))

        # Test that each filter has a set of filters, coords, name
        for key in ["filters", "coordinates", "name"]:
            self.assertTrue(key in filters["whitelist"][0])

        # Each filter is a list of actions, name is string, coords are list
        self.assertTrue(isinstance(filters["whitelist"][0]["filters"], list))
        self.assertTrue(isinstance(filters["whitelist"][0]["name"], str))
        self.assertTrue(isinstance(filters["whitelist"][0]["coordinates"], list))

        # Check content of the first filter
        for key in ["action", "field", "operator", "InnerOperators", "value"]:
            self.assertTrue(key in filters["whitelist"][0]["filters"][0])

        # Fields and Values
        print("Testing get_fields_lists and get_values_lists")
        self.assertEqual(recipe.get_fields_lists(), None)
        self.assertEqual(recipe.get_values_lists(), None)
        self.assertEqual(recipe.ls_fieldlists(), [])
        self.assertEqual(recipe.ls_valuelists(), [])
        self.assertTrue(not recipe.has_fields_lists())
        self.assertTrue(not recipe.has_values_lists())

        # Load in recipe with values and fields
        deid = os.path.abspath("%s/../examples/deid/deid.dicom-groups" % self.pwd)
        recipe = DeidRecipe(deid)

        assert "values" in recipe.deid
        assert "fields" in recipe.deid
        self.assertTrue(isinstance(recipe.deid["values"], dict))
        self.assertTrue(isinstance(recipe.deid["fields"], dict))

        self.assertTrue(recipe.get_fields_lists() is not None)
        self.assertTrue(recipe.get_values_lists() is not None)
        self.assertEqual(recipe.ls_fieldlists(), ["instance_fields"])
        self.assertEqual(recipe.ls_valuelists(), ["cookie_names", "operator_names"])
        self.assertTrue(recipe.has_fields_lists())
        self.assertTrue(recipe.has_values_lists())


if __name__ == "__main__":
    unittest.main()
