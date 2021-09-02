#!/usr/bin/env python

"""
Test Filter Detection

Copyright (c) 2016-2021 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import unittest
import tempfile
import shutil
import json
import os
import numpy as np

from deid.utils import get_installdir
from deid.data import get_dataset
from deid.dicom.parser import DicomParser
from deid.dicom import get_identifiers, replace_identifiers
from pydicom import read_file
from pydicom.sequence import Sequence
from deid.tests.common import get_file

from collections import OrderedDict


class TestFilterDetect(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deidpath = os.path.abspath("%s/tests/resources/" % self.pwd)
        self.dataset = get_dataset("animals")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_filter_single_rule_false(self):
        """Test the DicomCleaner.detect to ensure a single rule evaluated to false detects appropriately."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_single_rule_false.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertFalse(out["flagged"])

    def test_filter_single_rule_true(self):
        """Test the DicomCleaner.detect to ensure a single rule evaluated to true detects appropriately."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_single_rule_true.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

    def test_filter_single_rule_innerop_false(self):
        """Test the DicomCleaner.detect to ensure a single rule with an inner operator evaluated to false detects appropriately."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_single_rule_innerop_false.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertFalse(out["flagged"])

    def test_filter_single_rule_innerop_true(self):
        """Test the DicomCleaner.detect to ensure a single rule with an inner operator evaluated to true detects appropriately."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_single_rule_innerop_true.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

    def test_filter_multiple_rule_innerop_false(self):
        """Test the DicomCleaner.detect to ensure multiple rules within a filter evaluated to false detects appropriately."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_multiple_rule_innerop_false.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertFalse(out["flagged"])

    def test_filter_multple_rule_innerop_true(self):
        """Test the DicomCleaner.detect to ensure multiple rules within a filter evaluated to true detects appropriately."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_multiple_rule_innerop_true.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

    def test_filter_multiple_two_filter_match(self):
        """Test the DicomCleaner.detect to ensure multiple detected filters are appropriately detected."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_multiple_two_filter_match.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        matchgroups = set()

        for r in out["results"]:
            matchgroups.add(r["group"])

        self.assertIn("ShouldMatch1", matchgroups)
        self.assertIn("ShouldMatch2", matchgroups)

    def test_filter_multiple_zero_filter_match(self):
        """Test the DicomCleaner.detect to ensure multiple detected filters are appropriately not detected when they shouldn't match."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_multiple_zero_filter_match.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertFalse(out["flagged"])

        matchgroups = set()

        for r in out["results"]:
            matchgroups.add(r["group"])

        self.assertNotIn("ShouldNotMatch1", matchgroups)
        self.assertNotIn("ShouldNotMatch2", matchgroups)

    def test_filter_multiple_first_filter_match(self):
        """Test the DicomCleaner.detect to ensure multiple detected filters are appropriately detected."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_multiple_first_filter_match.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        matchgroups = set()

        for r in out["results"]:
            matchgroups.add(r["group"])

        self.assertIn("ShouldMatch", matchgroups)
        self.assertNotIn("ShouldNotMatch", matchgroups)

    def test_filter_multiple_second_filter_match(self):
        """Test the DicomCleaner.detect to ensure multiple detected filters are appropriately detected."""
        from deid.dicom import DicomCleaner

        dicom_file = get_file(self.dataset)
        deid = os.path.join(self.deidpath, "filter_multiple_second_filter_match.dicom")

        client = DicomCleaner(output_folder=self.tmpdir, deid=deid)
        out = client.detect(dicom_file)
        self.assertTrue(out["flagged"])

        matchgroups = set()

        for r in out["results"]:
            matchgroups.add(r["group"])

        self.assertIn("ShouldMatch", matchgroups)
        self.assertNotIn("ShouldNotMatch", matchgroups)


if __name__ == "__main__":
    unittest.main()
