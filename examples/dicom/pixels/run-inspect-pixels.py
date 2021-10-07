#!/usr/bin/env python3

# This is a complete example of inspecting pixels for PHI
# based on a deid.dicom specification
# https://pydicom.github.io/deid


# This will get a set of example cookie dicoms
from deid.dicom import get_files, has_burned_pixels
from deid.data import get_dataset
from deid.logger import bot

bot.level = 3

base = get_dataset("dicom-cookies")
dicom_files = list(get_files(base))  # todo : consider using generator functionality

results = has_burned_pixels(dicom_files=dicom_files, deid="examples/deid")

# The dictionary has a "clean" list, and a "flagged" list,
# Eg:

# {'clean': [],
#  'flagged': {'/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image1.dcm': {'flagged': True,
#  'results': [{'coordinates': [],
#               'group': 'blacklist',
#               'reason': ' ImageType missing  or ImageType empty '}]},
