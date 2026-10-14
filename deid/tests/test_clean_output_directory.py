__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2025, Vanessa Sochat"
__license__ = "MIT"

import os
import stat
import tempfile
import unittest
from pathlib import Path

from deid.dicom.pixels.clean import DicomCleaner


@unittest.skipUnless(os.name == "posix", "POSIX permission semantics")
class TestCleanOutputDirectory(unittest.TestCase):
    def test_new_directory_is_private_and_existing_mode_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "cleaned"
            cleaner = DicomCleaner.__new__(DicomCleaner)
            cleaner.output_folder = str(output)
            cleaner.dicom_file = "synthetic.dcm"
            previous_umask = os.umask(0o022)
            try:
                filename = cleaner._get_clean_name(None)
            finally:
                os.umask(previous_umask)
            self.assertEqual(filename, str(output / "cleaned-synthetic.dcm"))
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
            output.chmod(0o750)
            cleaner._get_clean_name(str(output), "png")
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o750)
