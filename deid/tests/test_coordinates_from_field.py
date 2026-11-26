__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2025, Vanessa Sochat"
__license__ = "MIT"

import os
import unittest

from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence

from deid.config import DeidRecipe
from deid.dicom import DicomCleaner
from deid.dicom.pixels import has_burned_pixels
from deid.utils import get_installdir


def create_ultrasound_dicom(x0, y0, x1, y1):
    """Create an in-memory dataset with one ultrasound region."""
    region = Dataset()
    region.RegionLocationMinX0 = x0
    region.RegionLocationMinY0 = y0
    region.RegionLocationMaxX1 = x1
    region.RegionLocationMaxY1 = y1

    ds = FileDataset("us.dcm", {}, file_meta=Dataset(), preamble=b"\0" * 128)
    ds.SequenceOfUltrasoundRegions = Sequence([region])
    return ds


class TestCoordinatesFromField(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath(
            "%s/tests/resources/keepcoordinates_from.dicom" % self.pwd
        )
        self.first = create_ultrasound_dicom(0, 0, 8, 8)
        self.second = create_ultrasound_dicom(16, 16, 32, 32)

    def test_reused_recipe_extracts_coordinates_per_image(self):
        """A reused recipe should read "from:" coordinates from each image."""
        recipe = DeidRecipe(self.deid)

        first = has_burned_pixels(self.first, deid=recipe)
        second = has_burned_pixels(self.second, deid=recipe)

        self.assertEqual(
            first["results"][0]["coordinates"], [[0, "all"], [1, ["0,0,8,8"]]]
        )
        self.assertEqual(
            second["results"][0]["coordinates"], [[0, "all"], [1, ["16,16,32,32"]]]
        )
        self.assertEqual(
            recipe.get_filters("graylist")[0]["coordinates"],
            [[0, "all"], [1, "from:SequenceOfUltrasoundRegions"]],
        )

    def test_reused_cleaner_extracts_coordinates_per_image(self):
        """A reused DicomCleaner should read "from:" coordinates from each image."""
        client = DicomCleaner(deid=self.deid)

        client.detect(self.first)
        second = client.detect(self.second)

        self.assertEqual(
            second["results"][0]["coordinates"], [[0, "all"], [1, ["16,16,32,32"]]]
        )


if __name__ == "__main__":
    unittest.main()
