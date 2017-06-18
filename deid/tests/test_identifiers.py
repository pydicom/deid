#!/usr/bin/env python

'''
Test identifiers (across format types)

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
import os


class TestIdentifiers(unittest.TestCase):

    def setUp(self):
        print("\n######################START######################")
        
    def tearDown(self):
        print("\n######################END########################")


    def test_is_number(self):
        print("Test deid.identifiers is_number")
        from deid.identifiers.utils import is_number
        self.assertTrue(is_number(1))
        self.assertTrue(is_number("1")==False)
        self.assertTrue(is_number(1.0))


    def test_get_timestamp(self):
        print("Test deid.identifers get_timestamp")
        from deid.identifiers.utils import get_timestamp

        print("Case 1: Blank date and no time")
        ts = get_timestamp(item_date='')
        self.assertEqual(ts,None)

        print("Case 2: Date and no time")
        ts = get_timestamp(item_date='12/12/2012')
        self.assertEqual(ts,'2012-12-12T00:00:00Z')


if __name__ == '__main__':
    unittest.main()
