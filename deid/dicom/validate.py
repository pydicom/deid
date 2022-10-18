__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

from pydicom import read_file

from deid.logger import bot


def validate_dicoms(dcm_files, force=False):
    """
    Validate that dicom files can open and return valid set.

    validate dicoms will test opening one or more dicom files,
    and return a list of valid files.

    Parameters
    ==========
    dcm_files: one or more dicom files to test

    """
    if not isinstance(dcm_files, list):
        dcm_files = [dcm_files]

    valids = []

    bot.debug("Checking %s dicom files for validation." % (len(dcm_files)))
    for dcm_file in dcm_files:

        try:
            with open(dcm_file, "rb") as filey:
                read_file(filey, force=force)
            valids.append(dcm_file)
        except Exception:
            bot.warning("Cannot read input file {0!s}, skipping.".format(dcm_file))

    bot.debug("Found %s valid dicom files" % (len(valids)))
    return valids
