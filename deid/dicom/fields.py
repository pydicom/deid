'''
header.py: functions to extract identifiers from dicom headers

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
import os


def expand_field_expression(field,dicom):
    '''Get a list of fields based on an expression. If 
    no expression found, return single field.
    '''
    fields = field.split(':')
    if fields == 1:
        return fields
    expander,expression = fields
    fields = []
    if expander.lower() == "endswith":
        fields = [x for x in dicom.dir() if x.endswith(expression)]
    elif expander.lower() == "startswith":
        fields = [x for x in dicom.dir() if x.startswith(expression)]
    return fields



def get_fields(dicom,skip=None):
    '''get fields is a simple function to extract a dictionary of fields
    (non empty) from a dicom file.
    '''    
    if skip is None:
        skip = []

    fields = dict()
    contenders = dicom.dir()
    dicom_file = os.path.basename(dicom.filename)
    for contender in contenders:
        if contender in skip:
            continue
        value = dicom.get(contender)
        if value not in [None,""]:
            fields[contender] = value
    bot.debug("Found %s defined fields for %s" %(len(fields),
                                                 dicom_file))
    return fields



def get_fields_byVR(dicom,exclude_fields=None):
    '''filter a dicom's fields based on a list of value
    representations (VR). If exclude_fields is not defined,
    defaults to "US" and "SS"'''

    if exclude_fields is None:
        exclude_fields = ['US','SS']

    if not isinstance(exclude_fields,list):
        exclude_fields = [exclude_fields]

    fields = []
    for field in dicom.dir():
        if dicom.data_element(field) is not None:
            if "VR" in dicom.data_element(field).__dict__:
                if dicom.data_element(field) not in exclude_fields:
                    fields.append(field)
    return fields
