#!/usr/bin/env python3

from deid.dicom import get_files, replace_identifiers
from deid.data import get_dataset

# This is an example of replacing fields in dicom headers,
# but via a function instead of a preset identifier.

# This will get a set of example cookie dicoms
base = get_dataset("dicom-cookies")
dicom_files = list(get_files(base))  # todo : consider using generator functionality


# This is the function to get identifiers
from deid.dicom import get_identifiers

items = get_identifiers(dicom_files)

# **
# The function performs an action to generate a uid, but you can also use
# it to communicate with databases, APIs, or do something like
# save the original (and newly generated one) in some (IRB approvied) place
# **

################################################################################
# The Deid Recipe
#
# The process of updating header values means writing a series of actions
# in the deid recipe, in this folder the file "deid.dicom" that has the
# following content:
#
# FORMAT dicom

# %header

# REPLACE StudyInstanceUID func:generate_uid
# REPLACE SeriesInstanceUID func:generate_uid
# ADD FrameOfReferenceUID func:generate_uid
#
# In the above we are saying we want to replace the fields above with the
# output from the generate_uid function, which is expected in the item dict
##################################

# Create the DeidRecipe Instance from deid.dicom
from deid.config import DeidRecipe

recipe = DeidRecipe("deid.dicom")

# To see an entire (raw in a dictionary) recipe just look at
recipe.deid

# What is the format?
recipe.get_format()
# dicom

# What actions do we want to do on the header?
recipe.get_actions()

"""
[{'action': 'REPLACE',
  'field': 'StudyInstanceUID',
  'value': 'func:generate_uid'},
 {'action': 'REPLACE',
  'field': 'SeriesInstanceUID',
  'value': 'func:generate_uid'},
 {'action': 'REPLACE',
  'field': 'FrameOfReferenceUID',
  'value': 'func:generate_uid'}]
"""

# We can filter to an action type (not useful here, we only have one type)
recipe.get_actions(action="REPLACE")

# or we can filter to a field
recipe.get_actions(field="FrameOfReferenceUID")

"""
[{'action': 'REPLACE',
  'field': 'FrameOfReferenceUID',
  'value': 'func:generate_uid'}]
"""

# and logically, both (not useful here)
recipe.get_actions(field="PatientID", action="REMOVE")


# Here we need to update each item with the function we want to use!


def generate_uid(item, value, field, dicom):
    """This function will generate a dicom uid! You can expect it to be passed
       the dictionary of items extracted from the dicom (and your function)
       and variables, the original value (func:generate_uid) and the field
       object you are applying it to.
    """
    import uuid

    # a field can either be just the name string, or a DicomElement
    if hasattr(field, "name"):
        field = field.name

    # Your organization should have it's own DICOM ORG ROOT.
    # For the purpose of an example, borrowing PYMEDPHYS_ROOT_UID.
    #
    # When using a UUID to dynamically create a UID (e.g. SOPInstanceUID),
    # the root '2.25' can be used instead of an organization's root.
    # For more information see DICOM PS3.5 2020b B.2
    ORG_ROOT = "1.2.826.0.1.3680043.10.188"  # e.g. PYMEDPHYS_ROOT_UID
    prefix = field.lower().replace(" ", " ")
    bigint_uid = str(uuid.uuid4().int)
    full_uid = ORG_ROOT + "." + bigint_uid
    sliced_uid = full_uid[0:64]  # A DICOM UID is limited to 64 characters
    return prefix + "-" + sliced_uid


# Remember, the action is:
# REPLACE StudyInstanceUID func:generate_uid
# so the key needs to be generate_uid

for item in items:
    items[item]["generate_uid"] = generate_uid

# Now let's generate the cleaned files! It will output to a temporary directory
# And then use the deid recipe and updated to create new files
cleaned_files = replace_identifiers(dicom_files=dicom_files, deid=recipe, ids=items)


# Print a cleaned file
print(cleaned_files[0])
