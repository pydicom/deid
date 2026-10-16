__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2025, Vanessa Sochat"
__license__ = "MIT"

import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy

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

    def test_save_functions_support_custom_mode_and_private_default(self):
        with tempfile.TemporaryDirectory() as directory:
            cleaner = DicomCleaner.__new__(DicomCleaner)
            cleaner.dicom_file = "synthetic.dcm"
            cleaner.cleaned = numpy.zeros((2, 2, 2), dtype=numpy.uint8)
            cleaner.cmap = "gray"
            dicom = MagicMock()
            dicom.file_meta.TransferSyntaxUID.is_compressed = False
            with patch.object(cleaner, "get_figure"), patch(
                "deid.dicom.pixels.clean.plt.subplots"
            ) as subplots, patch("matplotlib.animation.FuncAnimation"), patch(
                "matplotlib.animation.rcParams", {}, create=True
            ), patch(
                "deid.dicom.pixels.clean.utils.dcmread", return_value=dicom
            ):
                subplots.return_value = (MagicMock(), MagicMock())
                previous_umask = os.umask(0o022)
                try:
                    for method in ("save_png", "save_animation", "save_dicom"):
                        for mode in (None, 0o750):
                            with self.subTest(method=method, mode=mode):
                                output = Path(directory) / f"{method}-{mode}"
                                cleaner.output_folder = str(output)
                                kwargs = {} if mode is None else {"mode": mode}
                                filename = getattr(cleaner, method)(**kwargs)
                                self.assertEqual(Path(filename).parent, output)
                                self.assertEqual(
                                    stat.S_IMODE(output.stat().st_mode),
                                    0o700 if mode is None else mode,
                                )
                                output.chmod(0o755)
                                getattr(cleaner, method)(**kwargs)
                                self.assertEqual(
                                    stat.S_IMODE(output.stat().st_mode), 0o755
                                )
                finally:
                    os.umask(previous_umask)
