# Loading Data

Typically, you have two common scenarios when loading a dataset:

## File Organization

### DICOMDIR

A dicom directory is how some providers store datasets, and one might look like this:

```
tree deid/data/example-patient/
deid/data/example-patient/
├── IMAGES
│   └── REF
│       ├── CT1_UNC
│       ├── CT2_UNC
│       ├── MG1_UNC
│       ├── MR1_UNC
│       ├── MR2_UNC
│       ├── MR3_UNC
│       ├── MR4_UNC
│       ├── NM1_UNC
│       ├── RG1_UNC
│       ├── RG2_UNC
│       ├── RG3_UNC
│       ├── SC1_UNC
│       ├── US1_UNC
│       ├── VL1_UNC
│       ├── VL2_UNC
│       ├── VL3_UNC
│       ├── VL4_UNC
│       ├── VL5_UNC
│       ├── VL6_UNC
│       └── XA1_UNC
└── DICOMDIR

```

### Flat

if you retrieved your data using a tool like [dcmqr](https://dcm4che.atlassian.net/wiki/display/d2/dcmqr) with a `C-MOVE`, then you might have a flat directory structure. Sometimes the files won't have an extension:

```
tree deid/data/example-flat/
deid/data/example-flat/
├── CT1_UNC
├── CT2_UNC
├── MG1_UNC
├── MR1_UNC
├── MR2_UNC
├── MR3_UNC
├── MR4_UNC
├── NM1_UNC
├── RG1_UNC
├── RG2_UNC
├── RG3_UNC
├── SC1_UNC
├── US1_UNC
├── VL1_UNC
├── VL2_UNC
├── VL3_UNC
├── VL4_UNC
├── VL5_UNC
├── VL6_UNC
└── XA1_UNC
```

and sometimes they will:

```
tree deid/data/cookie-series/
deid/data/cookie-series/
├── image1.dcm
├── image2.dcm
├── image3.dcm
├── image4.dcm
├── image5.dcm
├── image6.dcm
└── image7.dcm
```

It doesn't actually matter so much how your data is structured, you can use any method that you like to. You could technically just use `os.listdir` or `glob`:


```
from glob import glob
import os

base = "deid/data/cookie-series"

dicom_files = glob("%s/*" %base)
['deid/data/cookie-series/image4.dcm',
 'deid/data/cookie-series/image2.dcm',
 'deid/data/cookie-series/image7.dcm',
 'deid/data/cookie-series/image6.dcm',
 'deid/data/cookie-series/image3.dcm',
 'deid/data/cookie-series/image1.dcm',
 'deid/data/cookie-series/image5.dcm']

os.listdir(base)
['image4.dcm',
 'image2.dcm',
 'image7.dcm',
 'image6.dcm',
 'image3.dcm',
 'image1.dcm',
 'image5.dcm']
```

Notice anything that might trigger a bug with the above? You probably should ask for an absolute path.

```
# For glob
dicom_files = glob("%s/*" %base)
dicom_files = [os.path.abspath(x) for x in dicom_files]

# For os module
dicom_files = []
for root, folders, files in os.walk(base):
    for file in files:
        fullpath = os.path.abspath(os.path.join(root,file))
        dicom_files.append(fullpath)
```

We provide a more robust function, because it's usually the case that you want to match a pattern of file, have subfolders, or want a validation done to be sure that each file is dicom.


## Find Datasets
The function that we have provided will find all datasets matching some pattern (or all files recursively in a folder). You simply need to provide a list of top folders, a list of files and folders, or just files to start. For the purposes of this walkthrough, we will load data folders that are provided with the application.

```
from deid.data import get_dataset

base = get_dataset("dicom-cookies")
base
'/home/vanessa/anaconda3/lib/python3.5/site-packages/som-0.1.1-py3.5.egg/som/data/dicom-cookies'
```

In the above, all we've done it retrieved the full path for a folder of dicom files. Let's try to read in the data:


```
from deid.dicom import get_files

dicom_files = get_files(base)
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
```

We can also specify to not do the check, if we are absolutely sure. For larger datasets this might speed up processing a little bit.

```
dicom_files = get_files(base,check=False)
DEBUG Found 7 contender files in dicom-cookies
```

We can also give it a particular pattern to match. Since these files all end with `.dcm`, that's not so useful. Let's give a pattern to just match `image1.dcm`:


```
dicom_files = get_files(base,pattern="image1*")
DEBUG Found 1 contender files in dicom-cookies
DEBUG Checking 1 dicom files for validation.
Found 1 valid dicom files
```

At this point, you should have a list of dicom files. You might now want to [configure](config.md) your deidentifation.
