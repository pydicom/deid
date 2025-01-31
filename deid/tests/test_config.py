#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.utils import get_installdir


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_load_deid(self):
        print("Case 1: Test loading deid directly")
        from deid.config import load_deid

        config = load_deid(self.deid)
        self.assertTrue("format" in config)

        print("Case 2: Loading from folder")
        config = load_deid(os.path.dirname(self.deid))
        self.assertTrue("format" in config)

        print("Case 3: Testing error on non-existing load of file")
        with self.assertRaises(SystemExit) as cm:
            config = load_deid(os.path.join(self.tmpdir, "deid.doesnt-exist"))
        self.assertEqual(cm.exception.code, 1)

        print("Case 4: Testing load of default deid.")
        config = load_deid(self.tmpdir)

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
        from deid.config import actions, formats, sections

        print("Testing standards: default actions")
        default_actions = [
            "ADD",
            "BLANK",
            "KEEP",
            "REPLACE",
            "REMOVE",
            "JITTER",
            "LABEL",
        ]
        [self.assertTrue(x in actions) for x in default_actions]

        # Should not be any we don't know about
        unknown = [x for x in actions if x not in default_actions]
        self.assertEqual(len(unknown), 0)

        print("Testing standards: allowed sections")
        default_sections = [
            "header",
            "labels",
            "filter",
            "fields",
            "values",
        ]
        [self.assertTrue(x in sections) for x in default_sections]
        unknown = [x for x in sections if x not in default_sections]
        self.assertEqual(len(unknown), 0)

        print("Testing default formats")
        default_formats = ["dicom"]
        [self.assertTrue(x in formats) for x in default_formats]
        unknown = [x for x in formats if x not in default_formats]
        self.assertEqual(len(unknown), 0)


if __name__ == "__main__":
    unittest.main()
