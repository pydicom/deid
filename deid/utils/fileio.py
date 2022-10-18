__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import fnmatch
import json
import os
import tempfile
from collections import OrderedDict

################################################################################
# Local commands and requests
################################################################################


def get_installdir():
    """
    Get installation directory of the application
    """
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_temporary_name(prefix=None, ext=None):
    """
    Get a temporary name.

    Get a temporary name, can be used for a directory or file. This does so
    without creating the file, and adds an optional prefix

    Parameters
    ==========
    prefix: if defined, add the prefix after deid
    ext: if defined, return the file extension appended. Do not specify "."
    """
    deid_prefix = "deid-"
    if prefix:
        deid_prefix = "deid-%s-" % prefix

    tmpname = os.path.join(
        tempfile.gettempdir(),
        "%s%s" % (deid_prefix, next(tempfile._get_candidate_names())),
    )
    if ext:
        tmpname = "%s.%s" % (tmpname, ext)
    return tmpname


################################################################################
## FILE OPERATIONS #############################################################
################################################################################


def write_file(filename, content, mode="w"):
    """
    Write to file.

    write_file will open a file, "filename" and write content, "content"
    and properly close the file

    Parameters
    ==========
    filename: the name of the file to write to
    content: the content to write to file
    mode: the mode to open the file, defaults to write (w)
    """
    with open(filename, mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj, filename, mode="w", print_pretty=True):
    """
    Write a json object to file

    Parameters
    ==========
    json_obj: the dict to print to json
    filename: the output file to write to
    pretty_print: if True, will use nicer formatting
    """
    with open(filename, mode) as filey:
        if print_pretty:
            filey.writelines(json.dumps(json_obj, indent=4, separators=(",", ": ")))
        else:
            filey.writelines(json.dumps(json_obj))
    return filename


def read_file(filename, mode="r"):
    """
    Read a file.

    Parameters
    ==========
    filename: the name of the file to write to
    mode: the mode to open the file, defaults to read (r)

    """
    with open(filename, mode) as filey:
        content = filey.readlines()
    return content


def read_json(filename, mode="r", ordered_dict=False):
    """
    Open a file, "filename" and read the string as json

    Parameters
    ==========
    filename: the name of the file to write to
    mode: the mode to open the file, defaults to read (r)
    ordered_dict: If true, return an OrderedDict (default is False)

    """
    with open(filename, mode) as filey:
        if ordered_dict is False:
            content = json.loads(filey.read())
        else:
            content = json.loads(filey.read(), object_pairs_hook=OrderedDict)
    return content


def recursive_find(base, pattern=None):
    """
    Recursively find files that match a pattern.

    recursive find will yield dicom files in all directory levels
    below a base path. It uses get_dcm_files to find the files in the bases.

    Parameters
    ==========
    base: the base directory to search
    pattern: a pattern to match. If None, defaults to "*"

    """
    if pattern is None:
        pattern = "*"

    for root, _, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)


################################################################################
## DATA FORMATS ################################################################
################################################################################


def to_int(value):
    """
    Convert a value (value) to int, if found to be otherwise
    """
    if not isinstance(value, int):
        value = int(float(value))
    return value


def is_number(value):
    """
    Determine if the value for a field is numeric
    """
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return True
    return False
