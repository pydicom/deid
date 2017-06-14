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


#########################################################################
# Functions for Single Dicom files
#########################################################################

def add_tag(dicom,name,value):
    '''add tag will add a tag only if it's in the (active) DicomDictionary
    :param dicom: the pydicom.dataset Dataset (pydicom.read_file)
    :param name: the name of the field to add
    :param value: the value to set, if name is a valid tag
    '''
    dicom_file = os.path.basename(dicom.filename)
    tag = get_tag(name)

    if name in tag:
        dicom.add_new(tag['tag'], tag['VR'], value) 
 
        # dicom.data_element("PatientIdentityRemoved")
        # (0012, 0062) Patient Identity Removed            CS: 'Yes'

        bot.debug("ADDITION %s to %s." %(dicom.data_element(name),dicom_file))
    else:
        bot.error("%s is not a valid field to add. Skipping." %(name))

    return dicom


def get_tag(name):
    '''get_tag will return a dictionary with tag indexed by name. For each entry,
    a dictionary lookup is included with VR,  
    :name: the keyword to get tag for, eg "PatientIdentityRemoved"
    '''
    found = [{key:value} for key,value in DicomDictionary.items() if value[4] == name]
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

        tags[name] = manifest 
    return tags


def update_tag(dicom,name,value):
    '''update tag will update a value in the header, if it exists
    if not, nothing is added. If the user wants to add a value
    (that might not exist) the function add_tag should be used
    '''
    if name in dicom:
        tag = dicom.data_element(name).tag
        dicom[tag] = value
    return dicom


def blank_tag(dicom,name):
    '''blank tag calls update_tag with value set to an
    empty string.
    '''
    return update_tag(dicom,name,"")


def remove_tag(dicom,name):
    '''remove tag will remove a tag if it is present in the dataset
    :param dicom: the pydicom.dataset Dataset (pydicom.read_file)
    :param name: the name of the field to remove
    '''
    if name in dicom:
        tag = dicom.data_element(name).tag
        del dicom[tag]
    return dicom
