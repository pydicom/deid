'''

Copyright (c) 2017-2018 Vanessa Sochat

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

'''

import fnmatch
import json
import os
import re
import requests
import tempfile
from deid.logger import bot
from collections import OrderedDict
import sys


# Python less than version 3 must import OSError
if sys.version_info[0] < 3:
    from exceptions import OSError


################################################################################
# Local commands and requests
################################################################################

def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(__file__))


def get_temporary_name(prefix=None, ext=None):
    '''get a temporary name, can be used for a directory or file. This does so
       without creating the file, and adds an optional prefix
  
       Parameters
       ==========
       prefix: if defined, add the prefix after deid
       ext: if defined, return the file extension appended. Do not specify "."
    '''
    deid_prefix = 'deid-'
    if prefix:
        deid_prefix = 'deid-%s-' % prefix

    tmpname = os.path.join(tempfile.gettempdir(), 
                           '%s%s' % (deid_prefix,
                                     next(tempfile._get_candidate_names())))
    if ext:
        tmpname = '%s.%s' % (tmpname, ext)
    return tmpname


################################################################################
## FILE OPERATIONS #############################################################
################################################################################

def write_file(filename, content, mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
       and properly close the file

       Parameters
       ==========
       filename: the name of the file to write to
       content: the content to write to file
       mode: the mode to open the file, defaults to write (w)

    '''
    with open(filename,mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj, filename, mode="w", print_pretty=True):
    '''write_json will (optionally,pretty print) a json object to file

       Parameters
       ==========
       json_obj: the dict to print to json
       filename: the output file to write to
       pretty_print: if True, will use nicer formatting   

    '''
    with open(filename, mode) as filey:
        if print_pretty == True:
            filey.writelines(json.dumps(json_obj, indent=4, separators=(',', ': ')))
        else:
            filey.writelines(json.dumps(json_obj))
    return filename



def read_file(filename, mode="r"):
    '''write_file will open a file, "filename" and write content, "content"
       and properly close the file

       Parameters
       ==========
       filename: the name of the file to write to
       mode: the mode to open the file, defaults to read (r)

    '''
    with open(filename, mode) as filey:
        content = filey.readlines()
    return content



def read_json(filename, mode="r", ordered_dict=False):
    '''read_json will open a file, "filename" and read the string as json

       Parameters
       ==========
       filename: the name of the file to write to
       mode: the mode to open the file, defaults to read (r)
       ordered_dict: If true, return an OrderedDict (default is False)

    '''
    with open(filename,mode) as filey:
        if ordered_dict is False:
            content = json.loads(filey.read())
        else:
            content = json.loads(filey.read(), object_pairs_hook=OrderedDict)
    return content


def recursive_find(base, pattern=None):
    '''recursive find will yield dicom files in all directory levels
       below a base path. It uses get_dcm_files to find the files in the bases.

       Parameters
       ==========
       base: the base directory to search
       pattern: a pattern to match. If None, defaults to "*"

    '''
    if pattern is None:
        pattern = "*"

    for root, dirnames, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)
