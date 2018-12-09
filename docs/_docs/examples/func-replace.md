---
title: Header Manipuation
category: Examples
order: 4
---

As we've discussed, the basic actions of using header filters to flag images, 
and performing actions on headers (for replacement), are controlled by a text file called 
a deid recipe. If you want a reminder about how to write this text file, 
[read here]({{ site.baseurl }}/getting-started/dicom-config). In this example,
we will walk through basic actions that might say something like:

 > Replace Field A with the output of a function called generate_uid

Specifically, we can define a set of REPLACE and ADD actions:

```
FORMAT dicom

%header

REPLACE StudyInstanceUID func:generate_uid
REPLACE SeriesInstanceUID func:generate_uid
ADD FrameOfReferenceUID func:generate_uid
```

# Function Header Actions

Here is a quick example to show using deid to update a frame of reference UID,
and instance UIDs across a set of datasets. We aren't doing any filtering, we are just going to
change field with a value derived from a function. This example
was derived based on a prompt in [this pull request](https://github.com/pydicom/contrib-pydicom/pull/14).
If you are interested in the code for this example, it's available
[here](https://github.com/pydicom/deid/tree/master/examples/dicom/header-manipulation).
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

## Write Your Funtion

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

You can load in a cleaned file to see what was done

```python
from pydicom import read_file
test_file = read_file(cleaned_files[0])
print(test_file)

# test_file (subset of changed)
# (0020, 000d) Study Instance UID                  UI: studyinstanceuid-022f82f4-e9df-4533-b237-6ab563dfaf56
# (0020, 000e) Series Instance UID                 UI: seriesinstanceuid-6a3a0ac8-22fd-449f-9779-2580cf2897bd
# (0020, 0052) Frame of Reference UID              UI: frameofreferenceuid-0693b1fa-9144-4a1d-9cb7-82da56e462ce
```

Finally, if you want to write to a different output folder, here is how to do that:

```python
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=recipe,
                                    ids=items,
                                    output_folder='/tmp/')

# Force overwrite (be careful!)
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=recipe,
                                    ids=items,
                                    output_folder='/tmp/',
                                    overwrite=True)

```

That's it! If you need any help, please open an issue. Full code for the
example above is [available here](https://github.com/pydicom/deid/tree/master/examples/dicom/header-manipulation).
