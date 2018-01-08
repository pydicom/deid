# Get Identifiers (GET)

A get request using the deid module will return the headers found in a particular dataset. Let's walk through these steps. As we did in the [loading](loading.md), the first step was to load a dicom dataset:

```
from deid.data import get_dataset
from deid.dicom import get_files

base = get_dataset("dicom-cookies")
dicom_files = list(get_files(base))
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
```

We now have our small dataset that we want to de-identify! The first step is to get the identifiers. By default, we will return all of them. That call will look like this:

```
from deid.dicom import get_identifiers
ids = get_identifiers(dicom_files)
```

By default, any Sequences (lists of items) within the files are expanded and provided. This means that a Sequence with header value `AdditionalData` and item `Modality` will be returned as `AdditionalData_Modality`. If you want to disable this and not return expanded sequences:

```
ids = get_identifiers(dicom_files=dicom_files,
                      expand_sequences=False)
```

We will see debug output for each, indicating that we found a particular number of fields:

```
$ ids=get_identifiers(dicom_files)
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG Found 27 defined fields for image4.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Found 27 defined fields for image2.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Found 27 defined fields for image7.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Found 27 defined fields for image6.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Found 27 defined fields for image3.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Found 27 defined fields for image1.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Found 27 defined fields for image5.dcm
```

Since a data structure is returned indexed by an entity id and then item (eg, patient --> image). under the hood this means that we use fields from the header to use as the index for entity id and item id. Id you don't change the defaults, the entity_id is `PatientID` and item id is `SOPInstanceUID`. To change this, just specify in the function:

```

ids = get_identifiers(dicom_files,
                      entity_id="PatientFullName",
                      item_id="InstanceUID")
```


## Organization
Let's take a closer look at how this is organized. If you notice, the above seems to be able to identify entity and items. This is because in the default, the configuration has set an entity id to be the `PatientID` and the item the `SOPInstanceUID`. This is how it is organized in the returned result - the entity is the first lookup key:

```
# We found one entity
len(ids)
1

# The entity id is cookie-47
ids.keys()
dict_keys(['cookie-47'])
```

and then below that, the data is indexed by the item id:

```
list(ids['cookie-47'].keys())
['1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947',
 '1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989',
 '1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351',
 '1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131',
 '1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268',
 '1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276',
 '1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866']
```
**note** that I only made it a list for prettier printing. 


### Why this organization?
We have this organization because by default, the software doesn't know what headers it will find in the dicom files, and it also doesn't know the number of (possibly) different entities (eg, a patient) or images (eg, an instance) it will find. For this reason, by default, for dicom we have specified that the entity id is the `PatientID` and the `itemID` is the `SOPInstanceUID`. 


### Header Fields
Then if we look at the data under a particular item id, we see the dicom fields (and corresponding values) found in the data.

```
ids['cookie-47']['1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947']
{'BitsAllocated': 8,
 'BitsStored': 8,
 'Columns': 2048,
 'ConversionType': 'WSD',
 'HighBit': 7,
 'ImageComments': 'This is a cookie tumor dataset for testing dicom tools.',
 'InstitutionName': 'STANFORD',
 'LossyImageCompression': '01',
 'LossyImageCompressionMethod': 'ISO_10918_1',
 'NameOfPhysiciansReadingStudy': 'Dr. damp lake',
 'OperatorsName': 'nameless voice',
 'PatientID': 'cookie-47',
 'PatientName': 'still salad',
 'PatientSex': 'F',
 'PhotometricInterpretation': 'YBR_FULL_422',
 'PixelRepresentation': 0,
 'PlanarConfiguration': 0,
 'ReferringPhysicianName': 'Dr. bold moon',
 'Rows': 1536,
 'SOPClassUID': '1.2.840.10008.5.1.4.1.1.7',
 'SOPInstanceUID': '1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947',
 'SamplesPerPixel': 3,
 'SeriesInstanceUID': '1.2.276.0.7230010.3.1.3.8323329.5360.1495927170.640945',
 'SpecificCharacterSet': 'ISO_IR 100',
 'StudyDate': '20131210',
 'StudyInstanceUID': '1.2.276.0.7230010.3.1.2.8323329.5360.1495927170.640946',
 'StudyTime': '191930'}
```

## Save what you need
Pretty neat! At this point, you have two options:

### Clean Pixels
It's likely that the pixels in the images have burned in annotations, and we can use the header data to flag these images. Thus, before you replace identifiers, you probably want to do this. We currently don't have this implemented in production quality, but you can see progress in the [pixels](pixels.md) documentation.


### Update Identifiers
It's likely that you now want to query your special de-identification API to do some replacement of the PatientID with something else, or custom parsing of the data. You can read our [update](update.md) docs for instructions on how to do this replacement.
