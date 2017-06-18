#!/usr/bin/env python

'''
Test utils

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

from deid.utils import get_installdir
from numpy.testing import (
    assert_array_equal, 
    assert_almost_equal, 
    assert_equal
)

import unittest
import tempfile
import shutil
import json
import os

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")
        

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")


    def test_write_read_files(self):
        '''test_write_read_files will test the functions 
           write_file and read_file
        '''
        print("Testing utils.write_file...")
        from deid.utils import write_file
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_file(tmpfile,"blaaahumbug")
        self.assertTrue(os.path.exists(tmpfile))        

        print("Testing utils.read_file...")
        from deid.utils import read_file
        content = read_file(tmpfile)[0]
        self.assertEqual("blaaahumbug",content)

        from deid.utils import write_json
        print("Testing utils.write_json...")
        print("Case 1: Providing bad json")
        bad_json = {"Wakkawakkawakka'}":[{True},"2",3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)        
        with self.assertRaises(TypeError) as cm:
            write_json(bad_json,tmpfile)

        print("Case 2: Providing good json")        
        good_json = {"Wakkawakkawakka":[True,"2",3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_json(good_json,tmpfile)
        content = json.load(open(tmpfile,'r'))
        self.assertTrue(isinstance(content,dict))
        self.assertTrue("Wakkawakkawakka" in content)


    def test_get_installdir(self):
        '''get install directory should return the base of where singularity
        is installed
        '''
        print("Testing finding the installation directory.")
        from deid.utils import get_installdir
        whereami = get_installdir()
        self.assertTrue(whereami.endswith('deid'))


    def test_recursive_find(self):
        '''test_recursive_find should detect 7 dicoms
        '''
        print("Testing recursive find.")
        from deid.utils import recursive_find
        files = recursive_find(self.pwd,pattern='*.dcm')
        print("Found %s files" %(len(files)))
        self.assertTrue(len(files)==7)


if __name__ == '__main__':
    unittest.main()
