---
title: 3. Get Identifiers (GET)
category: Getting Started
order: 5
---

<a id="data">
## Data

To run these examples, you'll need to install external deid-data.

```bash
$ pip install deid-data
```


<a id="get-identifiers">
## Get Identifiers

A get request using the deid module will return a data structure with headers found in a particular dataset.
Let's walk through these steps. As we did in the [loading]({{ site.baseurl }}/getting-started/dicom-loading),
the first step was to load a dicom dataset:


```python
from deid.data import get_dataset
from deid.dicom import get_files

base = get_dataset("dicom-cookies")
dicom_files = list(get_files(base))
```

We now have our small dataset that we want to de-identify! The first step is to get
the identifiers. By default, we will return all of them. That call will look like this:

```python
from deid.dicom import get_identifiers
ids = get_identifiers(dicom_files)
```

You'll get back a dictionary(indexed by the file name) for each dicom file.
Within each entry, the value is another dictionary with an expanded string of
the tag. For example:

```
ids[dicom_files[0]]
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
 '(0008, 1070)': (0008, 1070) Operators' Name                     PN: 'curly darkness'  [OperatorsName],
 '(0010, 0010)': (0010, 0010) Patient's Name                      PN: 'falling disk'  [PatientName],
 '(0010, 0020)': (0010, 0020) Patient ID                          LO: 'cookie-47'  [PatientID],
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
 '(7fe0, 0010)': (7fe0, 0010) Pixel Data                          OB: Array of 652494 bytes  [PixelData]}
```

If there is a nested tag, you'll see it with the format `(7fe0, 0010)__(0080, 0012)`. If there
is a nested sequence, you'll see the index provided in that same format. For example,
`(7fe0, 0010)__0__(0080, 0012)` counts as the first element of a sequence,
and `(7fe0, 0010)__1__(0080, 0012)` the second. We start counting at 0, we aren't barbarians!

<a id="dicomfield">
## DicomField

The content of each field is a DicomField, which carries with it the
dicom tag (string), name (string), and the actual element for further
parsing. For example:

```python
field = ids[dicom_files[0]]['(0010, 0010)']

field.element
(0010, 0010) Patient's Name                      PN: 'falling disk'

field.name
'PatientName'

field.uid
'(0010, 0010)'
```

The field.element is what you would get if you indexed the dicom Dataset
at dicom.get("PatientName"). The name refers to the keyword (which, if there
is nesting, will include that. For example, a Sequence with header value `AdditionalData`
and item `Modality` will be returned as `AdditionalData_Modality`,
and this name string is used to help with filters. The uid would also
include the index of the sequence, since we use it to index into the
Dataset.

<a id="next-steps">
## Next Steps

The `get_identifiers` function is an easy way to quickly extract (in bulk) multiple
identifiers for inspection, across a lot of files. You might be writing or developing
a recipe, and need easy access to all these fields. What should you do next?
At this point, you have a few options:

<a id="recipe-interaction">
### Recipe Interaction

If you want to write a recipe to perform a bunch of custom actions on your
dicom files, you should read about how to [work with recipes]({{ site.basurl }}/examples/recipe/).

<a id="clean-pixels">
### Clean Pixels

It's likely that the pixels in the images have burned in annotations, and we can
use the header data to flag these images. Thus, before you replace identifiers,
you probably want to do this. We have a DicomCleaner class that can flag images
for PHI based on matching some header filter criteria, and you can
[read about that here]({{site.baseurl}}/getting-started/dicom-pixels/).

<a id="update-identifiers">
### Update Identifiers

Once you are finished with any customization of the recipe, updating identifiers,
 and/or potentially flagging and quarantining images that have PHI, you should be
ready to [replace (PUT)]({{ site.baseurl}}/getting-started/dicom-put/) with new
 fields based on the deid recipe.
