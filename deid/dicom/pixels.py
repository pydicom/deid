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
from .tags import get_tag
from .utils import perform_action
from deid.utils import read_json
from pydicom import read_file
from .filter import (
    Dataset,     # add additional filters
    apply_filter
)
import os

here = os.path.dirname(os.path.abspath(__file__))

def clean_pixels():
    bot.warning('BEEP-BOOP - I am not written yet!')


def has_burned_pixels(dicom_files,force=True):
    ''' has burned pixels will use the MIRCTP criteria (see ref folder with the
    original scripts used by CTP) to determine if an image is likely to have 
    PHI, based on fields in the header alone. This script does NOT perform
    pixel cleaning, but returns a dictionary of results, where the key is
    the file, and the value is True/False to indicate if there are burned 
    pixels in the image (with possible identifiers)
    '''

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    decision = dict()

    for dicom_file in dicom_files:
        decision[dicom_file] = has_burned_pixels_single(dicom_file,force)

    return decision


def has_burned_pixels_single(dicom_file,force=True, config=None):
    '''has burned pixels single will evaluate one dicom file.
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

    if config is None:
        config = "%s/pixels.json" %(here)

    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))

    config = read_json(config)

    # Load criteria (actions) for flagging
    for criteria in config:

        flagged = False
        filters = criteria["filters"]
        label = [x for x in [criteria['modality'],
                             criteria['manufacturer'],
                             criteria['label']]
                 if x is not None]

        for func,actions in filters.items():
            for action in actions:
                flagged = apply_filter(dicom=dicom,
                                       field=action['field'],
                                       filter_name=func,
                                       value=action["value"])
                                     
                if flagged:
                    label = " ".join(label)
                    bot.warning("FLAG for %s: %s" %(dicom_name,label))
                    return flagged


    bot.debug("%s header filter indicates pixels are clean." %dicom_name)
    return flagged
