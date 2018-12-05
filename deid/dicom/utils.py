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

from deid.config.standards import (
    actions as valid_actions
)

from .fields import expand_field_expression

from deid.logger import bot
from pydicom import read_file
from pydicom._dicom_dict import DicomDictionary
from pydicom.tag import Tag
from deid.utils import recursive_find
from .tags import *
from .validate import validate_dicoms
from deid.identifiers import get_timestamp
import tempfile
import os
import re
import sys

################################################################################
# Functions for Dicom files
################################################################################

def get_files(contenders, check=True, pattern=None, force=False):
    '''get_files will take a list of single dicom files or directories,
       and return a generator that yields complete paths to all files
    
       Parameters
       ==========
       conteners: a list of files or directories (contenders!)
       check: boolean to indicate if we should validate dicoms (default True)
       pattern: A pattern to use with fnmatch. If None, * is used
       force: force reading of the files, if some headers invalid.
              Not recommended, as many non-dicom will come through

    '''
    if not isinstance(contenders,list):
        contenders = [contenders]

    for contender in contenders:
        if os.path.isdir(contender):
            dicom_files = recursive_find(contender, pattern=pattern)
        else:
            dicom_files = [contender]

        for dicom_file in dicom_files:
            if dicom_file is not None:
                if check:
                    validated_files = validate_dicoms(dicom_file, force=force)
                else:
                    validated_files = [dicom_file]

                for validated_file in validated_files:
                    bot.debug("Found contender file %s" %(validated_file))
                    yield validated_file


def save_dicom(dicom, dicom_file, output_folder=None, overwrite=False):
    '''save_dicom will save a dicom file to an output folder,
       making sure to not overwrite unless the user has enforced it

       Parameters
       ==========
       dicom: the pydicon Dataset to save
       dicom_file: the path to the dicom file to save (we only use basename)
       output_folder: the folder to save the file to
       overwrite: overwrite any existing file? (default is False)

    '''

    if output_folder is None:
        if overwrite is False:
            output_folder = tempfile.mkdtemp()
        else:
            output_folder = os.path.dirname(dicom_file)

    dicom_name = os.path.basename(dicom_file)
    output_dicom = os.path.join(output_folder,dicom_name)
    dowrite = True
    if overwrite is False:
        if os.path.exists(output_dicom):
            bot.error("%s already exists, overwrite set to False. Not writing." %dicom_name)
            dowrite = False

    if dowrite:
        dicom.save_as(output_dicom)
    return output_dicom


################################################################################
# Config.json Helpers
################################################################################


def get_func(function_name):
    '''get_func will return a function that is defined from a string.
       the function is assumed to be in this file

       Parameters
       ==========
       return a function from globals based on a name string

    '''
    env = globals()
    if function_name in env:
        return env[function_name]
    return None



def perform_action(dicom, action, item=None, fields=None):
    '''perform an action on a dataset.

       Parameters
       ==========
       dicom: a loaded dicom file (pydicom read_file)
       item: a dictionary with keys as fields, values as values
       fields: if provided, a filtered list of fields for expand
       action: the action from the parsed deid to take
           "died" (eg, PatientID) the header field to process
           "action" (eg, REPLACE) what to do with the field
           "value": if needed, the field from the response to replace with

    '''
    field = action.get('field')   # e.g: PatientID, endswith:ID
    value = action.get('value')   # "suid" or "var:field"
    action = action.get('action') # "REPLACE"

    # If there is an expander applied to field, we iterate over
    fields = expand_field_expression(field=field,
                                     dicom=dicom,
                                     contenders=fields)
    
    changed = False
    for field in fields:
        result = _perform_action(dicom=dicom,
                                 field=field,
                                 item=item,
                                 action=action,
                                 value=value)
        if result is not None:
            changed = True
            dicom = result
    if changed is True:
        return dicom
    return None


def _perform_action(dicom, field, action, value=None, item=None):
    '''_perform_action is the base function for performing an action.
        perform_action (above) typically is called using a loaded deid,
        and perform_addition is typically done via an addition in a config
        Both result in a call to this function. If an action fails or is not
        done, None is returned, and the calling function should handle this.
    '''

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

        # Code the value with something in the response
        elif action == "JITTER":
            value = parse_value(item,value)
            if value is not None:

                # Jitter the field by the supplied value
                done = True
                result = jitter_timestamp(dicom,
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
            bot.warning("%s %s not done" %(action, field))

    elif action == "ADD":
        value = parse_value(item,value)
        if value is not None:
            result = add_tag(dicom,field,value) 


    return result


# Values

def parse_value(item, value):
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
def jitter_timestamp(dicom, field, value):
    '''if present, jitter a timestamp in dicom
       field "field" by number of days specified by "value"
       The value can be positive or negative.
 
       Parameters
       ==========
       dicom: the pydicom Dataset
       field: the field with the timestamp
       value: number of days to jitter by. Jitter bug!

    '''
    if not isinstance(value, int):
        value = int(value)

    original = dicom.get(field,None)
    if original is not None:
        dicom[field] = original + value
    return dicom
   

def get_entity_timestamp(dicom, date_field=None):
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
       
       ::notes 
           testing function:
           https://gist.github.com/vsoch/23d6b313bd231cad855877dc544c98ed
    '''
    if time_field is None:
        time_field = "InstanceCreationTime"
    if date_field is None:
        date_field = "InstanceCreationDate"

    item_time = dicom.get(time_field,"")
    item_date = dicom.get(date_field)

    return get_timestamp(item_date=item_date,
                         item_time=item_time)
