import contextlib
import os
import tempfile
import unittest

from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid

from deid.config import DeidRecipe
from deid.dicom.header import get_identifiers, replace_identifiers


@contextlib.contextmanager
def temporary_recipe(recipe_text: str):
    """
    Create a temporary recipe file for testing.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as recipe_file:
        recipe_file.write(recipe_text.encode())
        recipe_file.flush()
        recipe = DeidRecipe(deid=recipe_file.name, base=False)
        yield recipe


def hashuid(item, value, field, dicom, element_name=None):
    """
    Generate a new UID based on the previous UID
    """
    if hasattr(field, "element"):
        hash_src = str(field.element.value)
    else:
        hash_src = field
    new_uid = generate_uid(entropy_srcs=[hash_src])
    return new_uid


class TestNestedDicomFields(unittest.TestCase):
    def setUp(self):
        print("\n######################START######################")

    def tearDown(self):
        print("\n######################END########################")

    def test_nested_dicom_fields(self):
        """
        Tests that header deidentification does not overwrite existing top-level tags
        when iterating over deeply nested tags.
        """
        # Create a mock DICOM dataset with a top-level and nested SeriesInstanceUID
        original_dicom = Dataset()
        original_dicom.SeriesInstanceUID = generate_uid()

        referenced_series = Dataset()
        referenced_series.SeriesInstanceUID = generate_uid()

        original_dicom.ReferencedSeriesSequence = Sequence([referenced_series])

        # Enforce precondition that the two SeriesInstanceUID attributes are different
        self.assertNotEqual(
            original_dicom.ReferencedSeriesSequence[0].SeriesInstanceUID,
            original_dicom.SeriesInstanceUID,
        )

        recipe_text = """
        FORMAT dicom
        %header
        REPLACE SeriesInstanceUID func:hashuid
        """

        with (
            tempfile.TemporaryDirectory() as temp_dir,
            temporary_recipe(recipe_text) as recipe,
        ):
            temp_file_name = os.path.join(temp_dir, "input.dcm")
            original_dicom.save_as(temp_file_name, implicit_vr=True, little_endian=True)
            dicom_paths = [temp_file_name]

            # Add hash function to deid context
            ids = get_identifiers(dicom_paths)
            for dicom_id in ids:
                ids[dicom_id]["hashuid"] = hashuid

            os.makedirs(os.path.join(temp_dir, "out"))
            output_paths = replace_identifiers(
                dicom_paths,
                ids=ids,
                deid=recipe,
                save=True,
                overwrite=True,
                output_folder=os.path.join(temp_dir, "out"),
            )

            output_dataset = dcmread(output_paths[0], force=True)
            # Assert that the SeriesInstanceUID has been replaced
            self.assertNotEqual(
                output_dataset.SeriesInstanceUID, original_dicom.SeriesInstanceUID
            )
            # Assert that the two unique UIDs were deidentified to different values
            self.assertNotEqual(
                output_dataset.ReferencedSeriesSequence[0].SeriesInstanceUID,
                output_dataset.SeriesInstanceUID,
            )
