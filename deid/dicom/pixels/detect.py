'''

detect.py: functions for pixel scrubbing

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

from deid.config import DeidRecipe
from deid.logger import bot
from pydicom import read_file
from deid.dicom.filter import apply_filter

import os
import sys

def has_burned_pixels(dicom_files, force=True, deid=None):
    ''' has burned pixels is an entrypoint for has_burned_pixels_multi (for 
    multiple images) or has_burned_pixels_single (for one detailed repor)
    We will use the MIRCTP criteria (see ref folder with the
    original scripts used by CTP) to determine if an image is likely to have 
    PHI, based on fields in the header alone. This script does NOT perform
    pixel cleaning, but returns a dictionary of results (for multi) or one
    detailed result (for single)
    '''
    # if the user has provided a custom deid, load it
    if not isinstance(deid, DeidRecipe):
        if deid is None:
            deid = 'dicom'
        deid = DeidRecipe(deid)

    if isinstance(dicom_files,list):
        return _has_burned_pixels_multi(dicom_files, force, deid)
    return _has_burned_pixels_single(dicom_files, force, deid)



def _has_burned_pixels_multi(dicom_files, force, deid):
    '''return a summary dictionary with lists of clean, and then lookups
       for flagged images with reasons. The deid should be a deid recipe
       instantiated from deid.config.DeidRecipe. This function should not
       be called directly, but should be called from has_burned_pixels
    '''

    # Store decisions in lookup based on filter groups
    decision = {'clean':[],
                'flagged':{}}

    for dicom_file in dicom_files:
        result = _has_burned_pixels_single(dicom_file=dicom_file,
                                           force=force,
                                           deid=deid)


        if result['flagged'] is False:
            # In this case, group is None
            decision['clean'].append(dicom_file)
        else:
            decision['flagged'][dicom_file] = result

    return decision


def _has_burned_pixels_single(dicom_file, force, deid):

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
    deid: the full path to a deid specification. if not defined, only default used

    deid['filter']['dangerouscookie'] <-- filter list "dangerouscookie"

    --> This is what an item in the criteria looks like
        [{'coordinates': ['0,0,512,110'],
          'filters': [{'InnerOperators': [],
          'action': ['notequals'],
          'field': ['OperatorsName'],
          'operator': 'and',
          'value': ['bold bread']}],
        'name': 'criteria for dangerous cookie'}]

    
    Returns
    =======
    --> This is what a clean image looks like:
        {'flagged': False, 'results': []}


    --> This is what a flagged image looks like:
       {'flagged': True,
        'results': [
                      {'reason': ' ImageType missing  or ImageType empty ',
                       'group': 'blacklist',
                       'coordinates': []}
                   ]
        }
    '''

    dicom = read_file(dicom_file,force=force)
    dicom_name = os.path.basename(dicom_file)
        
    # Load criteria (actions) for flagging
    filters = deid.get_filters()
    if not filters:
        bot.error('Deid provided does not have %filter, exiting.')
        sys.exit(1)

    # Return list with lookup as dicom_file
    results = []
    global_flagged = False

    for name,items in filters.items():
        for item in items:
            flags = []

            descriptions = [] # description for each group across items

            for group in item['filters']:
                group_flags = []         # evaluation for a single line
                group_descriptions = []

                # You cannot pop from the list
                for a in range(len(group['action'])):
                    action = group['action'][a]
                    field = group['field'][a]
                    value = ''
                    if len(group['value']) > a:
                        value = group['value'][a]
                    flag = apply_filter(dicom=dicom,
                                        field=field,
                                        filter_name=action,
                                        value=value or None)
                    group_flags.append(flag)
                    description = "%s %s %s" %(field,action,value)
                    if len(group['InnerOperators']) > a:
                        inner_operator = group['InnerOperators'][a]
                        group_flags.append(inner_operator)
                        description = "%s %s" %(description,inner_operator)
                    group_descriptions.append(description)

                # At the end of a group, evaluate the inner group   
                flag = evaluate_group(group_flags)

                # "Operator" is relevant for the outcome of the list of actions 
                operator = ''
                if 'operator' in group:
                    if group['operator'] is not None:
                        operator = group['operator']
                        flags.append(operator)

                flags.append(flag)
                reason = ('%s %s' %(operator,' '.join(group_descriptions))).replace('\n',' ')
                descriptions.append(reason)

            group_name = ''
            if "name" in item:
                group_name = item['name']

            # When we parse through a group, we evaluate based on all flags
            flagged = evaluate_group(flags=flags)

            if flagged is True:
                global_flagged = True
                reason = ' '.join(descriptions)

                result = {'reason': reason,
                          'group': name,
                          'coordinates': item['coordinates'] }

                results.append(result)

    results = {'flagged': global_flagged,
               'results': results }
    return results


def evaluate_group(flags):
    '''evaluate group will take a list of flags (eg:

        [True, and, False, or, True]

    And read through the logic to determine if the image result
    is to be flagged. This is how we combine a set of criteria in
    a group to come to a final decision.
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
