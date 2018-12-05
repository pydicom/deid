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

from pydicom.sequence import Sequence
from pydicom.dataset import RawDataElement

from deid.logger import bot
from pydicom import read_file
import os


def extract_sequence(sequence,prefix=None):
    '''return a pydicom.sequence.Sequence recursively
       as a list of dictionary items
    '''
    items = []
    for item in sequence:
        for key,val in item.items():
            if not isinstance(val,RawDataElement):
                header = val.keyword
                if prefix is not None:
                    header = "%s__%s" %(prefix,header)  
                value = val.value
                if isinstance(value,bytes):
                    value = value.decode('utf-8')
                if isinstance (value,Sequence):
                    items += extract_sequence(value,prefix=header)
                    continue
                entry = {"key": header, "value": value}
                items.append(entry)
    return items



def expand_field_expression(field,dicom,contenders=None):
    '''Get a list of fields based on an expression. If 
       no expression found, return single field.
    '''
    fields = field.split(':')
    if len(fields) == 1:
        return fields
    expander,expression = fields
    fields = []
    if contenders is None:
        contenders = dicom.dir()
    if expander.lower() == "endswith":
        fields = [x for x in contenders if x.endswith(expression)]
    elif expander.lower() == "startswith":
        fields = [x for x in contenders if x.startswith(expression)]
    return fields



def get_fields(dicom, skip=None, expand_sequences=True):
    '''get fields is a simple function to extract a dictionary of fields
       (non empty) from a dicom file.
    '''    
    if skip is None:
        skip = []
    if not isinstance(skip,list):
        skip = [skip]
    fields = dict()
    contenders = dicom.dir()
    for contender in contenders:
        if contender in skip:
            continue

        try:
            value = dicom.get(contender)
            # Adding expanded sequences
            if isinstance(value,Sequence) and expand_sequences is True:
                sequence_fields = extract_sequence(value,prefix=contender)
                for sf in sequence_fields:
                    fields[sf['key']] = sf['value']
            else:
                if value not in [None,""]:
                    if isinstance(value,bytes):
                        value = value.decode('utf-8')
                    fields[contender] = str(value)
        except:
            pass # need to look into this bug
    return fields



def get_fields_byVR(dicom,exclude_fields=None):
    '''filter a dicom's fields based on a list of value
       representations (VR). If exclude_fields is not defined,
       defaults to "US" and "SS"
    '''

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
