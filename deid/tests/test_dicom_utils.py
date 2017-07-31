#!/usr/bin/env python

'''
Test dicom utils

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

class TestDicomUtils(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" %self.pwd)
        self.dataset = get_dataset('dicom-cookies')
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")


    def test_get_files(self):
        print("Case 1: Test get files from dataset")
        from deid.dicom import get_files
        from deid.config import load_deid
        dicom_files = get_files(self.dataset)
        self.assertEqual(len(dicom_files), 7)

        print("Case 2: Ask for files from empty folder")
        dicom_files = get_files(self.tmpdir)
        self.assertEqual(len(dicom_files), 0)



    def test_parse_action(self):
        print("Testing parse action")
        from deid.dicom.utils import perform_action
        dicom = get_dicom(self.dataset)

        print("Case 1: Testing ADD action")
        self.assertTrue("PatientIdentityRemoved" not in dicom)  
        ADD = {"action":"ADD",
               "field":"PatientIdentityRemoved",
               "value":"Yes"} 

        dicom = perform_action(dicom=dicom,action=ADD)
        self.assertTrue("PatientIdentityRemoved" in dicom)  
        self.assertEqual(dicom.get("PatientIdentityRemoved"),"Yes")

        print("Case 2: Testing REPLACE action with string")
        REPLACE = { "action":"REPLACE",
                    "field":"PatientIdentityRemoved",
                    "value":"No"} 

        dicom = perform_action(dicom=dicom,action=REPLACE)
        self.assertTrue("PatientIdentityRemoved" in dicom)  
        self.assertEqual(dicom.get("PatientIdentityRemoved"),"No")

        print("Case 3: Testing REPLACE action with variable")
        item = {"fish":"stick"}
        REPLACE = { "action":"REPLACE",
                    "field":"PatientIdentityRemoved",
                    "value":"var:fish"} 

        dicom = perform_action(dicom=dicom,action=REPLACE,item=item)
        self.assertEqual(dicom.get("PatientIdentityRemoved"),"stick")

        print("Case 4: Testing REPLACE action with non-existing variable")
        REPLACE = { "action":"REPLACE",
                    "field":"PatientIdentityRemoved",
                    "value":"var:gummybear"} 
        updated = perform_action(dicom=dicom,action=REPLACE,item=item)
        self.assertEqual(updated,None)  

        print("Case 5: Testing REMOVE action")
        REMOVE = { "action":"REMOVE",
                   "field":"PatientIdentityRemoved"} 

        dicom = perform_action(dicom=dicom,action=REMOVE)
        self.assertTrue("PatientIdentityRemoved" not in dicom)  


        print("Case 6: Testing invalid action")
        RUN = { "action":"RUN",
                "field":"PatientIdentityRemoved"} 

        updated = perform_action(dicom=dicom,action=RUN)
        self.assertEqual(updated,None)  


    def test_entity_timestamp(self):
        from deid.dicom.utils import get_entity_timestamp
        print("Testing entity timestamp")
 
        print("Case 1: field is empty returns None")
        dicom = get_dicom(self.dataset)
        ts = get_entity_timestamp(dicom)
        self.assertEqual(ts,None)

        print("Case 2: field not empty")
        dicom.PatientBirthDate = "8/12/1962"
        ts = get_entity_timestamp(dicom)        
        self.assertEqual(ts,'1962-08-12T00:00:00Z')


    def test_item_timestamp(self):
        from deid.dicom.utils import get_item_timestamp
        print("Testing item timestamp")
 
        print("Case 1: field is empty returns None")
        dicom = get_dicom(self.dataset)
        ts = get_item_timestamp(dicom)
        self.assertEqual(ts,None)

        print("Case 2: field not empty")
        from deid.dicom.utils import perform_action
        ADD = {"action":"ADD",
               "field":"InstanceCreationDate",
               "value":"1/1/2010"} 
        dicom = perform_action(action=ADD,dicom=dicom)        
        ts = get_item_timestamp(dicom)        
        self.assertEqual(ts,'2010-01-01T00:00:00Z')



def get_dicom(dataset):
    '''helper function to load a dicom
    '''
    from deid.dicom import get_files
    from pydicom import read_file
    dicom_files = get_files(dataset)
    return read_file(dicom_files[0])


if __name__ == '__main__':
    unittest.main()
