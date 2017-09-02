'''
pixels.py: functions for pixel scrubbing

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
from deid.dicom.tags import get_tag
from deid.dicom.utils import perform_action
from deid.utils import read_json
from pydicom import read_file
from deid.dicom.filter import (
    Dataset,     # add additional filters
    apply_filter
)
from deid.data import get_deid
from deid.config import load_deid

import os


def clean_pixels():
    bot.warning('BEEP-BOOP - I am not written yet!')


def has_burned_pixels(dicom_files,force=True,deid=None):
    ''' has burned pixels will use the MIRCTP criteria (see ref folder with the
    original scripts used by CTP) to determine if an image is likely to have 
    PHI, based on fields in the header alone. This script does NOT perform
    pixel cleaning, but returns a dictionary of results, where the key is
    the file, and the value is True/False to indicate if there are burned 
    pixels in the image (with possible identifiers)
    '''

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    # Store decisions in lookup based on filter groups
    decision = {'clean':[],
                'flagged':{},
                'reason':{}}

    for dicom_file in dicom_files:
        flagged,group,reason = has_burned_pixels_single(dicom_file=dicom_file,
                                                        force=force,
                                                        deid=deid)
        if flagged is False:
            # In this case, group is None
            decision['clean'].append(dicom_file)
        else:
            if group not in decision['flagged']:
                decision['flagged'][group] = []
            decision['flagged'][group].append(dicom_file)
            decision['reason'][dicom_file] = reason

    return decision


def has_burned_pixels_single(dicom_file,force=True, deid=None, return_group=True, return_reason=True):
    '''has burned pixels single will evaluate one dicom file for burned in
    pixels based on 'filter' criteria in a deid. If deid is not provided,
    will use application default. The method proceeds as follows:

    1. deid is loaded, with criteria groups ordered from specific --> general
    2. image is run down the criteria, stops when hits and reports FLAG
    3. passing through the entire list gives status of pass
    
    The default deid has a greylist, whitelist, then blacklist

    Parameters
    =========
    dicom_file: the fullpath to the file to evaluate
    force: force reading of a potentially erroneous file
    deid: the full path to a deid specification. if not defined, default used
    return_group: also return the group of the flagged files
    return_reason: return a string reason for why the flag was done (none if clean)

    config['filter']['dangerouscookie'] <-- filter list "dangerouscookie"

     has one or more filter criteria associated with coordinates

     [{'coordinates': ['0,0,512,110'],
       'filters': [{'InnerOperators': [],
       'action': ['notequals'],
       'field': ['OperatorsName'],
       'operator': 'and',
       'value': ['bold bread']}],
     'name': 'criteria for dangerous cookie'}]
    '''

    dicom = read_file(dicom_file,force=force)
    dicom_name = os.path.basename(dicom_file)
        

    if deid is None:
        deid = get_deid('dicom')

    if not os.path.exists(deid):
        bot.error("Cannot find config %s, exiting" %(config))

    config = load_deid(deid)

    # Load criteria (actions) for flagging
    if 'filter' not in config:
        bot.error('Deid provided does not have %filter, exiting.')
        sys.exit(1)

    for name,items in config['filter'].items():
        for item in items:
            flags = []

            descriptions = [] # description for each group across items

            for group in item['filters']:
                group_flags = []         # evaluation for a single line
                group_descriptions = []
                for action in group['action']:
                    field = group['field'].pop(0)
                    value = ''
                    if len(group['value']) > 0:
                        value = group['value'].pop(0)
                    flag = apply_filter(dicom=dicom,
                                        field=field,
                                        filter_name=action,
                                        value=value or None)
                    group_flags.append(flag)
                    description = "%s %s %s" %(field,action,value)
                    if len(group['InnerOperators']) > 0:
                        inner_operator = group['InnerOperators'].pop()
                        group_flags.append(inner_operator)
                        description = "%s %s" %(description,inner_operator)
                    group_descriptions.append(description)
                # At the end of a group, evaluate the inner group   
                flag = evaluate_group(group_flags)
                flags.append(flag)
                # "Operator" is relevant for the outcome of the list of actions 
                operator = ''
                if 'operator' in group:
                    if group['operator'] is not None:
                        operator = group['operator']
                reason = ('%s %s' %(operator,' '.join(group_descriptions))).replace('\n',' ')
                descriptions.append(reason)
            group_name = ''
            if "name" in item:
                group_name = item['name']

            # When we parse through a group, we evaluate based on all flags
            flagged = evaluate_group(flags=flags)

            if flagged is True:
                bot.flag("%s in section %s\n" %(dicom_name,name))
                print('LABEL: %s' %group_name)
                print('CRITERIA: %s' %' '.join(descriptions))
                if return_reason is True:
                    return flagged, name, reason
                return flagged, name

    bot.debug("%s header filter indicates pixels are clean." %dicom_name)
    return flagged, None, None


def evaluate_group(flags):
    '''evaluate group will take a list of flags (eg:

        [True, and, False, or, True]

    And read through the logic to determine if the image result
    is to be flagged.
    '''
    flagged = False
    first_entry = True

    while len(flags) > 0:
        flag = flags.pop(0)
        if flag == "and":
            flag = flags.pop(0)
            flagged = flag and flagged
        elif flag == "or":
            flag = flags.pop(0)
            flagged = flag or flagged
        else:
            # If it's the first entry
            if first_entry is True:
                flagged = flag
            else:
                flagged = flagged and flag
        first_entry = False

    return flagged
