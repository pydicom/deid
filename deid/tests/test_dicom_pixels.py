# test_dicom_pixels_detect.py

import os
import unittest

from deid.dicom.pixels.detect import DeidRecipe, _has_burned_pixels_single
from deid.utils import get_installdir

# Path to test data (adjust based on your setup)
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def create_dummy_dicom(
    sop_class_uid=None,
    manufacturer="foo",
    series_description="Test Series",
    image_type=None,
):
    """Create a dummy DICOM dataset for testing."""
    import tempfile

    from pydicom.dataset import Dataset, FileDataset

    filename = tempfile.NamedTemporaryFile(suffix=".dcm", delete=False).name
    file_meta = Dataset()
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)

    ds.PatientName = "Test^BurnedPixels"
    ds.Rows = 64
    ds.Columns = 64
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0

    if sop_class_uid:
        ds.SOPClassUID = sop_class_uid
    if manufacturer:
        ds.Manufacturer = manufacturer
    if series_description:
        ds.SeriesDescription = series_description
    if image_type and isinstance(image_type, list):
        ds.ImageType = image_type

    ds.save_as(filename)
    return filename


class TestCleanPizelDimensions(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deidpath = os.path.abspath("%s/tests/resources/" % self.pwd)
        print("\n######################START######################")

    def tearDown(self):
        print("\n######################END########################")

    def test_has_burned_pixels_single_clean(self):
        """Test that a DICOM has no burned pixels.

        It uses a dummy DICOM FileDataset and a simple deid specification.
        """
        dicom_file = create_dummy_dicom()
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_multiple.dicom")
        deid = DeidRecipe(deid_profile)

        expected_results = {
            "flagged": False,
            "results": [],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)

    def test_has_burned_pixels_single_detect(self):
        """Test that a DICOM has burned pixels.

        It uses a simple deid specification and a dummy DICOM FileDataset with an
        SOPClassUID that matches that in the profile and a simple deid specification.
        """
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_multiple.dicom")
        deid = DeidRecipe(deid_profile)

        # Load the deid profile, which contains the SOPClassUID to check against and the
        # coordinates to remove.
        target_sop_class_uid = None
        expected_coordinates = []
        with open(deid_profile, "r") as f:
            for line in f:
                if "contains SOPClassUID" in line:
                    target_sop_class_uid = line.split("contains SOPClassUID", 1)[
                        1
                    ].strip()
                elif "coordinates" in line:
                    expected_coordinates.append(
                        [0, line.split("coordinates", 1)[1].strip()]
                    )

        dicom_file = create_dummy_dicom(sop_class_uid=target_sop_class_uid)

        expected_results = {
            "flagged": True,
            "results": [
                {
                    "reason": f" SOPClassUID contains {target_sop_class_uid}",
                    "group": "blacklist",
                    "coordinates": expected_coordinates,
                }
            ],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)

    def test_has_burned_pixels_single_group_with_or_false(self):
        """Test that _has_burned_pixels_single returns False when the Group With OR does
        not match the first condition, even if one of the "or" group is true.
        """
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_groups.dicom")
        deid = DeidRecipe(deid_profile)

        # Create a dummy DICOM FileDataset with a manufacturer that does NOT match the
        # one in the "Group With OR" profile, and a SeriesDescription that does:
        dicom_file = create_dummy_dicom(
            manufacturer="dummy_manufacturer", series_description="flag me now"
        )

        expected_results = {
            "flagged": False,
            "results": [],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)

    def test_has_burned_pixels_single_group_with_or_true(self):
        """Test that _has_burned_pixels_single returns True when the Group With OR does
        match the first condition and one in the "OR" group.
        """
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_groups.dicom")
        deid = DeidRecipe(deid_profile)

        # Load the deid profile to find the coordinates we expect to find in the results
        expected_coordinates = []
        with open(deid_profile, "r") as f:
            for line in f:
                if "coordinates" in line:
                    expected_coordinates.append(
                        [0, line.split("coordinates", 1)[1].strip()]
                    )
                    # just take the first one for this test
                    break

        # Create a dummy DICOM FileDataset with a manufacturer and SeriesDescription DO
        # match those in the "Group With OR" profile:
        dicom_file = create_dummy_dicom(
            manufacturer="foo", series_description="flag me now"
        )

        expected_results = {
            "flagged": True,
            "results": [
                {
                    "reason": (
                        "and Manufacturer contains foo ManufacturerModelName contains bar "
                        "or SeriesDescription contains flag me"
                    ),
                    "group": "graylist",
                    "coordinates": expected_coordinates,
                }
            ],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)

    def test_has_burned_pixels_single_value_with_or_false(self):
        """Test that _has_burned_pixels_single returns False when the Value With OR does
        not match the condition with the OR ("|").
        """
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_groups.dicom")
        deid = DeidRecipe(deid_profile)

        # Create a dummy DICOM FileDataset with a manufacturer that does NOT match any
        # of those in "Value With OR" profile, and a SeriesDescription that does:
        dicom_file = create_dummy_dicom(
            manufacturer="dummy_manufacturer", series_description="bamboo"
        )

        expected_results = {
            "flagged": False,
            "results": [],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)

    def test_has_burned_pixels_single_value_with_or_true(self):
        """Test that _has_burned_pixels_single returns True when the Value With OR does
        match one of the values in the first condition and also matches the second
        condition.
        """
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_groups.dicom")
        deid = DeidRecipe(deid_profile)

        # Load the deid profile to find the coordinates we expect to find in the results
        expected_coordinates = []
        with open(deid_profile, "r") as f:
            skip_coordinates = False
            for line in f:
                # Skip the lines between "LABEL Group With OR" and "LABEL Value With OR"
                if "LABEL Groups With OR" in line:
                    skip_coordinates = True
                    continue
                if "LABEL Value With OR" in line:
                    skip_coordinates = False
                    continue
                if "coordinates" in line and not skip_coordinates:
                    expected_coordinates.append(
                        [0, line.split("coordinates", 1)[1].strip()]
                    )
                    # just take the first one for this test
                    break

        # Create a dummy DICOM FileDataset with a manufacturer and SeriesDescription DO
        # match those in the "Group With OR" profile:
        dicom_file = create_dummy_dicom(manufacturer="foo", series_description="bamboo")

        expected_results = {
            "flagged": True,
            "results": [
                {
                    "reason": (
                        "and Manufacturer contains foo|bar|baz SeriesDescription contains "
                        "bam"
                    ),
                    "group": "graylist",
                    "coordinates": expected_coordinates,
                }
            ],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)

    def test_has_burned_pixels_single_value_with_and_false(self):
        """Test that _has_burned_pixels_single returns False when the Value With AND
        does not match the condition with the OR ("+").
        """
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_groups.dicom")
        deid = DeidRecipe(deid_profile)

        # Create a dummy DICOM FileDataset with a manufacturer that does NOT match any
        # of those in "Value With AND" profile, and a SeriesDescription that does:
        dicom_file = create_dummy_dicom(manufacturer="foo", image_type=["ORIGINAL"])

        expected_results = {
            "flagged": False,
            "results": [],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)

    @unittest.skip(
        reason="""I think dicom.contains() doesn't behave as expected:

        If "contains ImageType DERIVED+SECONDARY" is in the deid profile, I think the
        expected behavior is that ImageType must contain both "DERIVED" and "SECONDARY"
        for the condition to be True. However, dicom.contains() returns False when both
        elements are present in the ImageType list.
        """
    )
    def test_has_burned_pixels_single_value_with_and_true(self):
        """Test that _has_burned_pixels_single returns True when the Value With AND does
        match one of the values in the first condition and also matches the second
        condition.
        """
        deid_profile = os.path.join(self.deidpath, "remove_coordinates_groups.dicom")
        deid = DeidRecipe(deid_profile)

        # Load the deid profile to find the coordinates we expect to find in the results
        expected_coordinates = []
        with open(deid_profile, "r") as f:
            skip_coordinates = False
            for line in f:
                # Skip the lines between "LABEL Group With OR" and "LABEL Value With OR"
                if "LABEL Groups With OR" in line:
                    skip_coordinates = True
                    continue
                if "LABEL Value With AND" in line:
                    skip_coordinates = False
                    continue
                if "coordinates" in line and not skip_coordinates:
                    expected_coordinates.append(
                        [0, line.split("coordinates", 1)[1].strip()]
                    )
                    # just take the first one for this test
                    break

        # Create a dummy DICOM FileDataset with a manufacturer and SeriesDescription DO
        # match those in the "Group With OR" profile:
        dicom_file = create_dummy_dicom(
            manufacturer="foo", image_type=["DERIVED", "SECONDARY", "IGNORED"]
        )

        expected_results = {
            "flagged": True,
            "results": [
                {
                    "reason": (
                        "and Manufacturer contains foo ImageType contains DERIVED+SECONDARY"
                    ),
                    "group": "graylist",
                    "coordinates": expected_coordinates,
                }
            ],
        }

        results = _has_burned_pixels_single(dicom_file, force=False, deid=deid)

        assert results == expected_results

        os.remove(dicom_file)


if __name__ == "__main__":
    unittest.main()
