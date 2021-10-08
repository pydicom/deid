"""

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
from pydicom import read_file


def validate_dicoms(dcm_files, force=False):
    """validate dicoms will test opening one or more dicom files,
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
