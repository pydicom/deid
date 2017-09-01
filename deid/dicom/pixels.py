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
                'flagged':[]}

    for dicom_file in dicom_files:
        decision,group = has_burned_pixels_single(dicom_file=dicom_file,
                                                  force=force,
                                                  deid=deid)
        if decision is False:
            decision['clean'].append(dicom_file)
        else:
            if group not in decision['flagged']:
                decision['flagged'] = []
            decision['flagged'].append(dicom_file)

    return decision


def has_burned_pixels_single(dicom_file,force=True, deid=None, return_group=True):
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
    '''

    dicom = read_file(dicom_file,force=force)
    dicom_name = os.path.basename(dicom_file)
        
    # We continue processing given that:
    # ![0008,0008].contains("SAVE") *   ImageType doesn't contain save AND
    # [0018,1012].equals("") *          DateofSecondaryCapture flat not present AND
    # ![0008,103e].contains("SAVE") *   SeriesDescription does not contain save AND
    # [0018,1016].equals("") *          SecondaryDeviceCaptureManufacturer flag not present AND
    # [0018,1018].equals("") *          SecondaryDeviceCaptureManufacturerModelName flag not present AND
    # [0018,1019].equals("") *          SecondaryDeviceCaptureDeviceSoftwareVersion flag not present AND
    # ![0028,0301].contains("YES")      BurnedInAnnotation is not YES

    # We continue processing given that:
    # Image was not saved with some secondary software or device
    # Image is not flagged to have burned pixels

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
            groups = []  # keep for printing if flagged
            for filters in item['filters']:
                for criteria in filters:

                    value = ''
                    if 'values' in criteria:
                        value = criteria['values']

                    flag = apply_filter(dicom=dicom,
                                        field=criteria['field'],
                                        filter_name=criteria['action'],
                                        value=value)
                                     
                    operator = '  '
                    if 'operator' in criteria:
                        operator = criteria['operator']
                        flags.append(operator)

                    flags.append(flag)
                    groups.append('%s %s %s %s\n' %(operator,
                                                    criteria['field'],
                                                    criteria['action'],
                                                    value))

            group_name = ''
            if "name" in item:
                group_name = item['name']

            # When we parse through a group, we evaluate based on all flags
            flagged = evaluate_group(flags=flags)
            if flagged is True:
                bot.flag("%s in %%s %s" %(dicom_name,name,group_name))
                print(''.join(groups))
                return flagged, name

    bot.debug("%s header filter indicates pixels are clean." %dicom_name)
    return flagged, None


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
