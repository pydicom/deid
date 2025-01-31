#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.data import get_dataset
from deid.dicom import replace_identifiers, utils
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

    def run_blank_test(self, VR, Field, Expected):
        print(f"Test BLANK {VR}")
        dicom_file = get_file(self.dataset)

        actions = [
            {"action": "BLANK", "field": Field},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[Field].value
        currentVR = inputfile[Field].VR

        self.assertNotEqual(None, currentValue)
        self.assertNotEqual("", currentValue)
        self.assertEqual(VR, currentVR)

        result = replace_identifiers(
            dicom_files=dicom_file,
            deid=recipe,
            save=True,
            remove_private=False,
            strip_sequences=False,
        )

        outputfile = utils.dcmread(result[0])
        self.assertEqual(1, len(result))
        self.assertEqual(Expected, outputfile[Field].value)

    def test_blank_AE(self):
        self.run_blank_test("AE", "NetworkID", "")

    def test_blank_AS(self):
        self.run_blank_test("AS", "PatientAge", "")

    def test_blank_AT(self):
        self.run_blank_test("AT", "00110004", None)

    def test_blank_CS(self):
        self.run_blank_test("CS", "BodyPartExamined", "")

    def test_blank_DA(self):
        self.run_blank_test("DA", "StudyDate", "")

    def test_blank_DS(self):
        self.run_blank_test("DS", "PatientWeight", None)

    def test_blank_DT(self):
        self.run_blank_test("DT", "AcquisitionDateTime", "")

    def test_blank_FD(self):
        self.run_blank_test("FD", "SingleCollimationWidth", None)

    def test_blank_FL(self):
        self.run_blank_test("FL", "CalciumScoringMassFactorDevice", None)

    def test_blank_IS(self):
        self.run_blank_test("IS", "Exposure", None)

    def test_blank_LO(self):
        self.run_blank_test("LO", "PatientID", "")

    def test_blank_LT(self):
        self.run_blank_test("LT", "AdditionalPatientHistory", "")

    def test_blank_OB(self):
        self.run_blank_test("OB", "00110011", None)

    def test_blank_OD(self):
        self.run_blank_test("OD", "00110012", None)

    def test_blank_OF(self):
        self.run_blank_test("OF", "00110013", None)

    def test_blank_OL(self):
        self.run_blank_test("OL", "00110014", None)

    def test_blank_OV(self):
        self.run_blank_test("OV", "00110016", None)

    def test_blank_OW(self):
        self.run_blank_test("OW", "00110015", None)

    def test_blank_PN(self):
        self.run_blank_test("PN", "ReferringPhysicianName", "")

    def test_blank_SH(self):
        self.run_blank_test("SH", "AccessionNumber", "")

    def test_blank_SL(self):
        self.run_blank_test("SL", "00110001", None)

    def test_blank_SQ(self):
        self.run_blank_test("SQ", "ProcedureCodeSequence", [])

    def test_blank_SS(self):
        self.run_blank_test("SS", "00110002", None)

    def test_blank_ST(self):
        self.run_blank_test("ST", "InstitutionAddress", "")

    def test_blank_SV(self):
        self.run_blank_test("SV", "00110007", None)

    def test_blank_TM(self):
        self.run_blank_test("TM", "StudyTime", "")

    def test_blank_UC(self):
        self.run_blank_test("UC", "00110009", "")

    def test_blank_UI(self):
        self.run_blank_test("UI", "FrameOfReferenceUID", "")

    def test_blank_UL(self):
        self.run_blank_test("UL", "00311101", None)

    def test_blank_UN(self):
        self.run_blank_test("UN", "00110003", None)

    def test_blank_UR(self):
        self.run_blank_test("UR", "00110008", "")

    def test_blank_US(self):
        self.run_blank_test("US", "PregnancyStatus", None)

    def test_blank_UT(self):
        self.run_blank_test("UT", "00291022", "")

    def test_blank_UV(self):
        self.run_blank_test("UV", "00110010", None)


if __name__ == "__main__":
    unittest.main()
