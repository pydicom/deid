#!/usr/bin/env python3

# This is a complete example of inspecting pixels for PHI 
# based on a deid.dicom specification
# https://pydicom.github.io/deid



# This will get a set of example cookie dicoms
from deid.dicom import (
    get_files,
    has_burned_pixels
)
from pydicom import read_file
from deid.data import get_dataset
from deid.logger import bot
import os
bot.level = 3

base = get_dataset('dicom-cookies')
dicom_files = get_files(base)

groups = has_burned_pixels(dicom_files=dicom_files, deid='examples/deid')

# Found 7 valid dicom files
# FLAGGED image6.dcm in section dangerouscookie
# LABEL: LABEL Criteria for Dangerous Cookie
# CRITERIA:  PatientSex contains M and OperatorsName notequals bold bread
# FLAGGED image5.dcm in section dangerouscookie
# LABEL: LABEL Criteria for Dangerous Cookie
# CRITERIA:  PatientSex contains M and OperatorsName notequals bold bread

# We see above two are flagged for OperatorsName not bold bread, and being male
# Is this accurate?
for dicom_file in dicom_files:
    dicom = read_file(dicom_file)
    print("%s:%s - %s" %(os.path.basename(dicom_file),
                         dicom.OperatorsName,
                         dicom.PatientSex))

# image4.dcm:bold bread - M
# image2.dcm:lingering hill - F
# image7.dcm:sweet brook - F
# image6.dcm:green paper - M       <--- FLAGGED
# image3.dcm:nameless voice - F
# image1.dcm:fragrant pond - F
# image5.dcm:curly darkness - M    <--- FLAGGED
