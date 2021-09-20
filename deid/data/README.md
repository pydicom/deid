This folder contains specifications for how to flag a dicom image for a possible burned in annotation. The specification file is called [deid.dicom](deid.dicom) and this README will contain a history of it's updates and changes.

## Deid.dicom Updates
 -'7/2/2017': created with [current CTP](https://github.com/johnperry/CTP/blob/8a3c595b60442e6d74aec4098eaed5dcf8ff8770/source/files/examples/example-dicom-pixel-anonymizer.script) criteria, which are also present on the Stanford run CTP.


## Datasets

deid uses the subfolders here, dicom-cookies and animals, as datasets that can be loaded
as follows:

```python
from deid.data import get_dataset
dataset = get_dataset('dicom-cookies')
dataset = get_dataset('animals')
```

And then you might write a function to load a dicom file:


```python
def get_dicom(dataset):
    """helper function to load a dicom
    """
    from deid.dicom import get_files
    from pydicom import read_file

    dicom_files = get_files(dataset)
    return read_file(next(dicom_files))

dicom = get_dicom(dataset)
```
