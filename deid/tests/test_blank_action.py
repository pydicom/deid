#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import os
import shutil
import tempfile
import unittest

from pydicom import read_file

from deid.data import get_dataset
from deid.dicom import replace_identifiers
from deid.tests.common import create_recipe, get_file
from deid.utils import get_installdir

global generate_uid


class TestBlankAction(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_blank_VR(self):
        """
        Loops through all VR Types testing the blank action on a field of each VR.
        """

        fieldList = [
            {"VR": "AE", "Field": "NetworkID", "Expected": ""},
            {"VR": "AS", "Field": "PatientAge", "Expected": ""},
            {"VR": "AT", "Field": "00110004", "Expected": None},
            {"VR": "CS", "Field": "BodyPartExamined", "Expected": ""},
            {"VR": "DA", "Field": "StudyDate", "Expected": ""},
            {"VR": "DS", "Field": "PatientWeight", "Expected": None},
            {"VR": "DT", "Field": "AcquisitionDateTime", "Expected": ""},
            {"VR": "FD", "Field": "SingleCollimationWidth", "Expected": None},
            {"VR": "FL", "Field": "CalciumScoringMassFactorDevice", "Expected": None},
            {"VR": "IS", "Field": "Exposure", "Expected": None},
            {"VR": "LO", "Field": "PatientID", "Expected": ""},
            {"VR": "LT", "Field": "AdditionalPatientHistory", "Expected": ""},
            {"VR": "OB", "Field": "00110011", "Expected": None},
            {"VR": "OD", "Field": "00110012", "Expected": None},
            {"VR": "OF", "Field": "00110013", "Expected": None},
            {"VR": "OL", "Field": "00110014", "Expected": None},
            {"VR": "OV", "Field": "00110015", "Expected": None},
            {"VR": "OW", "Field": "00110016", "Expected": None},
            {"VR": "PN", "Field": "ReferringPhysicianName", "Expected": ""},
            {"VR": "SH", "Field": "AccessionNumber", "Expected": ""},
            {"VR": "SL", "Field": "00110001", "Expected": None},
            {"VR": "SQ", "Field": "ProcedureCodeSequence", "Expected": []},
            {"VR": "SS", "Field": "00110002", "Expected": None},
            {"VR": "ST", "Field": "InstitutionAddress", "Expected": ""},
            {"VR": "SV", "Field": "00110007", "Expected": None},
            {"VR": "TM", "Field": "StudyTime", "Expected": ""},
            {"VR": "UC", "Field": "00110009", "Expected": ""},
            {"VR": "UI", "Field": "FrameOfReferenceUID", "Expected": ""},
            {"VR": "UL", "Field": "00311101", "Expected": None},
            {"VR": "UN", "Field": "00110003", "Expected": None},
            {"VR": "UR", "Field": "00110008", "Expected": ""},
            {"VR": "US", "Field": "PregnancyStatus", "Expected": None},
            {"VR": "UT", "Field": "00291022", "Expected": ""},
            {"VR": "UV", "Field": "00110010", "Expected": None},
        ]

        for field in fieldList:
            currentfield = field["Field"]
            currentVR = field["VR"]
            currentExpected = field["Expected"]

            print(f"Test BLANK {currentVR}")
            dicom_file = get_file(self.dataset)

            actions = [
                {"action": "BLANK", "field": currentfield},
            ]
            recipe = create_recipe(actions)

            inputfile = read_file(dicom_file)
            currentValue = inputfile[currentfield].value

            self.assertNotEqual(None, currentValue)
            self.assertNotEqual("", currentValue)

            result = replace_identifiers(
                dicom_files=dicom_file,
                deid=recipe,
                save=True,
                remove_private=False,
                strip_sequences=False,
            )

            outputfile = read_file(result[0])
            self.assertEqual(1, len(result))
            self.assertEqual(currentExpected, outputfile[currentfield].value)


if __name__ == "__main__":
    unittest.main()
