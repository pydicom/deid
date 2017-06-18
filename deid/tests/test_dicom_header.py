#!/usr/bin/env python

'''
Test dicom header

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

class TestDicomHeader(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" %self.pwd)
        self.dataset = get_dataset('dicom-cookies')
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")


    def test_get_fields(self):
        print("Case 1: Test get fields from dataset")
        from deid.dicom.header import get_fields        
        dicom = get_dicom(self.dataset)
        fields = get_fields(dicom)
        self.assertEqual(len(fields),28)
        self.assertTrue("PatientID" in fields)


    def test_get_identifiers(self):
        print("Testing deid.dicom get_identifiers")
        from deid.dicom import get_identifiers
        dicom_files = get_dicom(self.dataset,return_dir=True)
        ids = get_identifiers(dicom_files)
        self.assertTrue(len(ids)==1)
        self.assertTrue(isinstance(ids,dict))
        self.assertEqual(len(ids['cookie-47']),7)


    def test_replace_identifiers(self):
        print("Testing deid.dicom replace_identifiers")
        from deid.dicom import replace_identifiers
        from deid.dicom import get_identifiers

        from pydicom import read_file

        dicom_files = get_dicom(self.dataset,return_dir=True)
        ids = get_identifiers(dicom_files)
        
        # Before blanking, 28 fields don't have blanks
        notblanked = read_file(dicom_files[0])
        notblanked_fields = [ x for x in notblanked.dir() 
                                if notblanked.get(x) != ''] # 28
        self.assertTrue(len(notblanked_fields)==28)

        updated_files = replace_identifiers(dicom_files,
                                            output_folder=self.tmpdir)

        # After replacing only 9 don't have blanks
        blanked = read_file(updated_files[0])
        blanked_fields = [ x for x in blanked.dir() if blanked.get(x) != '']
        self.assertTrue(len(blanked_fields)==9)
        


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
