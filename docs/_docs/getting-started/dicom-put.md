---
title: 5. Put Identifiers Back
category: Getting Started
order: 7
---

At this point, we have a bunch of dicom files, have written a recipe with 
actions, and want to run those actions across the files. The easiest way
to do this is with the `DicomParser`

<a id="dicom-parser">
## DicomParser

The dicom parser is a helper class that will make it easy to load in your recipe,
and perform custom actions on it, and then save (or not). Let's first
get the full path to a cat dataset, and a recipe with actions to take.

```python
# dicom
from deid.data import get_dataset
from deid.dicom import get_files

base = get_dataset("dicom-cookies")
dicom_file = next(get_files(base))

# recipe
from deid.utils import get_installdir
import os
path = os.path.abspath("%s/../examples/deid/deid.dicom-groups" % get_installdir())
```

Let's now import the DicomParser and 

```python
from deid.dicom.parser import DicomParser
parser = DicomParser(dicom_file, recipe=path)
```

<a id="inspecting-the-loaded-dicom">
### 1. Inspecting the Loaded Dicom

You can see that the dicom is loaded:

```python
parser.dicom
Out[32]: 
(0008, 0005) Specific Character Set              CS: 'ISO_IR 100'
(0008, 0016) SOP Class UID                       UI: Secondary Capture Image Storage
(0008, 0018) SOP Instance UID                    UI: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
(0008, 0020) Study Date                          DA: '20131210'
(0008, 0030) Study Time                          TM: '191929'
(0008, 0050) Accession Number                    SH: ''
(0008, 0064) Conversion Type                     CS: 'WSD'
(0008, 0080) Institution Name                    LO: 'STANFORD'
(0008, 0090) Referring Physician's Name          PN: 'Dr. solitary heart'
(0008, 1060) Name of Physician(s) Reading Study  PN: 'Dr. lively wind'
(0008, 1070) Operators' Name                     PN: 'curly darkness'
(0010, 0010) Patient's Name                      PN: 'falling disk'
(0010, 0020) Patient ID                          LO: 'cookie-47'
(0010, 0030) Patient's Birth Date                DA: ''
(0010, 0040) Patient's Sex                       CS: 'M'
(0020, 000d) Study Instance UID                  UI: 1.2.276.0.7230010.3.1.2.8323329.5329.1495927169.580350
(0020, 000e) Series Instance UID                 UI: 1.2.276.0.7230010.3.1.3.8323329.5329.1495927169.580349
(0020, 0010) Study ID                            SH: ''
(0020, 0011) Series Number                       IS: ''
(0020, 0013) Instance Number                     IS: ''
(0020, 0020) Patient Orientation                 CS: ''
(0020, 4000) Image Comments                      LT: 'This is a cookie tumor dataset for testing dicom tools.'
(0028, 0002) Samples per Pixel                   US: 3
(0028, 0004) Photometric Interpretation          CS: 'YBR_FULL_422'
(0028, 0006) Planar Configuration                US: 0
(0028, 0010) Rows                                US: 1536
(0028, 0011) Columns                             US: 2048
(0028, 0100) Bits Allocated                      US: 8
(0028, 0101) Bits Stored                         US: 8
(0028, 0102) High Bit                            US: 7
(0028, 0103) Pixel Representation                US: 0
(0028, 2110) Lossy Image Compression             CS: '01'
(0028, 2114) Lossy Image Compression Method      CS: 'ISO_10918_1'
(7fe0, 0010) Pixel Data                          OB: Array of 652494 bytes
```

Notice that we *don't* have a field for `PatientIdentityRemoved`, and the Patient name
and Operator Name are some original value. Notice that since we haven't parsed anything
yet, the parser.fields is empty:

```python
parser.fields
{}
```

The recipe is provided by the parser too!

```python
parser.recipe
[deid]
```

Actually, let's look in detail at the recipe so we know the actions that are going to be
taken.

```python
OrderedDict([('format', 'dicom'),
             ('values',
              OrderedDict([('cookie_names',
                            [{'action': 'SPLIT',
                              'field': 'PatientID',
                              'value': 'by="^";minlength=4'}]),
                           ('operator_names',
                            [{'action': 'FIELD',
                              'field': 'startswith:Operator'}])])),
             ('fields',
              OrderedDict([('instance_fields',
                            [{'action': 'FIELD',
                              'field': 'contains:Instance'}])])),
             ('header',
              [{'action': 'ADD',
                'field': 'PatientIdentityRemoved',
                'value': 'Yes'},
               {'action': 'REPLACE',
                'field': 'values:cookie_names',
                'value': 'var:id'},
               {'action': 'REPLACE',
                'field': 'values:operator_names',
                'value': 'var:source_id'},
               {'action': 'REMOVE', 'field': 'fields:instance_fields'}])])
```

Under "values," each named entry is a list of actions to take to derive a list of values
to be used later. Under "fields" it's the same, but we will extract fields for later.
Under "header" is where we see our list of actions. We want to:

 - add a field, `PatientIdentityRemoved` with value `Yes`
 - replace any values that are found in the list of extracted "cookie_names" with a variable we call id
 - replace any values under "operator_names" that we define with a variable we call "source_id"
 - remove any fields that quality under "instance_fields"

<a id="understanding-fields-and-values">
### 2. Understanding fields and values

The "values" and "fields" lists will be calculated based on your data. For example,
this rule:

```
{"operator_names": {'action': 'FIELD', 'field': 'startswith:Operator'}}
```

says that we are going to derive a list called "operator_names" that includes
all the values under fields that start with "Operator." This should come down to
one field, `OperatorsName`, which is "curly darkness."

<a id="understanding-var-and-func">
### 3. Understanding var and func

If you have a recipe that references a "var:name" or func:name" you would need
to provide that directly to the parser. For the above example, we are referencing
variables called "id" and "source_id" so we should define them for the parser:

```python
parser.define('id', 'new-cookie-id')
parser.define('source_id', 'new-operator-id')
```

You would do the same thing for a named function. Where do these end up? In  a lookup
held by the parser:

```python
parser.lookup                                                                                                                                
{'id': 'new-cookie-id', 'source_id': 'new-operator-id'}
```

So they will be available when you parse.

### 4. Parse Away!

Now that we've defined the variables that we need, and we've loaded our recipe
and dicom, let's perform the parse action! By default, sequences and private 
tags are not removed (so they are included in parsing).

```python
parser.parse(strip_sequences=False, remove_private=False)
```

After this, you'll notice that the parser.fields is populated:

```python
{'(0008, 0005)': (0008, 0005) Specific Character Set              CS: 'ISO_IR 100'  [SpecificCharacterSet],
 '(0008, 0016)': (0008, 0016) SOP Class UID                       UI: Secondary Capture Image Storage  [SOPClassUID],
 '(0008, 0018)': (0008, 0018) SOP Instance UID                    UI: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351  [SOPInstanceUID],
 '(0008, 0020)': (0008, 0020) Study Date                          DA: '20131210'  [StudyDate],
 '(0008, 0030)': (0008, 0030) Study Time                          TM: '191929'  [StudyTime],
 '(0008, 0050)': (0008, 0050) Accession Number                    SH: ''  [AccessionNumber],
 '(0008, 0064)': (0008, 0064) Conversion Type                     CS: 'WSD'  [ConversionType],
 '(0008, 0080)': (0008, 0080) Institution Name                    LO: 'STANFORD'  [InstitutionName],
 '(0008, 0090)': (0008, 0090) Referring Physician's Name          PN: 'Dr. solitary heart'  [ReferringPhysicianName],
 '(0008, 1060)': (0008, 1060) Name of Physician(s) Reading Study  PN: 'Dr. lively wind'  [NameOfPhysiciansReadingStudy],
 '(0008, 1070)': (0008, 1070) Operators' Name                     PN: 'new-operator-id'  [OperatorsName],
 '(0010, 0010)': (0010, 0010) Patient's Name                      PN: 'falling disk'  [PatientName],
 '(0010, 0020)': (0010, 0020) Patient ID                          LO: 'new-cookie-id'  [PatientID],
 '(0010, 0030)': (0010, 0030) Patient's Birth Date                DA: ''  [PatientBirthDate],
 '(0010, 0040)': (0010, 0040) Patient's Sex                       CS: 'M'  [PatientSex],
 '(0020, 000d)': (0020, 000d) Study Instance UID                  UI: 1.2.276.0.7230010.3.1.2.8323329.5329.1495927169.580350  [StudyInstanceUID],
 '(0020, 000e)': (0020, 000e) Series Instance UID                 UI: 1.2.276.0.7230010.3.1.3.8323329.5329.1495927169.580349  [SeriesInstanceUID],
 '(0020, 0010)': (0020, 0010) Study ID                            SH: ''  [StudyID],
 '(0020, 0011)': (0020, 0011) Series Number                       IS: ''  [SeriesNumber],
 '(0020, 0013)': (0020, 0013) Instance Number                     IS: ''  [InstanceNumber],
 '(0020, 0020)': (0020, 0020) Patient Orientation                 CS: ''  [PatientOrientation],
 '(0020, 4000)': (0020, 4000) Image Comments                      LT: 'This is a cookie tumor dataset for testing dicom tools.'  [ImageComments],
 '(0028, 0002)': (0028, 0002) Samples per Pixel                   US: 3  [SamplesPerPixel],
 '(0028, 0004)': (0028, 0004) Photometric Interpretation          CS: 'YBR_FULL_422'  [PhotometricInterpretation],
 '(0028, 0006)': (0028, 0006) Planar Configuration                US: 0  [PlanarConfiguration],
 '(0028, 0010)': (0028, 0010) Rows                                US: 1536  [Rows],
 '(0028, 0011)': (0028, 0011) Columns                             US: 2048  [Columns],
 '(0028, 0100)': (0028, 0100) Bits Allocated                      US: 8  [BitsAllocated],
 '(0028, 0101)': (0028, 0101) Bits Stored                         US: 8  [BitsStored],
 '(0028, 0102)': (0028, 0102) High Bit                            US: 7  [HighBit],
 '(0028, 0103)': (0028, 0103) Pixel Representation                US: 0  [PixelRepresentation],
 '(0028, 2110)': (0028, 2110) Lossy Image Compression             CS: '01'  [LossyImageCompression],
 '(0028, 2114)': (0028, 2114) Lossy Image Compression Method      CS: 'ISO_10918_1'  [LossyImageCompressionMethod],
 '(7fe0, 0010)': (7fe0, 0010) Pixel Data                          OB: Array of 652494 bytes  [PixelData],
 '(0012, 0062)': (0012, 0062) Patient Identity Removed            CS: 'Yes'  [PatientIdentityRemoved]}
```

And each of the above is a DicomField, as discussed previously [here]({{ site.baseurl}}/getting-started/dicom-get/).
Now if we look at the parser.lookup, we will see that all of the actions have been performed
to extract data specific to the dicom for later use:

```python
{'id': 'new-cookie-id',
 'source_id': 'new-operator-id',
 'cookie_names': ['cookie-47'],
 'operator_names': ['curly darkness'],
 'instance_fields': {'(0008, 0018)': (0008, 0018) SOP Instance UID                    UI: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351  [SOPInstanceUID],
  '(0020, 000d)': (0020, 000d) Study Instance UID                  UI: 1.2.276.0.7230010.3.1.2.8323329.5329.1495927169.580350  [StudyInstanceUID],
  '(0020, 000e)': (0020, 000e) Series Instance UID                 UI: 1.2.276.0.7230010.3.1.3.8323329.5329.1495927169.580349  [SeriesInstanceUID],
  '(0020, 0013)': (0020, 0013) Instance Number                     IS: ''  [InstanceNumber]}}
```

Importantly, if we look at the parser.dicom, the replacement has been done. Notice the Patient ID and
Operator's name are changed, as is added the `PatientIdentityRemoved`. and the Instance fields are removed.

```python
(0008, 0005) Specific Character Set              CS: 'ISO_IR 100'
(0008, 0016) SOP Class UID                       UI: Secondary Capture Image Storage
(0008, 0020) Study Date                          DA: '20131210'
(0008, 0030) Study Time                          TM: '191929'
(0008, 0050) Accession Number                    SH: ''
(0008, 0064) Conversion Type                     CS: 'WSD'
(0008, 0080) Institution Name                    LO: 'STANFORD'
(0008, 0090) Referring Physician's Name          PN: 'Dr. solitary heart'
(0008, 1060) Name of Physician(s) Reading Study  PN: 'Dr. lively wind'
(0008, 1070) Operators' Name                     PN: 'new-operator-id'
(0010, 0010) Patient's Name                      PN: 'falling disk'
(0010, 0020) Patient ID                          LO: 'new-cookie-id'
(0010, 0030) Patient's Birth Date                DA: ''
(0010, 0040) Patient's Sex                       CS: 'M'
(0012, 0062) Patient Identity Removed            CS: 'Yes'
(0020, 0010) Study ID                            SH: ''
(0020, 0011) Series Number                       IS: ''
(0020, 0020) Patient Orientation                 CS: ''
(0020, 4000) Image Comments                      LT: 'This is a cookie tumor dataset for testing dicom tools.'
(0028, 0002) Samples per Pixel                   US: 3
(0028, 0004) Photometric Interpretation          CS: 'YBR_FULL_422'
(0028, 0006) Planar Configuration                US: 0
(0028, 0010) Rows                                US: 1536
(0028, 0011) Columns                             US: 2048
(0028, 0100) Bits Allocated                      US: 8
(0028, 0101) Bits Stored                         US: 8
(0028, 0102) High Bit                            US: 7
(0028, 0103) Pixel Representation                US: 0
(0028, 2110) Lossy Image Compression             CS: '01'
(0028, 2114) Lossy Image Compression Method      CS: 'ISO_10918_1'
(7fe0, 0010) Pixel Data                          OB: Array of 652494 bytes
```

And you could save your data to file.

```python
parser.save("/tmp/mydicom.dcm")
```
<a id="replace-identifers">
## Replace Identifiers

If you want to do the above in bulk, you might find it easier to use the `replace_identifiers`
function.

```python
from deid.dicom import get_files
from deid.data import get_dataset
base = get_dataset('dicom-cookies')
dicom_files = list(get_files(base))
```

Let's import the function, and get back a list of dicom objects to interact with.
If we don't provide a recipe, deid will use it's default.

```python
from deid.dicom import replace_identifiers
cleaned_dicoms = replace_identifiers(dicom_files=dicom_files)
```

The default recipe you can view [here](https://github.com/pydicom/deid/blob/master/deid/data/deid.dicom#L744).
It's fairly aggressive and generally removes times and other identifiers. But *you should not use this verbatim!*
It's important that you develop a strategy that is most robust for your datasets.
The example is provided as a conservative start. If you want to save to temporary
files, you can specify save=True:

```python
cleaned_files = replace_identifiers(dicom_files=dicom_files, save=True)
```

You will notice that by default, the files are written to a temporary directory:

```python
cleaned_files 
['/tmp/tmphvj05c6y/image4.dcm',
 '/tmp/tmphvj05c6y/image2.dcm',
 '/tmp/tmphvj05c6y/image7.dcm',
 '/tmp/tmphvj05c6y/image6.dcm',
 '/tmp/tmphvj05c6y/image3.dcm',
 '/tmp/tmphvj05c6y/image1.dcm',
 '/tmp/tmphvj05c6y/image5.dcm']
```

You can choose to use a custom output folder:

```python
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    output_folder='/home/vanessa/Desktop')
...python
cleaned_files
['/home/vanessa/Desktop/image4.dcm',
 '/home/vanessa/Desktop/image2.dcm',
 '/home/vanessa/Desktop/image7.dcm',
 '/home/vanessa/Desktop/image6.dcm',
 '/home/vanessa/Desktop/image3.dcm',
 '/home/vanessa/Desktop/image1.dcm',
 '/home/vanessa/Desktop/image5.dcm']
```

One setting that is important is `overwrite`, which is by default set to False. 
For example, let's say we decided to run the above again, using the same output 
directory of desktop (where the files already exist!)

```python
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
ERROR image4.dcm already exists, overwrite set to False. Not writing.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
ERROR image2.dcm already exists, overwrite set to False. Not writing.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
ERROR image7.dcm already exists, overwrite set to False. Not writing.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
ERROR image6.dcm already exists, overwrite set to False. Not writing.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
ERROR image3.dcm already exists, overwrite set to False. Not writing.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
ERROR image1.dcm already exists, overwrite set to False. Not writing.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
ERROR image5.dcm already exists, overwrite set to False. Not writing.
```

The function gets angry at us, and returns the list of files that are already 
there. If you really want to force an overwrite, then you need to do this:


```python
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    output_folder='/home/vanessa/Desktop',
                                    overwrite=True)
```

wherever you dump your new dicoms, it's up to you to decide how to then move 
and store them, and (likely) deal with the original data with identifiers.

<a id="private-tags">
## Private Tags

An important note is that by default, this function will keep private tags
 (`remove_private=False`). If you need to remove private tags 
you would want to set this to True.


```python
# Clean the files, but set remove_private to True
cleaned_dicom = replace_identifiers(dicom_files=dicom_files,
                                    remove_private=True)
```

If you want to keep the tags (default) but then go back and remove them,
you can use the `remove_private_identifiers` function:

```python
from deid.dicom import remove_private_identifiers

really_cleaned = remove_private_identifiers(dicom_files=cleaned_files)
```

You could also do pixel scraping first, and then call the function
(per default) to remove private.

<a id="getting-private-tags">
### Getting Private Tags

If you are working within python and want to get private tags for inspection, 
you can do that too! Let's first load some default data:


```python
from deid.dicom import get_files
from deid.data import get_dataset
base = get_dataset('dicom-cookies')
dicom_files = list(get_files(base))
```

and now the functions we can use. We will look at one dicom_file

```python
from deid.dicom.tags import has_private, get_private

from pydicom import read_file
dicom = read_file(dicom_files[0])
```

Does it have private tags?

```python
has_private(dicom)
Found 0 private tags
False
```

Nope! This is a dicom cookie, after all. If we wanted to get the list of tags, we could do:

```python
private_tags = get_private(dicom)
```

Although in this case, the list is empty.

<a id="developer-replacement">
## Developer Replacement

If you are a developer, you can create your own config.json OR deid recipe for the functions above.
You can read more about this in the [developers]({{ site.baseurl}}/development/) notes.
