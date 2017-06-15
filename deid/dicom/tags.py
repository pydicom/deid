'''
tags.py: working with header field tags

Copyright (c) 2017 Vanessa Sochat

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
from pydicom._dicom_dict import DicomDictionary
from pydicom.tag import Tag
import os
import sys

#########################################################################
# Functions for Single Dicom files
#########################################################################

def add_tag(dicom,field,value):
    '''add tag will add a tag only if it's in the (active) DicomDictionary
    :param dicom: the pydicom.dataset Dataset (pydicom.read_file)
    :param field: the name of the field to add
    :param value: the value to set, if name is a valid tag
    '''
    dicom_file = os.path.basename(dicom.filename)
    bot.debug("Attempting ADDITION of %s to %s." %(field,dicom_file))

    dicom = change_tag(dicom,field,value)
 
    # dicom.data_element("PatientIdentityRemoved")
    # (0012, 0062) Patient Identity Removed            CS: 'Yes'

    return dicom


def get_tag(field):
    '''get_tag will return a dictionary with tag indexed by field. For each entry,
    a dictionary lookup is included with VR,  
    :name: the keyword to get tag for, eg "PatientIdentityRemoved"
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


def change_tag(dicom,field,value):
    '''change tag is a general function that can be used by 
    update_tag or add_tag. The only difference is the print output,
    and determining to call the function based on different conditions
    '''
    dicom_file = os.path.basename(dicom.filename)
    tag = get_tag(field)

    if field in tag:
        dicom.add_new(tag[field]['tag'], tag[field]['VR'], value) 
    else:
        bot.error("%s is not a valid field to add. Skipping." %(field))

    return dicom


def update_tag(dicom,field,value):
    '''update tag will update a value in the header, if it exists
    if not, nothing is added. If the user wants to add a value
    (that might not exist) the function add_tag should be used
    '''
    if field in dicom:
        dicom = change_tag(dicom,field,value)
    return dicom


def blank_tag(dicom,field):
    '''blank tag calls update_tag with value set to an
    empty string.
    '''
    return update_tag(dicom,field,"")


def remove_tag(dicom,field):
    '''remove tag will remove a tag if it is present in the dataset
    :param dicom: the pydicom.dataset Dataset (pydicom.read_file)
    :param field: the name of the field to remove
    '''
    if field in dicom:
        tag = dicom.data_element(field).tag
        del dicom[tag]
    return dicom
