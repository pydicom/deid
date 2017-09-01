#!/usr/bin/env python3

# This is a complete example of inspecting pixels for PHI 
# based on a deid.dicom specification
# https://pydicom.github.io/deid



# This will get a set of example cookie dicoms
from deid.dicom import (
    get_files,
    has_burned_pixels
)
from deid.data import get_dataset
from deid.logger import bot
bot.level = 3

base = get_dataset('dicom-cookies')
dicom_files = get_files(base)

groups = has_burned_pixels(dicom_files=dicom_files, deid='examples/deid')

# FLAGGED image2.dcm in section dangerouscookie
# LABEL: criteria for dangerous cookie
# CRITERIA: and OperatorsName notequals bold bread

# FLAGGED image7.dcm in section dangerouscookie
# LABEL: criteria for dangerous cookie
# CRITERIA: and OperatorsName notequals bold bread

# FLAGGED image6.dcm in section dangerouscookie
# LABEL: criteria for dangerous cookie
# CRITERIA: and OperatorsName notequals bold bread

# FLAGGED image3.dcm in section dangerouscookie
# LABEL: criteria for dangerous cookie
# CRITERIA: and OperatorsName notequals bold bread

# FLAGGED image1.dcm in section dangerouscookie
# LABEL: criteria for dangerous cookie
# CRITERIA: and OperatorsName notequals bold bread

# FLAGGED image5.dcm in section dangerouscookie
# LABEL: criteria for dangerous cookie
# CRITERIA: and OperatorsName notequals bold bread

# We see above six are flagged because the operator's name isn't bold bread. 
# Is this accurate?
for dicom_file in dicom_files:
    dicom = read_file(dicom_file)
    print("%s:%s" %(os.path.basename(dicom_file),dicom.OperatorsName))

#image4.dcm:bold bread
#image2.dcm:lingering hill
#image7.dcm:sweet brook
#image6.dcm:green paper
#image3.dcm:nameless voice
#image1.dcm:fragrant pond
#image5.dcm:curly darkness
