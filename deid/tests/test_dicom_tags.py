import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.utils import get_installdir


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
        from pydicom.tag import BaseTag

        from deid.dicom.tags import get_tag

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
