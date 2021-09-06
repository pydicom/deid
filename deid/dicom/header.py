"""

header.py: functions to extract identifiers from dicom headers

Copyright (c) 2017-2021 Vanessa Sochat

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

"""


from deid.logger import bot
from deid.utils import read_json

from deid.config import DeidRecipe

from pydicom import read_file

from deid.dicom.utils import save_dicom
from deid.dicom.tags import remove_sequences, get_private
from deid.dicom.groups import extract_values_list, extract_fields_list
from deid.dicom.fields import get_fields
from deid.dicom.parser import DicomParser

import os

here = os.path.dirname(os.path.abspath(__file__))


def get_identifiers(
    dicom_files,
    force=True,
    config=None,
    strip_sequences=False,
    remove_private=False,
    disable_skip=False,
):
    """extract all identifiers from a dicom image.
    This function returns a lookup by file name, where each value indexed
    includes a dictionary of nested fields (indexed by nested tag).

    Parameters
    ==========
    dicom_files: the dicom file(s) to extract from
    force: force reading the file (default True)
    config: if None, uses default in provided module folder
    strip_sequences: if True, remove all sequences
    remove_private: remove private tags
    disable_skip: do not skip over protected fields
    """
    if not isinstance(dicom_files, list):
        dicom_files = [dicom_files]

    bot.debug("Extracting identifiers for %s dicom" % len(dicom_files))
    lookup = dict()

    # Parse each dicom file
    for dicom_file in dicom_files:
        parser = DicomParser(dicom_file, force=force, config=config, disable_skip=False)
        lookup[parser.dicom_file] = parser.get_fields()

    return lookup


def remove_private_identifiers(
    dicom_files, save=True, overwrite=False, output_folder=None, force=True
):

    """remove_private_identifiers is a wrapper for the
    simple call to dicom.remove_private_tags, it simply
    reads in the files for the user and saves accordingly
    """
    updated_files = []
    if not isinstance(dicom_files, list):
        dicom_files = [dicom_files]

    for dicom_file in dicom_files:
        dicom = read_file(dicom_file, force=force)
        dicom.remove_private_tags()
        dicom_name = os.path.basename(dicom_file)
        bot.debug("Removed private identifiers for %s" % dicom_name)

        if save:
            dicom = save_dicom(
                dicom=dicom,
                dicom_file=dicom_file,
                output_folder=output_folder,
                overwrite=overwrite,
            )

        updated_files.append(dicom)
    return updated_files


def replace_identifiers(
    dicom_files,
    ids=None,
    deid=None,
    save=False,
    overwrite=False,
    output_folder=None,
    force=True,
    config=None,
    strip_sequences=False,
    remove_private=False,
    disable_skip=False,
):

    """replace identifiers using pydicom, can be slow when writing
    and saving new files. If you want to replace sequences, they need
    to be extracted with get_identifiers and expand_sequences to True.
    """
    if not isinstance(dicom_files, list):
        dicom_files = [dicom_files]

    # Warn the user that we use the default deid recipe
    if not deid:
        bot.warning("No deid specification provided, will use defaults.")

    # ids (a lookup) is not required
    ids = ids or {}

    # Parse through dicom files, update headers, and save
    updated_files = []
    for dicom_file in dicom_files:
        parser = DicomParser(
            dicom_file,
            force=force,
            config=config,
            recipe=deid,
            disable_skip=disable_skip,
        )

        # If a custom lookup was provided, update the parser
        if parser.dicom_file in ids:
            parser.lookup.update(ids[parser.dicom_file])

        parser.parse(strip_sequences=strip_sequences, remove_private=remove_private)

        # Save to file, otherwise return updated objects
        if save is True:
            ds = save_dicom(
                dicom=parser.dicom,
                dicom_file=parser.dicom_file,
                output_folder=output_folder,
                overwrite=overwrite,
            )
            updated_files.append(ds)
        else:
            updated_files.append(parser.dicom)

    return updated_files
