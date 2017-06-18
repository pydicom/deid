'''
utils.py: helper functions for working with dicom module

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

from deid.config.standards import (
    actions as valid_actions
)

from deid.logger import bot
from pydicom import read_file
from pydicom._dicom_dict import DicomDictionary
from pydicom.tag import Tag
from deid.utils import recursive_find
from .tags import *
from .validate import validate_dicoms
from deid.identifiers import get_timestamp
import os
import re
import sys

#########################################################################
# Functions for Dicom files
#########################################################################


def get_files(contenders,check=True,pattern=None,force=False):
    '''get_dcm_files will take a list of single dicom files or directories,
    and return a single list of complete paths to all files
    :param pattern: A pattern to use with fnmatch. If None, * is used
    :param force: force reading of the files, if some headers invalid.
    Not recommended, as many non-dicom will come through
    '''
    if not isinstance(contenders,list):
        contenders = [contenders]

    dcm_files = []
    for contender in contenders:
        if os.path.isdir(contender):
            dicom_dir = recursive_find(contender,pattern=pattern)
            bot.debug("Found %s contender files in %s" %(len(dicom_dir),
                                                         os.path.basename(contender)))
            dcm_files.extend(dicom_dir)
        else:
            bot.debug("Adding single contender file %s" %(contender))
            dcm_files.append(contender)

    if check:
        dcm_files = validate_dicoms(dcm_files,force=force)
    return dcm_files



#########################################################################
# Config.json Helpers
#########################################################################


def get_func(function_name):
    '''get_func will return a function that is defined from a string.
    the function is assumed to be in this file
    '''
    env = globals()
    if function_name in env:
        return env[function_name]
    return None



def perform_action(dicom,action,item=None):
    '''perform action takes  
    :param dicom: a loaded dicom file (pydicom read_file)
    :param item: a dictionary with keys as fields, values as values
    :param action: the action from the parsed deid to take
        "dield" (eg, PatientID) the header field to process
        "action" (eg, REPLACE) what to do with the field
        "value": if needed, the field from the response to replace with
    '''
    field = action.get('field')   # e.g: PatientID
    value = action.get('value')   # "suid" or "var:field"
    action = action.get('action') # "REPLACE"
    return _perform_action(dicom=dicom,
                           field=field,
                           item=item,
                           action=action,
                           value=value)


def _perform_action(dicom,field,action,value=None,item=None):
    '''_perform_action is the base function for performing an action.
    perform_action (above) typically is called using a loaded deid,
    and perform_addition is typically done via an addition in a config
    Both result in a call to this function. If an action fails or is not
    done, None is returned, and the calling function should handle this.
    '''
    dicom_file = os.path.basename(dicom.filename)
    done = False
    result = None

    if action not in valid_actions:
        bot.warning('%s in not a valid choice [%s]. Defaulting to blanked.' %(action,
                                                                              ".".join(valid_actions)))
        action = "BLANK"

    if field in dicom and action != "ADD":

        # Blank the value
        if action == "BLANK":
            result = blank_tag(dicom,field)
            done = True
 
        # Code the value with something in the response
        elif action == "REPLACE":
            value = parse_value(item,value)
            if value is not None:

                # If we make it here, do the replacement
                done = True
                result = update_tag(dicom,
                                    field=field,
                                    value=value)


        # Do nothing. Keep the original
        elif action == "KEEP":
            done = True
            result = dicom

        # Remove the field entirely
        elif action == "REMOVE":
            result = remove_tag(dicom,field)
            done = True

        if not done:            
            bot.warning("%s %s not done for %s" %(action,
                                                  field,
                                                  dicom_file))

    elif action == "ADD":
        value = parse_value(item,value)
        if value is not None:
            result = add_tag(dicom,field,value) 

    else:
        bot.warning('Field %s is not present in %s' %(field,dicom_file))

    return result


# Values

def parse_value(item,value):
    '''parse_value will parse the value field of an action,
    either returning the string, or a variable looked up
    in the case of var:FieldName
    '''
    # Does the user want a custom value?
    if re.search('[:]',value):
        value_type,value_option = value.split(':') 
        if value_type.lower() == "var": 
            # If selected variable not provided, skip
            if value_option not in item:
                return None
            return item[value_option]

        bot.warning('%s is not a valid value type, skipping.' %(value_type))
        return None

    return value


# Timestamps

def get_entity_timestamp(dicom,date_field=None):
    '''get_entity_timestamp will return a timestamp from the dicom
    header based on the PatientBirthDate (default) if a field is
    not provided.'''
    if date_field is None:
        date_field = "PatientBirthDate"
    item_date = dicom.get(date_field)
    return get_timestamp(item_date=item_date)


def get_item_timestamp(dicom,date_field=None,time_field=None):
    '''get_dicom_timestamp will return the UTC time for an instance.
    This is derived from the InstanceCreationDate and InstanceCreationTime
    If the Time is not set, only the date is used.
    # testing function https://gist.github.com/vsoch/23d6b313bd231cad855877dc544c98ed
    '''
    if time_field is None:
        time_field = "InstanceCreationTime"
    if date_field is None:
        date_field = "InstanceCreationDate"

    item_time = dicom.get(time_field,"")
    item_date = dicom.get(date_field)

    return get_timestamp(item_date=item_date,
                         item_time=item_time)
