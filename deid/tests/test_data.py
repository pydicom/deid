#!/usr/bin/env python

'''
Test data functions

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

class TestUtils(unittest.TestCase):

    def setUp(self):
        print("\n######################START######################")
        
    def tearDown(self):
        print("\n######################END########################")


    def test_get_dataset(self):
        '''test_get_dataset will make sure we can load provided datasets
        '''
        print("Case 1: Ask for existing dataset.")
        from deid.data import get_dataset
        dataset = get_dataset('dicom-cookies')        
        self.assertTrue(os.path.exists(dataset))        

        print("Case 2: Ask for non existing dataset")
        dataset = get_dataset('other-cookies')        
        self.assertEqual(dataset,None)        


if __name__ == '__main__':
    unittest.main()
