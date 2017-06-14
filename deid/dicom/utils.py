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


import dateutil.parser
from deid.identifiers.standards import valid_actions
from deid.logger import bot
from pydicom import read_file
from pydicom._dicom_dict import DicomDictionary
from pydicom.tag import Tag
from deid.utils import recursive_find
from .validate import validate_dicoms
import os
import sys

#########################################################################
# Functions for Dicom files
#########################################################################


def get_files(contenders,check=True,pattern=None):
    '''get_dcm_files will take a list of single dicom files or directories,
    and return a single list of complete paths to all files
    :param pattern: A pattern to use with fnmatch. If None, * is used
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
        dcm_files = validate_dicoms(dcm_files)
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


def perform_addition(config,dicom):
    '''perform addition will add any additional fields to the dicom
    :param config: the config, with expected ['response']['additions']
    :param dicom: the dicom file to add a field to
    if the field is already in the dicom, it will be overwritten
    '''
    ## Actions/Additions for each come from config
    additions = config['response']['additions']

    for addition in additions:

        name = addition['name']
        value = addition['value']
        dicom = add_tag(dicom,name,value) 

    return dicom


def perform_action(dicom,response,params):
    '''perform action takes  
    :param dicom: a loaded dicom file (pydicom read_file)
    and a dictionary of params.
    :param response: the api response, with "id", "id_source" "items"
    at the top level
    :param params:
        "name" (eg, PatientID) the header field to process
        "action" (eg, coded) what to do with the field
        "value": if needed, the field from the response to replace with
    '''
    header = entity_action.get('name')   # e.g: PatientID
    action = entity_action.get('action') # "coded"
    value = entity_action.get('value')   # "suid"
    done = False

    if action not in valid_actions:
        bot.warning('%s in not a valid choice [%s]. Defaulting to blanked.' %(action,
                                                                              ".".join(valid_actions)))
        action = "blanked"

    if header in dicom:

        # Blank the value
        if action == "blanked":
            dicom = blank_tag(dicom,name=header)
            done = True
 
        # Code the value with something in the response
        elif entity_action == "coded":
            if value in response:
                dicom = update_tag(dicom,
                                   name=header,
                                   value=response[value])
                done = True

        # Remove the field entirely
        elif entity_action == "removed":
            dicom = remove_tag(dicom,name=header)
            done = True

        # Do nothing. Keep the original
        elif entity_action == "original":
            done = True

        if not done:            
            dicom = blank_tag(dicom,name=header)

    return dicom


# Timestamps

def get_item_timestamp(dicom):
    '''get_item_timestamp will return the UTC time for an instance.
    This is derived from the InstanceCreationDate and InstanceCreationTime
    If the Time is not set, only the date is used.
    # testing function https://gist.github.com/vsoch/23d6b313bd231cad855877dc544c98ed
    '''
    item_time = dicom.get("InstanceCreationTime","")
    item_date = dicom.get("InstanceCreationDate")
    timestamp = dateutil.parser.parse("%s%s" %(item_date,item_time))
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_entity_timestamp(dicom):
    '''get_entity_timestamp will return a UTC timestamp for the entity,
    derived from the patient's birthdate. In the config.json, this is
    set by setting type=func, and value=get_entity_timestamp
    '''
    item_date = dicom.get("PatientBirthDate")
    timestamp = dateutil.parser.parse("%s" %(item_date))
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

