# Get Identifiers (GET)

A get request using the deid module will return the headers found in a particular dataset. Let's walk through these steps. As we did in the [loading](loading.md), the first step was to load a dicom dataset:

```
from deid.data import get_dataset
from deid.dicom import get_files

base = get_dataset("dicom-cookies")
dicom_files = get_files(base)
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
```

We now have our small dataset that we want to de-identify! The first step is to get the identifiers. By default, we will return all of them. That call will look like this:

```
from deid.dicom import get_identifiers
ids = get_identifiers(dicom_files)
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

## Organization
How is the result organized? If you notice, the above seems to be able to identify entity and items. This is because in the default, the configuration has set an entity id to be the `PatientID` and the item the `SOPInstanceUID`. This is how it is organized in the returned result - the entity is the first lookup key:

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
Pretty neat! At this point, you would want to use whatever methods that you have to save/store your data, and then call the function to `replace_identifiers`, which is considered a [put](put.md) operation. Remember that if you use the defaults, it won't matter what you specify above (and you won't need to provide anything) because all fields will be blanked. However, if you want to replace the variable `SOPClassUID` and you have specified this in your `deid` configuration file, you would want to replace that here:

ids['cookie-47']['1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947']['SOPInstanceUID'] = 'HalloMoto'

More instruction will be provided on how to do this in the [put](put.md) docs.



## Customization
Let's say that you want to use a different entity or item id to index the data. How would you do that? Like this:

```
entity_id = 'OtherPatientNames'
item_id = 'SOPInstanceUID'

ids = get_identifiers(dicom_files=dicom_files,
                      entity_id=entity_id,
                      item_id=item_id)
```

Or if you are a developer, you can change the defaults by making your own version of a [config.json](../deid/dicom/config.json).


and then specify it like this:

```
myconfig = '/path/to/myconfig.json'
ids = get_identifiers(dicom_files,config=myconfig)
```

We recommend the first for most users that don't want to be writing json files.
