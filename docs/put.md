# Put Identifiers Back
At this point, we want to perform a `put` action, which is generally associated with the `replace_identifiers` function. As a reminder, we are working with a data structure returned from `get_identifiers` in [header.py](../deid/dicom/header.py) in the dicom module, and it is indexed first by entity id (`PatientID`) and then item ID (`SOPInstanceUID`). A single entry looks like this:

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

At this point, let's walk through a few basic use cases.


## Default: Blank Everything
In this first use case, we extracted identifiers to save to our database, and we want to blank everything in the data. To do this, we can use the dicom module defaults, and we don't need to give the function anything. Our call would look like this:

```
from deid.dicom import replace_identifiers

cleaned_files = replace_identifiers(dicom_files=dicom_files)
```

Again, remember that you could set a custom `entity_id` or `item_id` if the defaults of `PatientID` and `SOPInstanceUID` aren't appropriate. By default, if you don't specify an `output_folder`, a temporary directory will be made. If you specify `overwrite=True`, the output folder will be the same where the images are, and the files will be over-written. Take caution with this approach.


## Customize Replacement
As we mentioned earlier, if you have a [deid settings](config.md) file, you can specify how you want the replacement to work, and in this case, you would want to provide the result `ids` variable from the [previous step](get.md)

For this example, we will use an example file provided with this package. Likely this will be put into a function with easier use, but this will work for now.

```
from deid.utils import get_installdir
from deid.config import load_deid
import os

deid = os.path.abspath("%s/../examples/deid/" %get_installdir())
```

The above `deid` is just a path to a folder that we have a `deid` file in. The function will find it for us. This function will happen internally, but here is an example of what your loaded `deid` file might look like.

```
load_deid(path)
DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved Yes
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
Out[76]: 
{
 'format': 'dicom',
 'header': [
             {'action': 'ADD','field': 'PatientIdentityRemoved','value': 'Yes'},
             {'action': 'REPLACE', 'field': 'PatientID', 'value': 'var:id'},
             {'action': 'REPLACE', 'field': 'SOPInstanceUID', 'value': 'var:source_id'}
           ]
}
```

Notice that under `header` we have a list of actions, each with a `field` to be applied to, an `action` type (eg, `REPLACE`), and when relevant (for `REPLACE` and `ADD`) we also have a value. If you remember what the `deid` file looked like:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

The above is a "coded" version of that, which has also been validated and checked. In the instruction, written in two forms:

```
{'action': 'REPLACE', 'field': 'SOPInstanceUID', 'value': 'var:source_id'}
REPLACE SOPInstanceUID var:source_id
```

we are saying that we want to replace the field `SOPInstanceUID` not with a value, but with a **variable** (`var`) that is called `source_id`. The full expression then for value, the third in the row, is `var:source_id`. What this means is that when we receive our ids data structure back from get_identifiers, we would need to do whatever lookup is necessary to get that item, and then set it for the appropriate item. Eg, for the entity/item showed above, we would do:

```
ids['cookie-47']['1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947']['source_id'] = 'suid123'
```

and then `suid123` will be used to replace `SOPInstanceUID` in the data. If we wanted it to be a string value, we would leave out the `var`. For example, to replace **all** entity/item `Modality` with the same string, you could do:

```
REPLACE Modality CT-SPECIAL
```

If you specify a replacement variable and it's not found in the data, a warning will be issued. If you specify a `REPLACE` command and the value isn't in the data, it will be added instead.

Stopping here... zzz
