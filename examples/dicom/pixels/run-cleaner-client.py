#!/usr/bin/env python3

from deid.dicom import DicomCleaner

# This is a complete example of using the cleaning client to inspect
# and clean pixels
# based on a deid.dicom specification
# https://pydicom.github.io/deid

#########################################
# 1. Get List of Files
#########################################

# This will get a set of example cookie dicoms
from deid.dicom import get_files
from deid.data import get_dataset

base = get_dataset("dicom-cookies")
dicom_files = list(get_files(base))  # todo : consider using generator functionality
dicom_file = dicom_files[3]


#########################################
# 2. Create Client
#########################################

client = DicomCleaner()

# You can set the output folder if you want, otherwise tmpdir is used
client = DicomCleaner(output_folder="/home/vanessa/Desktop")

# Steps are to detect, clean, and save in desired format, one image
# at a time.
# client.detect(dicom_file)
# client.clean()
# client.save_<format>


#########################################
# 3. Detect
#########################################

# Detect means using the deid recipe to parse headers

# If we try to clean before we detect, we can't
# client.clean()
# WARNING Use <deid.dicom.pixels.clean.DicomCleaner object at 0x7fafb70b9cf8>.detect() to find coordinates first.

client.detect(dicom_file)

# {'flagged': True,
# 'results': [{'coordinates': [],
#   'group': 'blacklist',
#   'reason': ' ImageType missing  or ImageType empty '}]}


#########################################
# 4. Clean and save
#########################################

client.clean()

# If there are coordinates, they are blanked. Otherwise, no change.
# Blanking 0 coordinate results

# Default output folder is temporary, unless specified at client onset
# or directly to saving functions
client.save_png()
client.save_dicom()
