#!/usr/bin/env python3

import os

# We can load in a cleaned file to see what was done
from pydicom import read_file

# Create a DeidRecipe
from deid.config import DeidRecipe
from deid.data import get_dataset
from deid.dicom import get_files, get_identifiers, replace_identifiers
from deid.utils import get_installdir

# This is a complete example of doing de-identification. For details, see our docs
# https://pydicom.github.io/deid


# This will get a set of example cookie dicoms
base = get_dataset("dicom-cookies")
dicom_files = list(get_files(base))  # todo : consider using generator functionality


ids = get_identifiers(dicom_files)

# **
# Here you might save them in your special (IRB approvied) places
# And then provide replacement anonymous ids to put back in the data
# A cookie tumor example is below
# **

################################################################################
# The Deid Recipe
#
# The process of flagging images comes down to writing a set of filters to
# check if each image meets some criteria of interest. For example, I might
# create a filter called "xray" that is triggered when the Modality is CT or XR.
# We specify these filters in a simple text file called a "deid recipe." When
# you work with the functions, you have the choice to instantiate the object
# in advance, or just provide a path to a recipe file. We will walk through
# examples  for both below, starting with working with a DeidRecipe object.
# If you aren't interested in this use case or just want to use a provided
# deid recipe file, continue to the step to replace_identifiers
#
##################################

recipe = DeidRecipe()

# Since we didn't load a custom deid recipe text file, we get a default
# WARNING No specification, loading default base deid.dicom
# You can add custom deid files with .load().

# We can look at the criteria loaded:
recipe.deid

# You can also provide your own deid recipe file, and in doing so, you
# won't load a default
path = os.path.abspath("%s/../examples/deid/" % get_installdir())
recipe = DeidRecipe(deid=path)

# You can also choose to load the default base with your own recipe
recipe = DeidRecipe(deid=path, base=True)

# Or specify a different base entirely. The base is the deid.<tag> in the
# deid.data folder. So for example, under deid/data/deid.dicom.chest.xray we would
# do:
recipe = DeidRecipe(deid=path, base=True, default_base="dicom.xray.chest")

# We can also specify one of the deid recipes provided by the library as our
# only to use.
recipe = DeidRecipe(deid="dicom.xray.chest")

# This is to encourage sharing! If you have a general recipe that others might
# use, please contribute it to the library.

# You can also load multiple deid files, just put them in a list in the order
# that you want them loaded.

# To see an entire (raw in a dictionary) recipe just look at
recipe.deid

# Now let's look at parts of this recipe. There are two categories of things:
# - filters: are used for parsing over headers and flagging images
# - header: is a set of rules that govern a replacement procedure

################################################################################
# Format
################################################################################

recipe.get_format()
# dicom


################################################################################
# Filters
################################################################################

# To get a complete dict of all filters, key (index) is by filter group
recipe.get_filters()

# To get the group names
recipe.ls_filters()
# ['whitelist', 'blacklist']

# To get a list of specific filters under a group
recipe.get_filters("blacklist")


################################################################################
# Header Actions
# A header action is a step (e.g., replace, remove, blank) to be applied to
# a dicom image header. The headers are also part of the deid recipe, and you
# don't need to necessarily use header actions and filters at the same time.
################################################################################

# For the example we were doing above, the recipe didn't have a header section.
# Let's load one that does.
recipe = DeidRecipe()

# We can get a complete list of actions
recipe.get_actions()

# We can filter to an action type
recipe.get_actions(action="ADD")

# [{'action': 'ADD',
#  'field': 'IssuerOfPatientID',
#  'value': 'STARR. In an effort to remove PHI all dates are offset from their original values.'},
# {'action': 'ADD',
#  'field': 'PatientBirthDate',
#  'value': 'var:entity_timestamp'},
# {'action': 'ADD', 'field': 'StudyDate', 'value': 'var:item_timestamp'},
# {'action': 'ADD', 'field': 'PatientID', 'value': 'var:entity_id'},
# {'action': 'ADD', 'field': 'AccessionNumber', 'value': 'var:item_id'},
# {'action': 'ADD', 'field': 'PatientIdentityRemoved', 'value': 'Yes'}]

# or we can filter to a field
recipe.get_actions(field="PatientID")

# [{'action': 'REMOVE', 'field': 'PatientID'},
# {'action': 'ADD', 'field': 'PatientID', 'value': 'var:entity_id'}]

# and logically, both
recipe.get_actions(field="PatientID", action="REMOVE")
#  [{'action': 'REMOVE', 'field': 'PatientID'}]


################################################################################
# Replacing Identifiers
#
# The %header section of a deid recipe defines a set of actions and associated
# fields to perform them on. As we saw in the examples above, we could easily
# view and filter the actions based on the header field or action type.
#
# For this next section, we will pretend that we've just extracted ids from
# our data files (in a dictionary called ids) and we will prepare a second
# dictionary of updated fields.

##################################

# Load the dummy / example deid
path = os.path.abspath("%s/../examples/deid/" % get_installdir())
recipe = DeidRecipe(deid=path)

# What actions are defined?
recipe.get_actions()

# [{'action': 'ADD', 'field': 'PatientIdentityRemoved', 'value': 'Yes'},
#  {'action': 'REPLACE', 'field': 'PatientID', 'value': 'var:id'},
#  {'action': 'REPLACE', 'field': 'SOPInstanceUID', 'value': 'var:source_id'}]

# The above says that we are going to:
#  ADD a field PatientIdentityRemoved with value Yes
#  REPLACE PatientID with whatever value is under "id" in our updated lookup
#  REPLACE SOPInstanceUID with whatever value is under "source_id"

# We have 7 dicom cookie images we loaded above, so we have two options. We can
# either loop through the dictionary of ids and update values (in this case,
# adding values to be used as new variables) or we can make a new datastructure

# Let's be lazy and just update the extracted ones
updated_ids = dict()
count = 0
for image, fields in ids.items():
    fields["id"] = "cookiemonster"
    fields["source_id"] = "cookiemonster-image-%s" % (count)
    updated_ids[image] = fields
    count += 1

# You can look at each of the updated_ids entries and see the added variables
#  'id': 'cookiemonster',
#  'source_id': 'cookiemonster-image-2'}}

# And then use the deid recipe and updated to create new files
cleaned_files = replace_identifiers(
    dicom_files=dicom_files, deid=recipe, ids=updated_ids
)


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
cleaned_files = replace_identifiers(
    dicom_files=dicom_files, deid=recipe, ids=updated_ids, output_folder="/tmp/"
)

# Force overwrite (be careful!)
cleaned_files = replace_identifiers(
    dicom_files=dicom_files,
    deid=recipe,
    ids=updated_ids,
    output_folder="/tmp/",
    overwrite=True,
)
