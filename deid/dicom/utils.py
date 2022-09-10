__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import os
import tempfile
import zipfile

from deid.logger import bot
from deid.utils import recursive_find

from .validate import validate_dicoms

################################################################################
# Functions for Dicom files
################################################################################


def get_files(contenders, check=True, pattern=None, force=False, tempdir=None):
    """
    Get a generator for files.

    get_files will take a list of single dicom files or directories,
    and return a generator that yields complete paths to all files

    Parameters
    ==========
    contenders: a list of files or directories (contenders!)
    check: boolean to indicate if we should validate dicoms (default True)
    pattern: A pattern to use with fnmatch. If None, * is used
    force: force reading of the files, if some headers invalid.
           Not recommended, as many non-dicom will come through

    """
    if not isinstance(contenders, list):
        contenders = [contenders]

    for contender in contenders:
        if os.path.isdir(contender):
            dicom_files = recursive_find(contender, pattern=pattern)
        else:
            dicom_files = [contender]

        for dicom_file in dicom_files:
            dfile, dextension = os.path.splitext(dicom_file)
            # The code currently only assumes a single-file per zip.  This could be
            # expanded to allow for multiple test files within an archive.
            if dextension == ".zip":
                with zipfile.ZipFile(dicom_file, "r") as compressedFile:
                    compressedFile.extractall(tempdir)
                    try:
                        dicom_file = next(
                            os.path.join(tempdir, f)
                            for f in os.listdir(tempdir)
                            if os.path.isfile(os.path.join(tempdir, f))
                        )
                    except StopIteration:
                        continue  # ZIP file does not contain any file

            if check:
                validated_files = validate_dicoms(dicom_file, force=force)
            else:
                validated_files = [dicom_file]

            for validated_file in validated_files:
                bot.debug("Found contender file %s" % (validated_file))
                yield validated_file


def save_dicom(dicom, dicom_file, output_folder=None, overwrite=False):
    """
    Save a dicom file to an output folder.

    We make sure to not overwrite unless the user has enforced it

    Parameters
    ==========
    dicom: the pydicon Dataset to save
    dicom_file: the path to the dicom file to save (we only use basename)
    output_folder: the folder to save the file to
    overwrite: overwrite any existing file? (default is False)

    """

    if output_folder is None:
        if overwrite is False:
            output_folder = tempfile.mkdtemp()
        else:
            output_folder = os.path.dirname(dicom_file)

    dicom_name = os.path.basename(dicom_file)
    output_dicom = os.path.join(output_folder, dicom_name)
    dowrite = True
    if overwrite is False:
        if os.path.exists(output_dicom):
            bot.error(
                "%s already exists, overwrite set to False. Not writing." % dicom_name
            )
            dowrite = False

    if dowrite:
        dicom.save_as(output_dicom)
    return output_dicom
