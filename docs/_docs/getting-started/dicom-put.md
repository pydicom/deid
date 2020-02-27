---
title: 5. Put Identifiers Back
category: Getting Started
order: 7
---


At this point, we want to perform a `put` action, which is generally associated with 
the `replace_identifiers` function. As a reminder, we are working with a data 
structure returned from `get_identifiers` in the dicom module, and it is 
indexed first by entity id (`PatientID`) and then item ID 
(`SOPInstanceUID`). A single entry looks like this:

```python
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

At this point, let's walk through a few basic use cases. We again first need to load our dicom files:

```python
from deid.dicom import get_files
from deid.data import get_dataset
base = get_dataset('dicom-cookies')
dicom_files = list(get_files(base))
```


## Default: Remove Everything
In this first use case, we extracted identifiers to save to our database, 
and we want to remove everything in the data. To do this, we can use the 
dicom module defaults, and we don't need to give the function anything. Our 
call would look like this:

```python
from deid.dicom import replace_identifiers

cleaned_files = replace_identifiers(dicom_files=dicom_files)

DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
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
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
```

wherever you dump your new dicoms, it's up to you to decide how to then move 
and store them, and (likely) deal with the original data with identifiers.

## Private Tags
An important note is that by default, this function will also remove private tags
 (`remove_private=True`). If you need private tags to determine if there is 
burned pixel data, you would want to set this to False, perform pixel 
identification, and then remove the private tags yourself:


```python
# Clean the files, but set remove_private to False
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    remove_private=False)

DEBUG Default action is BLANK
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
WARNING Private tags were not removed!
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
WARNING Private tags were not removed!
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
WARNING Private tags were not removed!
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
WARNING Private tags were not removed!
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
WARNING Private tags were not removed!
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
WARNING Private tags were not removed!
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
WARNING Private tags were not removed!
```

Notice how the warning appeared, because we didn't remove private tags? 
Next you would want to do your pixel cleaning, likely using those private
tags that are still in the data. Then you would go back and remove them.

```python
from deid.dicom import remove_private_identifiers

really_cleaned = remove_private_identifiers(dicom_files=cleaned_files)
DEBUG Removed private identifiers for /tmp/tmp2kayz83n/image4.dcm
DEBUG Removed private identifiers for /tmp/tmp5iadxfb9/image2.dcm
DEBUG Removed private identifiers for /tmp/tmpk0yii_ya/image7.dcm
DEBUG Removed private identifiers for /tmp/tmpnxqirboq/image6.dcm
DEBUG Removed private identifiers for /tmp/tmpp9_tj7zq/image3.dcm
DEBUG Removed private identifiers for /tmp/tmpo_kwxmlj/image1.dcm
DEBUG Removed private identifiers for /tmp/tmpf6whw73y/image5.dcm

```

You could also do pixel scraping first, and then call the function
(per default) to remove private. These are the first calls that we did, 
not specifying the variable `remove_private`, and by default it was True. 

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

### Screening Private Tags
Sometimes it is necessary to deidentify the contents of private tags.  While there are no standards regarding the contents of private tags, screening functionality enables the caller to define rules to apply when scanning the values within private tags. 

To screen private tags, the `replace_identifiers` method should be instructed to retain private tags, but screen the tags using the specified screening rules.

```python
screen_rules = []
ScreenValue = collections.namedtuple('ScreenValue', 'type tag split separator minvaluelen pattern')
screen_rules.append(ScreenValue(type='value', tag='PatientName', 
     split=True, separator='^', minvaluelen=4, pattern=None))
screen_rules.append(ScreenValue(type='pattern', tag=None, 
     split=False, separator=None, minvaluelen=None, pattern=r'^(Q\d+)'))
     
# Clean the files, set remove_private to False, and screen the private tags for PHI.
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    remove_private=False,
                                    screen_private=True,
                                    screen_values=screen_rules)
```

#### Configuring Screening Rules
Screening rules are defined by a namedtuple describing the rule to be applied when evaluating the values of the private tag.  

`value` type screening rules instruct the screening to use the value in the specified tag as a value to find within private tags and remove.  The `split` property instructs the parser to split the value retrieved by the tag by the specified character and use the returned values as the screening value.  `minvaluelength` sets the minimum required length of each returned split component for the split value to be scanned.

```python
screen_rules = []
ScreenValue = collections.namedtuple('ScreenValue', 'type tag split separator minvaluelen pattern')

# Instructs the parser to grab the value from the PatientName tag, split it by '^', 
# and scan for and remove tags containing the value if the value is 4 or more characters in length.
screen_rules.append(ScreenValue(type='value', tag='PatientName', 
      split=True, separator='^', minvaluelen=4, pattern=None))
# Example: PatientName = Simpson^Homer^Jay^^^
# Resulting Scanned Values: [Simpson|Homer]
#     Jay is not included as it is less than the specified minvaluelen, 4.
```

`pattern` type screening rules instruct the screening functionality to use the specified regex pattern to determine when private tags should be removed. The actual regex pattern to utilized is specified within the `pattern` property.

```python
# Instructs the parser to remove private tags containing values that begin 
# with a Q followed by numbers. 
screen_rules.append(ScreenValue(type='pattern', tag=None, 
     split=False, separator=None, minvaluelen=None, pattern=r'^(Q\d+)'))
     
# Instructs the parser to remove private tags with values containing ^ characters.
screen_rules.append(ScreenValue(type='pattern', tag=None, 
     split=False, separator=None, minvaluelen=None, pattern=r'.*\^+.*'))
```

## Customize Replacement
As we mentioned earlier, if you have a [deid settings]({{ site.baseurl}}/getting-started/dicom-config/) file, 
you can specify how you want the replacement to work, and in this case, 
you would want to provide the result `ids` variable from the [previous step]({{ site.baseurl}}/getting-started/dicom-get/)

### Create your deid specification
For this example, we will use an example file provided with this package. 
Likely this will be put into a function with easier use, but this will work for now.

```python
from deid.utils import get_installdir
from deid.config import load_deid
import os

path = os.path.abspath("%s/../examples/deid/" %get_installdir())
```

The above `deid` is just a path to a folder that we have a `deid` file in. 
The function will find it for us. This function will happen internally, 
but here is an example of what your loaded `deid` file might look like.

```
deid = load_deid(path)
DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved Yes
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
deid

{
 'format': 'dicom',
 'header': [
             {'action': 'ADD','field': 'PatientIdentityRemoved','value': 'Yes'},
             {'action': 'REPLACE', 'field': 'PatientID', 'value': 'var:id'},
             {'action': 'REPLACE', 'field': 'SOPInstanceUID', 'value': 'var:source_id'}
           ]
}
```

Notice that under `header` we have a list of actions, each with a `field` 
to be applied to, an `action` type (eg, `REPLACE`), and when relevant 
(for `REPLACE` and `ADD`) we also have a value. If you remember what 
the `deid` file looked like:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

The above is a "coded" version of that, which has also been validated and checked. In the instruction, written in two forms:

```python
        {'action': 'REPLACE', 'field': 'SOPInstanceUID', 'value': 'var:source_id'}
    
        REPLACE SOPInstanceUID var:source_id
```

we are saying that we want to replace the field `SOPInstanceUID` not with a value, 
but with a **variable** (`var`) that is called `source_id`. The full expression 
then for value, the third in the row, is `var:source_id`. What this means 
is that when we receive our ids data structure back from get_identifiers, 
we would need to do whatever lookup is necessary to get that item, and then 
set it for the appropriate item. Eg, for the entity/item showed above, we would do:

```python
ids['cookie-47']['1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947']['source_id'] = 'suid123'
```

### Add your variables
Let's walk through that complete example, first getting our identifiers,
 adding some random source_id and id, and then running the function.

```python
from deid.dicom import get_identifiers
ids = get_identifiers(dicom_files)
```

Let's say that we want to change the `PatientID` `cookie-47` to `cookiemonster`, 
and for each identifier, we will give it a numerically increasing `SOPInstanceUID`.

```python
count=0
for entity, items in ids.items():
    for item in items:
        ids[entity][item]['id'] = "cookiemonster"
        ids[entity][item]['source_id'] = "cookiemonster-image-%s" %(count)
        count+=1
```

An important note - both fields are added on the level of the item, and not at the 
level of the entity! This is because, although we have an entity and item both 
represented, they are both represented in a flat hierarchy (on the level of the 
item) so the final data structure, for each item, should look like this:

```python
entity = 'cookie-47'
item = '1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351'

ids[entity][item]

{'BitsAllocated': 8,
 'BitsStored': 8,h
 'Columns': 2048,
 'ConversionType': 'WSD',
 'HighBit': 7,
 'ImageComments': 'This is a cookie tumor dataset for testing dicom tools.',
 'InstitutionName': 'STANFORD',
 'LossyImageCompression': '01',
 'LossyImageCompressionMethod': 'ISO_10918_1',
 'NameOfPhysiciansReadingStudy': 'Dr. lively wind',
 'OperatorsName': 'curly darkness',
 'PatientID': 'cookie-47',
 'PatientName': 'falling disk',
 'PatientSex': 'M',
 'PhotometricInterpretation': 'YBR_FULL_422',
 'PixelRepresentation': 0,
 'PlanarConfiguration': 0,
 'ReferringPhysicianName': 'Dr. solitary heart',
 'Rows': 1536,
 'SOPClassUID': '1.2.840.10008.5.1.4.1.1.7',
 'SOPInstanceUID': '1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351',
 'SamplesPerPixel': 3,
 'SeriesInstanceUID': '1.2.276.0.7230010.3.1.3.8323329.5329.1495927169.580349',
 'SpecificCharacterSet': 'ISO_IR 100',
 'StudyDate': '20131210',
 'StudyInstanceUID': '1.2.276.0.7230010.3.1.2.8323329.5329.1495927169.580350',
 'StudyTime': '191929',
 'id': 'cookiemonster',
 'id_source': 'cookiemonster-image-6'}
```

Now we are going to run our function again, but this time providing:
 1. The path to our deid specification
 2. the ids data structure we updated above


### Replace identifiers
It's time to clean our data with the deid specification and ids datastructure we have prepared.

```python
# path is '/home/vanessa/Documents/Dropbox/Code/som/dicom/deid/examples/deid'
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=path,
                                    ids=ids)

DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved Yes
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG Attempting ADDITION of PatientIdentityRemoved to image4.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Attempting ADDITION of PatientIdentityRemoved to image2.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Attempting ADDITION of PatientIdentityRemoved to image7.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Attempting ADDITION of PatientIdentityRemoved to image6.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Attempting ADDITION of PatientIdentityRemoved to image3.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Attempting ADDITION of PatientIdentityRemoved to image1.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Attempting ADDITION of PatientIdentityRemoved to image5.dcm.
```

We can now read in one of the output files to see the result:

```python
# We can load in a cleaned file to see what was done
from pydicom import read_file
test_file = read_file(cleaned_files[0])

test_file
(0008, 0018) SOP Instance UID                    UI: cookiemonster-image-4
(0010, 0020) Patient ID                          LO: 'cookiemonster'
(0012, 0062) Patient Identity Removed            CS: 'Yes'
(0028, 0002) Samples per Pixel                   US: 3
(0028, 0010) Rows                                US: 1536
(0028, 0011) Columns                             US: 2048
(7fe0, 0010) Pixel Data                          OB: Array of 738444 bytes
```

And it looks like we are good!

In this example, we did the more complicated thing of setting the value to be a variable from the ids data structure (specified with `var:id`. We can take an even simpler approach. If we wanted it to be a string value, meaning the same for all items, we would leave out the `var`:


```
REPLACE Modality CT-SPECIAL
```

This example would replace the Modality for all items to be the string `CT-SPECIAL`.

#### Define entity or items
For this function, if you have set a custom `entity_id` or `item_id` 
(that you used for the first call) you would also want to specify it here. 
Again, the the defaults are `PatientID` for the entity, and `SOPInstanceUID` for each item. 


```python
replace_identifiers(dicom_files,
                    ids=ids,
                    entity_id="PatientID",
                    item_id="SOPInstanceUID")
```

For more refinement of the default config, see the [development]({{ site.baseurl}}/development/) docs.

## Errors During Replacement
Let's try to break the above. We are going to extract ids, but then define the 
`source_id` at the wrong variable. What happens?

```python
from deid.dicom import get_identifiers
ids = get_identifiers(dicom_files)
```

Let's be stupid, oops, instead of `source_id` I wrote `source_uid`

```python
count=0
for entity, items in ids.items():
    for item in items:
        ids[entity][item]['id'] = "cookiemonster"
        ids[entity][item]['source_uid'] = "cookiemonster-image-%s" %(count)
        count+=1
```

Try the replacement...

```python
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=path,
                                    ids=ids)
DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved Yes
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG Attempting ADDITION of PatientIdentityRemoved to image4.dcm.
WARNING REPLACE SOPInstanceUID not done for image4.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Attempting ADDITION of PatientIdentityRemoved to image2.dcm.
WARNING REPLACE SOPInstanceUID not done for image2.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Attempting ADDITION of PatientIdentityRemoved to image7.dcm.
WARNING REPLACE SOPInstanceUID not done for image7.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Attempting ADDITION of PatientIdentityRemoved to image6.dcm.
WARNING REPLACE SOPInstanceUID not done for image6.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Attempting ADDITION of PatientIdentityRemoved to image3.dcm.
WARNING REPLACE SOPInstanceUID not done for image3.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Attempting ADDITION of PatientIdentityRemoved to image1.dcm.
WARNING REPLACE SOPInstanceUID not done for image1.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Attempting ADDITION of PatientIdentityRemoved to image5.dcm.
WARNING REPLACE SOPInstanceUID not done for image5.dcm
```

You see that we get a warning. As a precaution, since the action wasn't taken, the field is removed from the data.

```python
from pydicom import read_file
test_file = read_file(cleaned_files[0])

test_file
(0010, 0020) Patient ID                          LO: 'cookiemonster'
(0012, 0062) Patient Identity Removed            CS: 'Yes'
(0028, 0002) Samples per Pixel                   US: 3
(0028, 0010) Rows                                US: 1536
(0028, 0011) Columns                             US: 2048
(7fe0, 0010) Pixel Data                          OB: Array of 738444 bytes
```


```python
replace_identifiers(dicom_files,
                    ids=ids,
                    entity_id="PatientID",
                    item_id="SOPInstanceUID")
```


```
REPLACE Modality CT-SPECIAL
```

## Developer Replacement
If you are a developer, you can create your own config.json and give it to the function above. 
You can read more about this in the [developers]({{ site.baseurl}}/development/) notes.
