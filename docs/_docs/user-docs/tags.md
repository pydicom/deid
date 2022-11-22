---
title: Tags
category: User Documentation
order: 7
---

It is sometimes helpful to be able to find a particular tag. [Pydicom](https://www.github.com/pydicom/pydicom)
has done a great job of providing a dictionary of tags:

```python
from pydicom._dicom_dict import DicomDictionary
```

<a id="search-by-name">
## Search By Name
and we extend that here to make it easy to find tags. For example,
we can use a function to search based on name:

```python
from deid.dicom.tags import find_tag
find_tag('Modality')

[('CS', '1', 'Modality', '', 'Modality'),
 ('SQ', '1', 'Modality LUT Sequence', '', 'ModalityLUTSequence'),
 ('LO', '1', 'Modality LUT Type', '', 'ModalityLUTType'),
 ('CS', '1', 'Equipment Modality', '', 'EquipmentModality')]
```

We can also limit to a particular VR, or VM:

```python
find_tag('Modality', VR='CS')
[('CS', '1', 'Modality', '', 'Modality'),
 ('CS', '1', 'Equipment Modality', '', 'EquipmentModality')]
```

<a id="search-repeaters">
## Search Repeaters (Retired)
If you want to search the set of Repeats (or tags I think pydicom doesn't use / calls retired).
Then set `retired=True`. For example, when I search for `Overlay Description` the normal
way I get nothing, but setting this flag returns the (old) value. This would be useful
given that you need to look up a tag for an older dataset.

```python
find_tag('Overlay Description')

find_tag('Overlay Description',retired=True)
[('LO', '1', 'Overlay Description', '', 'OverlayDescription')]
```
