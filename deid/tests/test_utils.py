#!/usr/bin/env python

import json
import os
import shutil
import tempfile
import unittest

from deid.utils import get_installdir


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_get_temporary_name(self):
        """test_get_temporary_name will test the generation of a temporary
        file name.
        """
        from deid.utils import get_temporary_name

        print("Testing utils.get_temporary_name...")
        tmpname = get_temporary_name()
        self.assertTrue(not os.path.exists(tmpname))
        self.assertTrue("deid" in tmpname)
        tmpname = get_temporary_name(prefix="clean")
        self.assertTrue("deid-clean" in tmpname)
        tmpname = get_temporary_name(ext=".dcm")
        self.assertTrue(tmpname.endswith(".dcm"))

    def test_write_read_files(self):
        """test_write_read_files will test the functions
        write_file and read_file
        """
        print("Testing utils.write_file...")
        from deid.utils import write_file

        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_file(tmpfile, "blaaahumbug")
        self.assertTrue(os.path.exists(tmpfile))

        print("Testing utils.read_file...")
        from deid.utils import read_file

        content = read_file(tmpfile)[0]
        self.assertEqual("blaaahumbug", content)

        from deid.utils import write_json

        print("Testing utils.write_json...")
        print("Case 1: Providing bad json")
        bad_json = {"Wakkawakkawakka'}": [{True}, "2", 3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        with self.assertRaises(TypeError):
            write_json(bad_json, tmpfile)

        print("Case 2: Providing good json")
        good_json = {"Wakkawakkawakka": [True, "2", 3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_json(good_json, tmpfile)
        with open(tmpfile, "r") as fd:
            content = json.loads(fd.read())
        self.assertTrue(isinstance(content, dict))
        self.assertTrue("Wakkawakkawakka" in content)

    def test_get_installdir(self):
        """get install directory should return the base of where singularity
        is installed
        """
        print("Testing finding the installation directory.")
        from deid.utils import get_installdir

        whereami = get_installdir()
        self.assertTrue(whereami.endswith("deid"))

    def test_recursive_find(self):
        """test_recursive_find should detect 7 dicoms"""
        print("Testing recursive find.")
        from deid.utils import recursive_find

        expected = 3
        found = len(list(recursive_find(self.pwd, pattern="deid*")))
        print("Found %s deid files" % (found))
        self.assertTrue(found == expected)


if __name__ == "__main__":
    unittest.main()
