# Tags

It is sometimes helpful to be able to find a particular tag. [Pydicom](https://www.github.com/pydicom/pydicom) has done a great job of providing a dictionary of tags:

```
from pydicom._dicom_dict import DicomDictionary
```

## Search By Name
and we extend that here to make it easy to find tags. For example, we can use a function to search based on name:

```
from deid.dicom.tags import find_tag
find_tag('Modality')

[('CS', '1', 'Modality', '', 'Modality'),
 ('SQ', '1', 'Modality LUT Sequence', '', 'ModalityLUTSequence'),
 ('LO', '1', 'Modality LUT Type', '', 'ModalityLUTType'),
 ('CS', '1', 'Equipment Modality', '', 'EquipmentModality')]
```

We can also limit to a particular VR, or VM:

```
find_tag('Modality', VR='CS')
[('CS', '1', 'Modality', '', 'Modality'),
 ('CS', '1', 'Equipment Modality', '', 'EquipmentModality')]
```
