#!/usr/bin/env python

from deid.dicom import get_identifiers, replace_identifiers, get_files
from deid.config import DeidRecipe
from deid.data import get_dataset

# This is supported for deid.dicom version 0.1.34

dicom_files = list(get_files(get_dataset("animals")))
print(dicom_files)

items = get_identifiers(dicom_files)

# Load in the recipe, we want to REPLACE InstanceCreationDate with a function

recipe = DeidRecipe("deid.dicom")

# Parse the files
parsed_files = replace_identifiers(
    dicom_files=dicom_files, deid=recipe, strip_sequences=False, ids=items
)

## Print two instances (one in sequence)
print(parsed_files[0].file_meta)
