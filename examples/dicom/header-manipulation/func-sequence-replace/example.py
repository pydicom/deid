from deid.dicom import get_identifiers, replace_identifiers
from deid.config import DeidRecipe

# This is supported for deid.dicom version 0.1.34

# This dicom has nested InstanceCreationDate fields

dicom_files = ['MR.dcm']

# They are extracted, and flattened in items
# 'ReferencedPerformedProcedureStepSequence__InstanceCreationDate': '20091124',

items = get_identifiers(dicom_files)

# Load in the recipe, we want to REPLACE InstanceCreationDate with a function

recipe = DeidRecipe('deid.dicom')

# Here is our function

def generate_uid(item, value, field):
    '''This function will generate a uuid! You can expect it to be passed
       the dictionary of items extracted from the dicom (and your function)
       and variables, the original value (func:generate_uid) and the field
       name you are applying it to.
    '''
    import uuid
    prefix = field.lower().replace(' ', " ")
    return prefix + "-" + str(uuid.uuid4())

# Add the function to each item to be found
for item in items:
    items[item]['generate_uid'] = generate_uid

# Clean the files
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=recipe,
                                    strip_sequences=False,
                                    ids=items)

