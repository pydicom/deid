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

from deid.logger import bot
from pydicom import read_file
from pydicom.tag import tag_in_exception
from pydicom.sequence import Sequence
from pydicom._dicom_dict import (
    DicomDictionary,
    RepeatersDictionary
)
from pydicom.tag import Tag
import os
import re
import sys

################################################################################
# Functions for Finding / Getting Tags
################################################################################

def get_tag(field):
    '''get_tag will return a dictionary with tag indexed by field. For each entry,
       a dictionary lookup is included with VR,  
    
       Parameters
       ==========
       field: the keyword to get tag for, eg "PatientIdentityRemoved"

    '''
    found = [{key:value} for key,value in DicomDictionary.items() if value[4] == field]
    tags = dict()
    if len(found) > 0:

        # (VR, VM, Name, Retired, Keyword
        found = found[0] # shouldn't ever have length > 1
        tag = Tag(list(found)[0])
        VR, VM, longName, retired, keyword = found[tag]

        manifest = {"tag": tag,
                    "VR": VR,
                    "VM":VM,
                    "keyword":keyword,
                    "name":longName }

        tags[field] = manifest 
    return tags


def find_tag(term, VR=None, VM=None, retired=False):
    '''find_tag will search over tags in the DicomDictionary and return the tags found
       to match some term.
    '''
    searchin = DicomDictionary
    if retired:
        searchin = RepeatersDictionary

    found = [value for key,value 
             in searchin.items() 
             if re.search(term,value[4]) or re.search(term,value[2])]

    # Filter by VR, VM, name, these are exact
    if VR is not None: found = _filter_tags(found,0,VR)
    if VM is not None: found = _filter_tags(found,1,VM)
    return found


def _filter_tags(tags, idx, fields=None):
    '''filter tags is a helper function to take some list of tags in the format
       [ (VR, VM, longname, retired, keyword).. ]
       where each of the items above has some index, idx, and filter that index
       down to what is provided in fields.
    '''
    if not isinstance(fields,list):
        fields = [fields]
    return [x for x in tags if x[idx] in fields]



################################################################################
# Manipulating Tags in Data
################################################################################

def remove_sequences(dicom):
    for field in dicom.dir():
        if isinstance(dicom.get(field),Sequence):
            dicom = remove_tag(dicom,field)
    return dicom


def add_tag(dicom, field, value, quiet=False):
    '''add tag will add a tag only if it's in the (active) DicomDictionary

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)
       field: the name of the field to add
       value: the value to set, if name is a valid tag

    '''
    if quiet is False:
        bot.debug("Attempting ADDITION of %s." %(field))
    dicom = change_tag(dicom,field,value)
 
    # dicom.data_element("PatientIdentityRemoved")
    # (0012, 0062) Patient Identity Removed            CS: 'Yes'

    return dicom


def change_tag(dicom, field, value):
    '''change tag is a general function that can be used by 
       update_tag or add_tag. The only difference is the print output,
       and determining to call the function based on different conditions

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)
       field: the name of the field to add
       value: the value to set, if name is a valid tag

    '''
    tag = get_tag(field)

    if field in tag:
        dicom.add_new(tag[field]['tag'], tag[field]['VR'], value) 
    else:
        bot.error("%s is not a valid field to add. Skipping." %(field))

    return dicom


def update_tag(dicom, field, value):
    '''update tag will update a value in the header, if it exists
       if not, nothing is added. This check is the only difference
       between this function and change_tag. 
       If the user wants to add a value (that might not exist) 
       the function add_tag should be used

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)
       field: the name of the field to update
       value: the value to set, if name is a valid tag

    '''
    if field in dicom:
        dicom = change_tag(dicom, field, value)
    return dicom


def blank_tag(dicom, field):
    '''blank tag calls update_tag with value set to an
       empty string. If the tag cannot be found, warns the user
       and doesn't touch (in case of imaging data, or not found)

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)
       field: the name of the field to blank

    '''
    # We cannot blank VR types of US or SS
    element = dicom.data_element(field)
    if element is not None:
        if element.VR not in ['US','SS']:
            return update_tag(dicom, field,"")
        bot.warning('Cannot determine tag for %s, skipping blank.' %field)
    return dicom


def remove_tag(dicom,field):
    '''remove tag will remove a tag if it is present in the dataset

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)
       field: the name of the field to remove

    '''
    if field in dicom:
        tag = dicom.data_element(field).tag
        del dicom[tag]
    return dicom



#########################################################################
# Private Tags
#########################################################################


def get_private(dicom):
    '''get private tags

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)
    '''
    datasets = [dicom]
    private_tags = []
    while len(datasets) > 0:
        ds = datasets.pop(0)
        taglist = sorted(ds.keys())
        for tag in taglist:
            with tag_in_exception(tag):
                if tag in ds:
                    try:
                        data_element = ds[tag]
                        if data_element.tag.is_private:
                            bot.debug(data_element.name)
                            private_tags.append(data_element)
                            if tag in ds and data_element.VR == "SQ":
                                sequence = data_element.value
                                for dataset in sequence:
                                    datasets.append(dataset)                        
                    except IndexError:
                        bot.debug("tag %s key present without value" %tag)
                    except NotImplementedError:
                        bot.debug('tag %s is invalid, skipping' %tag)
    return private_tags


def has_private(dicom):
    '''has_private will return True if the header has private tags

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)

    '''
    private_tags = len(get_private(dicom))
    print("Found %s private tags" %private_tags)
    if private_tags > 0:
        return True
    return False
