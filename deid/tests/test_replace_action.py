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


class TestReplaceAction(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.dataset = get_dataset("humans")
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def run_replace_test(self, VR, Field, newValue, expected=None):
        print(f"Test REPLACE {VR}")
        dicom_file = get_file(self.dataset)

        if expected is None:
            expected = newValue

        actions = [
            {"action": "REPLACE", "field": Field, "value": newValue},
        ]
        recipe = create_recipe(actions)

        inputfile = utils.dcmread(dicom_file)
        currentValue = inputfile[Field].value
        currentVR = inputfile[Field].VR

        self.assertNotEqual(newValue, currentValue)
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
        self.assertEqual(expected, outputfile[Field].value)

    def test_replace_AE(self):
        self.run_replace_test("AE", "NetworkID", "TEST_AE")

    def test_replace_AS(self):
        self.run_replace_test("AS", "PatientAge", "TEST_AS")

    def test_replace_AT(self):
        self.run_replace_test("AT", "00110004", "00110077")

    def test_replace_CS(self):
        self.run_replace_test("CS", "BodyPartExamined", "TEST_CS")

    def test_replace_DA(self):
        self.run_replace_test("DA", "StudyDate", "19000101")

    def test_replace_DS(self):
        self.run_replace_test("DS", "PatientWeight", "501")

    def test_replace_DT(self):
        self.run_replace_test("DT", "AcquisitionDateTime", "19000101012421.621000")

    def test_replace_FD(self):
        self.run_replace_test("FD", "SingleCollimationWidth", "1.3", 1.3)

    def test_replace_FL(self):
        self.run_replace_test(
            "FL",
            "CalciumScoringMassFactorDevice",
            "0.7799999713897705",
            float("0.7799999713897705"),
        )

    def test_replace_IS(self):
        self.run_replace_test("IS", "Exposure", "400")

    def test_replace_LO(self):
        self.run_replace_test("LO", "PatientID", "TEST_LO")

    def test_replace_LT(self):
        self.run_replace_test("LT", "AdditionalPatientHistory", "TEST_LT")

    def test_replace_OB_fake_test(self):
        # Should this be implemented or should this be excluded from REPLACE?
        #    self.run_replace_test("OB", "00110011", ??????)
        self.assertTrue(True)

    def test_replace_OD_fake_test(self):
        # Should this be implemented or should this be excluded from REPLACE?
        #    self.run_replace_test("OD", "00110012", ??????)
        self.assertTrue(True)

    def test_replace_OF_fake_test(self):
        # Should this be implemented or should this be excluded from REPLACE?
        #    self.run_replace_test("OF", "00110013", ??????)
        self.assertTrue(True)

    def test_replace_OL_fake_test(self):
        # Should this be implemented or should this be excluded from REPLACE?
        #    self.run_replace_test("OL", "00110014", ??????)
        self.assertTrue(True)

    def test_replace_OV_fake_test(self):
        # Should this be implemented or should this be excluded from REPLACE?
        #    self.run_replace_test("OV", "00110015", ??????)
        self.assertTrue(True)

    def test_replace_OW_fake_test(self):
        # Should this be implemented or should this be excluded from REPLACE?
        #    self.run_replace_test("OW", "00110016", ??????)
        self.assertTrue(True)

    def test_replace_PN(self):
        self.run_replace_test("PN", "ReferringPhysicianName", "TEST_PN")

    def test_replace_SH(self):
        self.run_replace_test("SH", "AccessionNumber", "TEST_SH")

    def test_replace_SL(self):
        self.run_replace_test("SL", "00110001", "112345", 112345)

    def test_replace_SQ_fake_test(self):
        # Should this be implemented or should this be excluded from REPLACE?
        #    self.run_replace_test("SQ", "ProcedureCodeSequence, ??????)
        self.assertTrue(True)

    def test_replace_SS(self):
        self.run_replace_test("SS", "00110002", "1123", 1123)

    def test_replace_ST(self):
        self.run_replace_test("ST", "InstitutionAddress", "TEST_ST")

    def test_replace_SV(self):
        self.run_replace_test("SV", "00110007", "-12345677", -12345677)

    def test_replace_TM(self):
        self.run_replace_test("TM", "StudyTime", "010101.621000")

    def test_replace_UC(self):
        self.run_replace_test("UC", "00110009", "TEST_UC")

    def test_replace_UI(self):
        self.run_replace_test("UI", "FrameOfReferenceUID", "1.2.840.10008.5.1.4.1.1.7")

    def test_replace_UL(self):
        self.run_replace_test("UL", "00311101", "888888", 888888)

    def test_replace_UN(self):
        self.run_replace_test(
            "UN", "00110003", "x0000000001", bytes("x0000000001", "utf-8")
        )

    def test_replace_UR(self):
        self.run_replace_test("UR", "00110008", "http://example.com?q=2")

    def test_replace_US(self):
        self.run_replace_test("US", "PregnancyStatus", "410", 410)

    def test_replace_UT(self):
        self.run_replace_test("UT", "00291022", "TEST_UT")

    def test_replace_UV(self):
        self.run_replace_test("UV", "00110010", "1844674407", 1844674407)


if __name__ == "__main__":
    unittest.main()
