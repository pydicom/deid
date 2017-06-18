#!/usr/bin/env python

'''
Test dicom tags

The MIT License (MIT)

Copyright (c) 2016-2017 Vanessa Sochat

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

'''

import unittest
import tempfile
import shutil
import json
import os

from deid.utils import get_installdir
from deid.data import get_dataset

class TestDicomTags(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" %self.pwd)
        self.dataset = get_dataset('dicom-cookies')
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")


    def test_add_tag(self):
        print("Test deid.dicom.tags add_tag")
        from deid.dicom.tags import add_tag
        dicom = get_dicom(self.dataset)
        self.assertTrue("PatientIdentityRemoved" not in dicom)
        updated = add_tag(dicom=dicom,field="PatientIdentityRemoved",value="Yes")
        self.assertEqual(updated.get("PatientIdentityRemoved"),"Yes")


    def test_get_tag(self):
        print("Test deid.dicom.tags get_tag")
        from deid.dicom.tags import get_tag
        from pydicom.tag import BaseTag

        print("Case 1: Ask for known tag")
        tag = get_tag("Modality")
        self.assertTrue("Modality" in tag)
        self.assertEqual(tag["Modality"]['VM'],'1')
        self.assertEqual(tag["Modality"]['VR'],'CS')
        self.assertEqual(tag["Modality"]['keyword'],'Modality')
        self.assertEqual(tag["Modality"]['name'],'Modality')
        self.assertTrue(isinstance(tag["Modality"]['tag'],BaseTag))

        print("Case 2: Ask for unknown tag")
        tag = get_tag("KleenexTissue")
        self.assertTrue(len(tag)==0)


    def test_change_tag(self):
        # Note, update_tag only exists to show different print output
        #       so we will not test again.
        print("Test deid.dicom.tags change_tag")
        from deid.dicom.tags import change_tag
        dicom = get_dicom(self.dataset)

        print("Case 1: Change known tag")
        updated = change_tag(dicom,field='PatientID',value="shiny-ham")
        self.assertEqual(updated.get('PatientID'),"shiny-ham")

        print("Case 1: Change unknown tag")
        updated = change_tag(dicom,field='PatientWazaa',value="shiny-ham")
        self.assertEqual(updated.get('PatientWazaa'),None)


    def test_blank_tag(self):
        # Note that outside of the controlled action
        # functions, user is limited on blanking
        # (eg could produce invalid dicom)
        print("Test deid.dicom.tags blank_tag")
        from deid.dicom.tags import blank_tag
        dicom = get_dicom(self.dataset)

        updated = blank_tag(dicom,field='PatientID')
        self.assertEqual(updated.get('PatientID'),"")


    def test_remove_tag(self):
        print("Test deid.dicom.tags remove_tag")
        from deid.dicom.tags import remove_tag
        dicom = get_dicom(self.dataset)
        self.assertTrue('PatientID' in dicom)
        updated = remove_tag(dicom,field='PatientID')
        self.assertTrue("PatientID" not in updated)


def get_dicom(dataset,return_dir=False):
    '''helper function to load a dicom
    '''
    from deid.dicom import get_files
    from pydicom import read_file
    dicom_files = get_files(dataset)
    if return_dir:
        return dicom_files
    return read_file(dicom_files[0])


if __name__ == '__main__':
    unittest.main()
