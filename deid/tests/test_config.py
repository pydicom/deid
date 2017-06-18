#!/usr/bin/env python

'''
Test config (deid) parsing functions

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

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" %self.pwd)
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")


    def test_load_deid(self):
        print("Case 1: Test loading deid directly")
        from deid.config import load_deid
        config = load_deid(self.deid)        
        self.assertTrue('format' in config)        

        print("Case 2: Loading from folder")
        config = load_deid(os.path.dirname(self.deid))        
        self.assertTrue('format' in config)        

        print("Case 3: Testing error on non-existing load")
        with self.assertRaises(SystemExit) as cm:
            config = load_deid(self.tmpdir)        
        self.assertEqual(cm.exception.code, 1)


    def test_find_deid(self):

        print("Testing finding deid file, referencing directly.")
        from deid.config.utils import find_deid
        config_file = find_deid(self.deid)
        self.assertTrue(os.path.exists(config_file))  

        print("Testing finding deid file in folder")
        from deid.config.utils import find_deid
        config_file = find_deid(os.path.dirname(self.deid))
        self.assertTrue(os.path.exists(config_file))  


    def test_standards(self):
        from deid.config import actions, sections, formats

        print("Testing standards: default actions")
        default_actions = ["ADD","BLANK","KEEP","REPLACE","REMOVE"]
        [self.assertTrue(x in actions) for x in default_actions]
        
        # Should not be any we don't know about
        unknown = [x for x in actions if x not in default_actions]
        self.assertEqual(len(unknown),0)

        print("Testing standards: allowed sections")
        default_sections = ["header","pixels","labels"]
        [self.assertTrue(x in sections) for x in default_sections]
        unknown = [x for x in sections if x not in default_sections]
        self.assertEqual(len(unknown),0)


        print("Testing default formats")
        default_formats = ["dicom"]
        [self.assertTrue(x in formats) for x in default_formats]
        unknown = [x for x in formats if x not in default_formats]
        self.assertEqual(len(unknown),0)


if __name__ == '__main__':
    unittest.main()
