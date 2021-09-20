"""

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

from deid.utils import get_installdir
from deid.data import get_dataset
from deid.tests.common import get_file


class TestDicomTags(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("dicom-cookies")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_get_tag(self):
        print("Test deid.dicom.tags get_tag")
        from deid.dicom.tags import get_tag
        from pydicom.tag import BaseTag

        print("Case 1: Ask for known tag")
        tag = get_tag("Modality")
        self.assertEqual(tag["VM"], "1")
        self.assertEqual(tag["VR"], "CS")
        self.assertEqual(tag["keyword"], "Modality")
        self.assertEqual(tag["name"], "Modality")
        self.assertTrue(isinstance(tag["tag"], BaseTag))

        print("Case 2: Ask for unknown tag")
        tag = get_tag("KleenexTissue")
        self.assertTrue(not tag)


if __name__ == "__main__":
    unittest.main()
