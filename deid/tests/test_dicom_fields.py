#!/usr/bin/env python

"""
Testing field parsing and expansion

Copyright (c) 2020-2021 Vanessa Sochat

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

from deid.utils import get_installdir
from deid.data import get_dataset
from deid.dicom.fields import get_fields
from deid.tests.common import get_dicom


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

        contenders = get_fields(dicom)

        print("Testing that field expansion works for basic tags")
        fields = expand_field_expression(
            dicom=dicom, field="endswith:Time", contenders=contenders
        )

        # The fields returned should end in time
        for uid, field in fields.items():
            assert field.name.endswith("Time")

        print("Testing that we can also search private tags based on numbers.")
        fields = expand_field_expression(
            dicom=dicom, field="contains:0019", contenders=contenders
        )

        # The fields returned should include tag group or element 0019
        for uid, field in fields.items():
            assert "0019" in uid

        print("Testing nested private tags")
        dataset = get_dataset("animals")  # includes nested private tags
        dicom = get_dicom(dataset)


if __name__ == "__main__":
    unittest.main()
