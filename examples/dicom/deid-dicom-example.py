#!/usr/bin/env python3

# This is a complete example of doing de-identifiction. For details, see our docs
# https://pydicom.github.io/deid


# This will get a set of example cookie dicoms
from deid.dicom import get_files
from deid.data import get_dataset
from deid.dicom import replace_identifiers
base = get_dataset('dicom-cookies')
dicom_files = get_files(base)


# This is the function to get identifiers
from deid.dicom import get_identifiers
ids = get_identifiers(dicom_files)

#**
# Here you might save them in your special (IRB approvied) places
# And then provide replacement anonymous ids to put back in the data
# A cookie tumor example is below
#**

# Load your custom deid parameters (see deid folder under examples)
from deid.utils import get_installdir
from deid.config import load_deid
import os

path = os.path.abspath("%s/../examples/deid/" %get_installdir())

# If you are intereseted to see it, but you don't have to do this,
# this happens internally
deid = load_deid(path)


# Let's add the fields that we specify to add in our deid, a source_id for SOPInstanceUID,
# and an id for PatientID
count=0
updated_ids = dict()
for image,fields in ids.items():    
    fields['id'] = 'cookiemonster'
    fields['source_id'] = "cookiemonster-image-%s" %(count)
    updated_ids[image] = fields
    count+=1

# Run again, provided the path to deid, and the updated ids
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=path,
                                    ids=updated_ids)


# We can load in a cleaned file to see what was done
from pydicom import read_file
test_file = read_file(cleaned_files[0])


# test_file
# (0008, 0018) SOP Instance UID                    UI: cookiemonster-image-1
# (0010, 0020) Patient ID                          LO: 'cookiemonster'
# (0012, 0062) Patient Identity Removed            CS: 'Yes'
# (0028, 0002) Samples per Pixel                   US: 3
# (0028, 0010) Rows                                US: 1536
# (0028, 0011) Columns                             US: 2048
# (7fe0, 0010) Pixel Data                          OB: Array of 738444 bytes


# Different output folder
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    ids=updated_ids,
                                    output_folder='/home/vanessa/Desktop')

# Force overwrite (be careful!)
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    ids=updated_ids,
                                    output_folder='/home/vanessa/Desktop',
                                    overwrite=True)
