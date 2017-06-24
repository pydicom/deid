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
from pydicom import read_file
import os

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


def has_burned_pixels_single(dicom_file,force=True):
    '''has burned pixels single will evaluate one dicom file.
    '''
    dicom = read_file(dicom_file,force=force)
    dicom_name = os.path.basename(dicom_file)
    has_annotation = False
        
    # has_annotation False given:

    # Image was not saved with some other software

    # ![0008,0008].contains("SAVE") * 
    if "SAVE" in dicom.get('ImageType',[]):
        has_annotation=True

    # There are no flags to indicate secondary capture

    # [0018,1012].equals("") *
    if dicom.get('DateOfSecondaryCapture') is not None:
        has_annotation=True

    # ![0008,103e].contains("SAVE") * 
    if "SAVE" in dicom.get('SeriesDescription',[]):
        has_annotation=True

    # [0018,1016].equals("") *
    if dicom.get('SecondaryCaptureDeviceManufacturer') is not None:
        has_annotation = True

    # [0018,1018].equals("") *
    if dicom.get('SecondaryCaptureDeviceManufacturerModelName') is not None:
        has_annotation = True

    # [0018,1019].equals("") *
    if dicom.get('SecondaryCaptureDeviceSoftwareVersions') is not None:
        has_annotation = True

    # The image is not flagged to have a Burned Annotation

    # ![0028,0301].contains("YES")
    if dicom.get('BurnedInAnnotation','no').upper() == "YES":
        has_annotation = True

    if has_annotation:
        bot.warning("%s header filters indicate burned pixels." %dicom_name)
    else:
        bot.debug("%s header filter indicates pixels are clean." %dicom_name)

    return has_annotation
        
