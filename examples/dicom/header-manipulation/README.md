# Header Manipulation

Here is a quick example to show using deid to update a frame of reference UID,
and instance UIDs across a set of datasets. We aren't doing any filtering, we are just going to
change field with a value derived from a function. This example
was derived based on a prompt in [this pull request](https://github.com/pydicom/contrib-pydicom/pull/14).
Let's get started!

## Imports
We first import the functions that we need

```python
from deid.dicom import get_files, replace_identifiers
from deid.utils import get_installdir
from deid.data import get_dataset
import os
```

This will get a set of example cookie dicoms

```python
base = get_dataset('dicom-cookies')
dicom_files = list(get_files(base)) # todo : consider using generator functionality
```

This is the function to get identifiers. Identifiers are basically a dictionary
of header values extracted from each dicom, indexed by the complete file path.

```python
from deid.dicom import get_identifiers
items = get_identifiers(dicom_files)
```

The function performs an action to generate a uid, but you can also use
it to communicate with databases, APIs, or do something like
save the original (and newly generated one) in some (IRB approvied) place

## The Deid Recipe
The process of updating header values means writing a series of actions
in the deid recipe, in this folder the file [deid.dicom](deid.dicom) has the
following content:

```
FORMAT dicom

%header

REPLACE StudyInstanceUID func:generate_uid
REPLACE SeriesInstanceUID func:generate_uid
ADD FrameOfReferenceUID func:generate_uid
```

The main difference between REPLACE and ADD here is that REPLACE won't add
a value if it doesn't already exist.  Let's create an instance of our recipe:

```python
# Create the DeidRecipe Instance from deid.dicom
from deid.config import DeidRecipe
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
  'field': 'StudyInstanceUID',
  'value': 'func:generate_uid'},
 {'action': 'REPLACE',
  'field': 'SeriesInstanceUID',
  'value': 'func:generate_uid'},
 {'action': 'REPLACE',
  'field': 'FrameOfReferenceUID',
  'value': 'func:generate_uid'}]

# We can filter to an action type (not useful here, we only have one type)
recipe.get_actions(action='REPLACE')

# or we can filter to a field
recipe.get_actions(field='FrameOfReferenceUID')
[{'action': 'REPLACE',
  'field': 'FrameOfReferenceUID',
  'value': 'func:generate_uid'}]

# and logically, both (not useful here)
recipe.get_actions(field='PatientID', action="REMOVE")
```

Our recipe instance is ready to go. From the above we are saying we want to replace the fields above with the
output from the generate_uid function, which is expected in the item dict. Let's write
that next.

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

but if we want to be more correct and adhere to the [dicom standard](http://dicom.nema.org/medical/Dicom/2017c/output/chtml/part05/chapter_B.html), we would want
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
    # For the purpose of an example, borrowing PYMEDPHYS_ROOT_UID.
    #
    # When using a UUID to dynamically create a UID (e.g. SOPInstanceUID),
    # the root '2.25' can be used instead of an organization's root.
    # For more information see DICOM PS3.5 2020b B.2
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

## Update Your Items

How do we update the items? Remember, the action is:

```
REPLACE StudyInstanceUID func:generate_uid
```

so the key for each item in items needs to be 'generate_uid." Just do this:

```python
for item in items:
    items[item]['generate_uid'] = generate_uid
```

## Replace identifiers
We are ready to go! Now let's generate the cleaned files! It will output to a
temporary directory.

```python
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=recipe,
                                    ids=items)

```

You can inspect the first cleaned file in the list:

```python
cleaned_files[0]
(0020, 000d) Study Instance UID                  UI: studyinstanceuid-1.2.826.0.1.3680043.10.188.1803528571851574950019323462792270863
(0020, 000e) Series Instance UID                 UI: seriesinstanceuid-1.2.826.0.1.3680043.10.188.1218768560803332968447018964651707696
(0020, 0052) Frame of Reference UID              UI: frameofreferenceuid-1.2.826.0.1.3680043.10.188.3138524385829221974514732538424409758
```

That's it! If you need any help, please open an issue.
