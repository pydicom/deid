from deid.dicom import get_identifiers, replace_identifiers
from deid.config import DeidRecipe

# This is supported for deid.dicom version 0.1.34

# This dicom has nested InstanceCreationDate fields

dicom_files = ["MR.dcm"]

# They are extracted, and flattened in items
# 'ReferencedPerformedProcedureStepSequence__InstanceCreationDate': '20091124',

items = get_identifiers(dicom_files)

# Load in the recipe, we want to REPLACE InstanceCreationDate with a function

recipe = DeidRecipe("deid.dicom")

# Here is our function


def generate_uid(item, value, field):
    """This function will generate a dicom uid! You can expect it to be passed
       the dictionary of items extracted from the dicom (and your function)
       and variables, the original value (func:generate_uid) and the field
       name you are applying it to.
    """
    import pydicom

    # Your organization should have it's own DICOM ORG ROOT.
    # For the purpose of an example, borrowing PYMEDPHYS_ROOT_UID
    ORG_ROOT = "1.2.826.0.1.3680043.10.188"  # e.g. PYMEDPHYS_ROOT_UID
    prefix = field.lower().replace(" ", " ")
    full_uid = pydicom.uid.generate_uid(ORG_ROOT)
    return prefix + "-" + full_uid


# Add the function to each item to be found
for item in items:
    items[item]["generate_uid"] = generate_uid

# Clean the files
cleaned_files = replace_identifiers(
    dicom_files=dicom_files, deid=recipe, strip_sequences=False, ids=items
)
