---
title: Deid Client
category: Examples
order: 3
---

Here is a quick example of using the deid executable. For more information on this
client, see the [user docs]({{ site.baseurl }}/user-docs/client/) page.

<a id="data">
## Data

To run these examples, you'll need to install external deid-data.

```bash
$ pip install deid-data
```

<a id="deid-executable">
### Deid Executable
The deid executable is installed automatically with the module. Just running `deid` we see:

```
usage: deid [-h] [--version] [--quiet] [--debug] [--outfolder OUTFOLDER]
            [--format {dicom}] [--overwrite] [--deid DEID]
            {inspect,identifiers} ...

Deid (de-identification, anonymization) command line tool.

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show deid software version
  --quiet, -q           Quiet the verbose output
  --debug               use verbose logging to debug.
  --outfolder OUTFOLDER, -o OUTFOLDER
                        full path to save output, will use temporary folder if
                        not specified
  --format {dicom}, -f {dicom}
                        format of images, default is dicom
  --overwrite           overwrite pre-existing files in output directory, if
                        they exist.

actions:
  actions for deid to perform

  {inspect,identifiers}
                        action for deid to perform
    inspect             various checks for PHI and quality
    identifiers         extract and replace identifiers from headers
```

What we want to do is inspect:

```
usage: deid inspect [-h] [--deid DEID] [--save] folder [folder ...]

positional arguments:
  folder       input folder or single image. If not provided, test data will
               be used.

optional arguments:
  -h, --help   show this help message and exit
  --deid DEID  deid file with preferences, if not specified, default used.
  --save, -s   save result to output tab separated file.
```

Let's run the command with test data (dicom cookies) and specify the deid in our examples folder:

```
deid inspect --deid examples/deid deid/data/dicom-cookies

Found 7 valid dicom files
FLAGGED image6.dcm in section dangerouscookie
LABEL: LABEL Criteria for Dangerous Cookie
CRITERIA:  PatientSex contains M and OperatorsName notequals bold bread
FLAGGED image5.dcm in section dangerouscookie
LABEL: LABEL Criteria for Dangerous Cookie
CRITERIA:  PatientSex contains M and OperatorsName notequals bold bread

SUMMARY ================================

CLEAN 5 files
FLAGGED dangerouscookie 2 files
```
You will see an output, and then a summary of file lists for each of clean and flagged.

If you want to run the above and save the result to file:

```
deid inspect --deid examples/deid deid/data/dicom-cookies --save
...
SUMMARY ================================

CLEAN 5 files
FLAGGED dangerouscookie 2 files
Result written to pixel-flag-results-dicom-cookies-17-09-02.tsv
```

and the file looks like this - images with OperatorsName notequals "bold bread" and PatientSex "M" are flagged:

```
dicom_file      pixels_flagged  flag_list       reason
deid/data/dicom-cookies/image4.dcm,CLEAN
deid/data/dicom-cookies/image2.dcm,CLEAN
deid/data/dicom-cookies/image7.dcm,CLEAN
deid/data/dicom-cookies/image3.dcm,CLEAN
deid/data/dicom-cookies/image1.dcm,CLEAN
deid/data/dicom-cookies/image1.dcm,FLAGGED      dangerouscookie  PatientSex contains M and OperatorsName notequals bold bread
deid/data/dicom-cookies/image1.dcm,FLAGGED      dangerouscookie  PatientSex contains M and OperatorsName notequals bold bread
```
<a id="within-python">
### Within Python
First, let's load the example "dicom cookies" dataset. We will first run this example within python, and then using a command line client (not written yet).

```
from deid.data import get_dataset
from deid.dicom import get_files

dicom_files = list(get_files(get_dataset('dicom-cookies')))
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files

['/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image4.dcm',
 '/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image2.dcm',
 '/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image7.dcm',
 '/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image6.dcm',
 '/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image3.dcm',
 '/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image1.dcm',
 '/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image5.dcm']

```

Next, let's use the example deid specification file that is relevant to this dataset. We read it in like this:

```
from deid.config import load_deid

# From the base of the deid repo
deid = load_deid('examples/deid')
DEBUG FORMAT set to dicom
DEBUG Adding section filter dangerouscookie
DEBUG Adding section header
DEBUG Adding ADD PatientIdentityRemoved YES
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
```

and the file we are reading looks like this. It's very intuitive, we have groups of
filters (more specific at the top and moving down to more general) and each is named
("dangerouscookie" and "bigimage"). Within each filter we have one criteria group,
with a "+" indicating and. We could have more groups under each, but happen to not
for this example.

```
FORMAT dicom

%filter dangerouscookie

LABEL Criteria for Dangerous Cookie
contains PatientSex M
  + notequals OperatorsName bold bread
  coordinates 0,0,512,110


%filter bigimage

LABEL Image Size Good for Machine Learning
equals Rows 2048
  + equals Columns 1536
  coordinates 0,0,512,200

%header

ADD PatientIdentityRemoved YES
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

We won't be using the header section for this example, but for your FYI,
this is the recipe for how we would want to replace information in the header,
if we were cleaning the headers. Right now we are just filtering images to
 flag those that might have PHI. Let's very strictly walk through the logic
that will be taken above:

 1. If the header contains field PatientSex "M" (Male), and OperatorsName is not "bold bread," we flag. Otherwise, keep going.
 2. If the header has field Rows 2048 and Columns 1536 we flag.

The flag that is done first (more specific) is the final decision.
This means that you should have your known coordinates of PHI (eg, specific
modality, manufacturer, etc) first, and followed by more general estimates of
PHI. Likely a later group will create flags for more manual inspection.

Now let's run the filter! First just within python:

```python
from deid.dicom import has_burned_pixels
groups = has_burned_pixels(dicom_files=dicom_files, deid='examples/deid')
```

We immediately see that two are flagged:

```bash
FLAGGED image6.dcm in section dangerouscookie
LABEL: LABEL Criteria for Dangerous Cookie
CRITERIA:  PatientSex contains M and OperatorsName notequals bold bread
FLAGGED image5.dcm in section dangerouscookie
LABEL: LABEL Criteria for Dangerous Cookie
CRITERIA:  PatientSex contains M and OperatorsName notequals bold bread
```

Is this accurate?

```python
for dicom_file in dicom_files:
    dicom = read_file(dicom_file)
    print("%s:%s - %s" %(os.path.basename(dicom_file),
                         dicom.OperatorsName,
                         dicom.PatientSex))

image4.dcm:bold bread - M
image2.dcm:lingering hill - F
image7.dcm:sweet brook - F
image6.dcm:green paper - M       <--- FLAGGED
image3.dcm:nameless voice - F
image1.dcm:fragrant pond - F
image5.dcm:curly darkness - M    <--- FLAGGED
```

Seems to be! The data structure returned gives us programmatic access to the groups,
including list of clean (top), list of flagged and flag list name (flagged) and given flagged, a lookup dictionary with reasons:

```python
{
   "clean":[
      "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image4.dcm",
      "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image2.dcm",
      "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image7.dcm",
      "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image3.dcm",
      "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image1.dcm"
   ],
   "flagged":{
      "dangerouscookie":[
         "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image6.dcm",
         "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image5.dcm"
      ]
   },
   "reason":{
      "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image5.dcm":" PatientSex contains M and OperatorsName notequals bold bread",
      "/home/vanessa/Documents/Dropbox/Code/dicom/deid/deid/data/dicom-cookies/image6.dcm":" PatientSex contains M and OperatorsName notequals bold bread"
   }
}
```
