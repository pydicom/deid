---
title: Header Sequence Manipuation
category: Examples
order: 4
---

The code and files for this example can be found [here](https://github.com/pydicom/deid/tree/master/examples/dicom/header-manipulation/func-sequence-replace/). 
For this example, we want to replace values that are nested (in sequences).
This operation is available for deid versions 0.1.34 and later, and currently
we support `REPLACE`, and `BLANK`.


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




## Imports

We first import the functions that we need

```python
from deid.dicom import get_identifiers, replace_identifiers
from deid.config import DeidRecipe
```

We are using an MR.dcm that is provided in the example's folder linked above.


```python
dicom_files = ['MR.dcm']
items = get_identifiers(dicom_files)
```

For each item (indexed by the dicom file name), sequences 
are flattened out in the data structure. For example:

```python
 'ReferencedImageSequence__ReferencedSOPClassUID': '111111111111111111',
 'ReferencedImageSequence__ReferencedSOPInstanceUID': '111111111111111',
 'ReferencedPerformedProcedureStepSequence__InstanceCreationDate': '22222222',
 'ReferencedPerformedProcedureStepSequence__InstanceCreationTime': '22222222',
 'ReferencedPerformedProcedureStepSequence__InstanceCreatorUID': 'xxxxxxx',
 'ReferencedPerformedProcedureStepSequence__ReferencedSOPClassUID': 'xxxxxxxxxx',
 'ReferencedPerformedProcedureStepSequence__ReferencedSOPInstanceUID': 'xxxxxxxx',
```

The function we will use for the example will perform an action to generate a uid, 
but you can also use it to communicate with databases, APIs, or do something like 
save the original (and newly generated one) in some (IRB approvied) place

## The Deid Recipe

The process of updating header values means writing a series of actions
in the deid recipe, in this folder the file [deid.dicom](deid.dicom) has the
following content:

Along with a deid.dicom that asks to `REPLACE` a field with a function:

```
FORMAT dicom

%header

REPLACE InstanceCreationDate func:generate_uid
```

Let's create an instance of our recipe:

```python
# Create the DeidRecipe Instance from deid.dicom
recipe = DeidRecipe('deid.dicom')
```

Here are a few different ways to interact:

```python
# To see an entire (raw in a dictionary) recipe just look at
recipe.deid

# What is the format?
recipe.get_format()
# dicom

# What actions do we want to do on the header?
recipe.get_actions()

[{'action': 'REPLACE',
  'field': 'InstanceCreationDate',
  'value': 'func:generate_uid'}]

# We can filter to an action type (not useful here, we only have one type)
recipe.get_actions(action='REPLACE')

# or we can filter to a field
recipe.get_actions(field='InstanceCreationDate')
[{'action': 'REPLACE',
  'field': 'FrameOfReferenceUID',
  'value': 'func:generate_uid'}]

# and logically, both (not useful here)
recipe.get_actions(field='PatientID', action="REMOVE")
```

Our recipe instance is ready to go. From the above we are saying we want to replace the 
`InstanceCreationDate` field with the output from the generate_uid function, 
which is expected in the item dict. Let's write that next.

## Write Your Function

```python
def generate_uid(item, value, field):
    '''This function will generate a uuid! You can expect it to be passed
       the dictionary of items extracted from the dicom (and your function)
       and variables, the original value (func:generate_uid) and the field
       name you are applying it to.
    '''
    import uuid
    prefix = field.lower().replace(' ', " ")
    return prefix + "-" + str(uuid.uuid4())

```

As stated in the docstring, you can expect it to be passed the dictionary of 
items extracted from the dicom (and your function) and variables, the 
original value (func:generate_uid) and the field name you are applying it to.

## Update Your Items

How do we update the items? Remember, the action is: 

```
REPLACE InstanceCreationDate func:generate_uid
```

so the key for each item in items needs to be 'generate_uid." Just do this:

```python
for item in items:
    items[item]['generate_uid'] = generate_uid
```

## Replace identifiers
We are ready to go! Now let's generate the cleaned files! It will output to a 
temporary directory. Since we want to replace nested sequences, we need to
set `strip_sequences` to False.


```python
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=recipe,
                                    ids=items,
                                    strip_sequences=False)
```

Note that expansion of sequences is not currently supported for operations
that remove or add a value (ADD, REMOVE, JITTER).
You can load in a cleaned file to see what was done (a cleaned file is provided
in the example folder):

```python
from pydicom import read_file
cleaned = read_file(cleaned_files[0])
print(cleaned)

# cleaned (subset of changed)
(0008, 0012) Instance Creation Date              DA: 'instancecreationdate-2ad6c7f6-2264-4f9d-a3f2-ead2cf438fe1'
...
# here is a nested sequence
   (0008, 0012) Instance Creation Date              DA: 'instancecreationdate-7fb93a26-b2fe-446a-8899-84ac7a1fc217'
```

You can write to a different output folder by setting `output_folder` in
the function, and use `overwrite` to specify if files should be overwritten
that already exist.

Full code for the
example above is [available here](https://github.com/pydicom/deid/tree/master/examples/dicom/header-manipulation/func-sequence-replace/).
