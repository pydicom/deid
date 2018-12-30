---
title: Header Expansion
category: Examples
order: 5
---

This example will walk through how to use <a href="https://pydicom.github.io/deid/user-docs/recipe-headers/#field-expansion" target="_blank">header expansion</a>
to select more than one field from a dicom header to apply an action to. We will
first show examples that you can write into [a deid recipe](https://pydicom.github.io/deid/examples/recipe/)
to keep a record of your dicom header edits. We will then show the same
(and more advanced) actions working with expanders directly in Python. Let's go!

## Deid Recipes

Let's say I want to:

**Blank all fields that end with "Name"**

I would write the following into my [deid recipe](https://pydicom.github.io/deid/examples/recipe/):

```
BLANK endswith:Name
```

**Blank all fields that start with Patient**

```
BLANK startswith:Patient
```

**Blank all fields that contain Patient or Physician**

```
BLANK contains:Patient|Physician
```

**Jitter the date for a specific field**

Specifically, add 31 days to it.

```
JITTER PatientBirthDate 31
```

**Jitter the timestamp for all fields that contain the work date**

```
JITTER contains:date 31
```

**Apply your special function to ALL fields**

```
def add_pusheen(field, value)
```


## Python Examples

If you want to use the expanders in your code, that's easy too! Here
are the same examples. Let's first start with reading in a dicom file, 
such as one of the dicom-cookies examples provided with deid.

## Imports
We first import the functions that we need

```python
from deid.dicom import get_files
from deid.data import get_dataset
```

Let's get those cookies!

```python
base = get_dataset('dicom-cookies')
dicom_files = list(get_files(base)) 
```

`dicom_files` is a list of the complete paths for 7 dicom cookie examples.

## Explore Expanders

For the purpose of exploration, let's load one file.

```python
from pydicom import read_file
dicom = read_file(dicom_files[0])
```

Let's play with our expanders! Remember the examples above that we wrote into
a deid recipe? Let me know you how those work. First, here is the function that
we import:

```python
from deid.dicom.fields import expand_field_expression
```

None of the actions (BLANK, JITTER, etc.) are relevant here; we just want to get back the list of
fields that meet some criteria.  Given an action, these fields would be 
passed on to the next step in deid to handle the blank action. 
You could also use this function to interactively explore the header data, or another purpose.

**Select all fields that end with "Name"**

Let's get back the list of fields that end with name.

```python
# endswith:Address
fields = expand_field_expression("endswith:Name", dicom)
['InstitutionName', 'OperatorsName', 'PatientName', 'ReferringPhysicianName']
```

Notice that we are passing the dicom image, and the list returned in fact ends
with name. Capitalization of "Name" "name" "nAmE" does not matter.


**Select all fields that start with Patient**

```python
# startswith:Patient
fields = expand_field_expression("startswith:Patient", dicom)
['PatientBirthDate',
 'PatientID',
 'PatientName',
 'PatientOrientation',
 'PatientSex']
```

**Select all fields that contain Physician or Patient**

```python
# contains:Patient|Physician
fields = expand_field_expression("contains:Patient|Physician", dicom)
['NameOfPhysiciansReadingStudy',
 'PatientBirthDate',
 'PatientID',
 'PatientName',
 'PatientOrientation',
 'PatientSex',
 'ReferringPhysicianName']
```

**Select all fields except PatientName or PatientSex**

We know there are a total of 34 fields, so this should select 32.

```python
# except:PatientName|PatientSex
fields = expand_field_expression("except:PatientName|PatientSex", dicom)
len(fields)
# 32
```

**Select a specific field**

This is a fairly silly example to show, but for many actions you may just choose
a single field. That would look like this:

```python
fields = expand_field_expression("PatientID", dicom)
['PatientID']
```

### All Fields

**Apply your special function to ALL fields**

This is a more complex (and fun!) example. We want to apply a function to
ALL fields. For this example, we will work with a deid recipe. Here is what
the recipe "deid.dicom-pusheen" looks like.

```
%header

REPLACE all func:pusheenize
```

```python
from deid.config import DeidRecipe
recipe = DeidRecipe('deid.dicom-pusheen')
```

```python
recipe.get_actions()
Out[47]: [{'action': 'REPLACE', 'field': 'all', 'value': 'func:pusheenize'}]
```

#### 1. Extract Identifiers

We would first need to extract what is currently there. Identifiers are basically a dictionary
of header values extracted from each dicom, indexed by the complete file path.
Let's run this over the entire dicom-cookies dataset.

```python
from deid.dicom import get_identifiers
items = get_identifiers(dicom_files)
```

The items is a lookup dictionary mapping dicom files to a dictionary of fields
and corresponding values. Now let's write our function.

#### 2. Write Our Function!

Notice the reference to a "func:pusheenize" in the recipe? We need that function
in the Python environment before we replace identifiers. The function we write should have arguments:

 - item: is going to be the dictionary of fields (keys) and respective values for the dicom being processed. We do this to make all data in the dicom header available to you.
 - value: Is the function name (e.g., func:pusheen) that you've defined.
 - field: if the name of the field, e.g., PatientID.

```python
def pusheenize(item, value, field):
    value = item.get(field, '')
    if "Name" in field:
        value = "Pusheena" + value.replace(' ', '')
    return value
```

To not forget that we are showing examples with expand_field_expression, this quick 
snippet simple shows that the list of field names is the entire
set included with the dicom.

```python
len(dicom.dir())
# 34   (--- we have 34 fields
fields = expand_field_expression('all', dicom)
len(fields)
# 34   (--- we selected all 34 fields
```

Then we would add the function to each item to be found when it's looked up:

```python
for item in items:
    items[item]['pusheenize'] = pusheenize
```

#### 3. Replace Identifiers
given that our function is in the python working environment, we would
have extracted identifiers like this. We don't want to save them
so we set save to False. If we set save to True, they would be saved to a temporary directory. 

```python
from deid.dicom import replace_identifiers
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=recipe, 
                                    save=False,
                                    ids=items)
```

Let's look at the first cleaned dicom. Is it pusheenized?

```python
In [78]: cleaned_files[0]
Out[78]: 
(0008, 0005) Specific Character Set              CS: 'ISO_IR 100'
(0008, 0016) SOP Class UID                       UI: Secondary Capture Image Storage
(0008, 0018) SOP Instance UID                    UI: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
(0008, 0020) Study Date                          DA: '20131210'
(0008, 0030) Study Time                          TM: '191929'
(0008, 0050) Accession Number                    SH: ''
(0008, 0064) Conversion Type                     CS: 'WSD'
(0008, 0080) Institution Name                    LO: 'PusheenaSTANFORD'
(0008, 0090) Referring Physician's Name          PN: 'PusheenaDr.whitebush'
(0008, 1060) Name of Physician(s) Reading Study  PN: 'PusheenaDr.agedhill'
(0008, 1070) Operators' Name                     PN: 'Pusheenaboldbread'
(0010, 0010) Patient's Name                      PN: 'Pusheenaflatglade'
(0010, 0020) Patient ID                          LO: 'cookie-47'
(0010, 0030) Patient's Birth Date                DA: ''
(0010, 0040) Patient's Sex                       CS: 'M'
(0020, 000d) Study Instance UID                  UI: 1.2.276.0.7230010.3.1.2.8323329.5323.1495927169.335275
(0020, 000e) Series Instance UID                 UI: 1.2.276.0.7230010.3.1.3.8323329.5323.1495927169.335274
(0020, 0010) Study ID                            SH: ''
(0020, 0011) Series Number                       IS: ''
(0020, 0013) Instance Number                     IS: ''
(0020, 0020) Patient Orientation                 CS: ''
(0020, 4000) Image Comments                      LT: 'This is a cookie tumor dataset for testing dicom tools.'
(0028, 0002) Samples per Pixel                   US: '3'
(0028, 0004) Photometric Interpretation          CS: 'YBR_FULL_422'
(0028, 0006) Planar Configuration                US: '0'
(0028, 0010) Rows                                US: '1536'
(0028, 0011) Columns                             US: '2048'
(0028, 0100) Bits Allocated                      US: '8'
(0028, 0101) Bits Stored                         US: '8'
(0028, 0102) High Bit                            US: '7'
(0028, 0103) Pixel Representation                US: '0'
(0028, 2110) Lossy Image Compression             CS: '01'
(0028, 2114) Lossy Image Compression Method      CS: 'ISO_10918_1'
(7fe0, 0010) Pixel Data                          OB or OW: ''
```

I'll filter it down to the fields with name to make it easy for you!

```
(0008, 0080) Institution Name                    LO: 'PusheenaSTANFORD'
(0008, 0090) Referring Physician's Name          PN: 'PusheenaDr.whitebush'
(0008, 1060) Name of Physician(s) Reading Study  PN: 'PusheenaDr.agedhill'
(0008, 1070) Operators' Name                     PN: 'Pusheenaboldbread'
(0010, 0010) Patient's Name                      PN: 'Pusheenaflatglade'
```

If you are clever, you'll notice that we didn't need to select all fields.
We could have written this instead:

```
%header

REPLACE contains:name func:pusheenize
```

But this is up to you! We have pusheenized the data, our job is done.
