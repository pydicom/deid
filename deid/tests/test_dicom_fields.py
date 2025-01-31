#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom.fields import get_fields
from deid.tests.common import get_dicom
from deid.utils import get_installdir


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

        print("Testing that field expansion works for groups")
        fields = expand_field_expression(
            dicom=dicom, field="select:group:0020", contenders=contenders
        )

        # The fields returned should be tag group 0020
        for uid, field in fields.items():
            assert field.element.tag.group == 0x0020

        print("Testing that field expansion works for VR")
        fields = expand_field_expression(
            dicom=dicom, field="select:VR:TM", contenders=contenders
        )

        # The fields returned should end in time
        for uid, field in fields.items():
            assert field.name.endswith("Time")
            assert field.element.VR == "TM"

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
