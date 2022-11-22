---
title: Header Sequence Manipuation
category: Examples
order: 4
---

The code and files for this example can be found [here](https://github.com/pydicom/deid/tree/master/examples/dicom/header-manipulation/func-sequence-replace/).
For this example, we want to replace values that are nested (in sequences).
This operation is available for deid versions 0.1.34 and later, and currently
we support `REPLACE`, and `BLANK`.

<a id="imports">
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

<a id="the-deid-recipe">
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
  'field': 'InstanceCreationDate',
  'value': 'func:generate_uid'}]

# and logically, both (not useful here)
recipe.get_actions(field='PatientID', action="REMOVE")
```

Our recipe instance is ready to go. From the above we are saying we want to replace the
`InstanceCreationDate` field with the output from the generate_uid function,
which is expected in the item dict. Let's write that next.

<a id="write-your-function">
## Write Your Function

A simple function with a uid generated from the uuid library might look like
this:

```python
def generate_uid(item, value, field):
    '''This function will generate a uuid! You can expect it to be passed
       the dictionary of items extracted from the dicom (and your function)
       and variables, the original value (func:generate_uid) and the field
       name you are applying it to.
    '''
    import uuid
    # a field can either be just the name string, or a DicomElement
    if hasattr(field, 'name'):
        field = field.name
    prefix = field.lower().replace(' ', " ")
    return prefix + "-" + str(uuid.uuid4())

```

but if we want to be more correct and adhere to the dicom standard, we would want
to do:

```python
def generate_uid(item, value, field, dicom):
    '''This function will generate a dicom uid! You can expect it to be passed
       the dictionary of items extracted from the dicom (and your function)
       and variables, the original value (func:generate_uid) and the field
       object you are applying it to.
    '''
    import uuid

    # a field can either be just the name string, or a DicomElement
    if hasattr(field, 'name'):
        field = field.name

    # Your organization should have it's own DICOM ORG ROOT.
    # For the purpose of an example, borrowing PYMEDPHYS_ROOT_UID
    ORG_ROOT = "1.2.826.0.1.3680043.10.188"  # e.g. PYMEDPHYS_ROOT_UID
    prefix = field.lower().replace(' ', " ")
    bigint_uid = str(uuid.uuid4().int)
    full_uid = ORG_ROOT + "." + bigint_uid
    sliced_uid = full_uid[0:64]  # A DICOM UID is limited to 64 characters
    return prefix + "-" + sliced_uid
```

As stated in the docstring, you can expect it to be passed the dictionary of
items extracted from the dicom (and your function) and variables, the
original value (func:generate_uid) and the field name you are applying it to.

<a id="development-tip">
## Development Tip

If you want to interactively develop and test what is passed to the function,
just insert an embedded ipython into the function:

```python
def generate_uid(item, value, field, dicom):
    '''This function will generate a dicom uid! You can expect it to be passed
       the dictionary of items extracted from the dicom (and your function)
       and variables, the original value (func:generate_uid) and the field
       object you are applying it to.
    '''
    import IPython
    IPython.embed()
```

And then proceed running the replace operation. This will put your into an
interactive session and have all the variables available to you for inspection.
For example:

```python
item
# {'(0008, 0005)': (0008, 0005) Specific Character Set              CS: 'ISO_IR 100'  [SpecificCharacterSet],
# ...
# 'generate_uid': <function __main__.generate_uid(item, value, field, dicom)>}

value
# 'func:generate_uid'

field
# (0020, 000d) Study Instance UID                  UI: 1.2.276.0.7230010.3.1.2.8323329.5329.1495927169.580350  [StudyInstanceUID]

dicom
# (0008, 0005) Specific Character Set              CS: 'ISO_IR 100'
...
```

And note that field can be the string identifier, or the full element, depending
on how it is used internally, so you should always check.

<a id="update-your-items">
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

<a id="replace-identifiers">
## Replace identifiers
We are ready to go! Now let's generate the cleaned files! It will output to a
temporary directory. Since we want to replace nested sequences, we need to
set `strip_sequences` to False.


```python
# Clean the files
cleaned_files = replace_identifiers(
    dicom_files=dicom_files, deid=recipe, strip_sequences=False, ids=items
)
```

Note that expansion of sequences is not currently supported for operations
that remove or add a value (ADD, REMOVE, JITTER).
You can load in a cleaned file to see what was done

```python
print(cleaned_files[0].InstanceCreationDate)
print(cleaned_files[0].ReferencedPerformedProcedureStepSequence[0].InstanceCreationDate)

20200608
20200608
```

Full code for the
example above is [available here](https://github.com/pydicom/deid/tree/master/examples/dicom/header-manipulation/func-sequence-replace/).
