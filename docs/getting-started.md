# Getting Started


## Application Flow
The general flow of the main function to anonymize is the following:

 1. Check each image against a set of filters, with increasing levels of specificity. An image is attributed to the filter group with the highest level of specificity, which is most specific to it. For example, an image that is flagged with a general Blacklist criteria that is subsequently flagged with Greylist (meaning we know how to clean it) is moved to the Greylist.
 2. Proceed to process each group separately

### Groups
The final groups that an image belongs to are considered accordingly:

 - **Greylist** is typically checked first, and an image being flagged for this groups means that contains PHI in a reliable, known configuration. The greylist checks are based on image headers like modality, and manufacturer that we are positive about the locations of pixels that need to be scrubbed. If an image is greylisted, we can confidently clean it, and continue processing. This strategy is similar to the MIRC-CTP protocol.
 - **Whitelist**: images also must pass through sets of criteria that serve as flags that the image is reliable to not contain any PHI.  These images can be passed without intervention (Note from Vanessa, I don't see many circumstances for which this might apply).
 - **Blacklist** images that are not Greylisted or Blacklisted are largely unknowns. They may contain PHI in an unstructured fashion, and we need to be conservative and precaucious. Blacklist images may be passed through a more sophisticated filter (such as a character recognition algorithm), deleted, or passed through and possibly marked (in the DICOM header or on the image) to note the images are blacklisted (with the requesting researcher defining the best method).


### Filters
Filters are included with the `deid.dicom` specification, provided by default with the application, and also customizable by you. The start of a filter might look like this:

```
FORMAT dicom

%filter graylist

LABEL CT Dose Series
  contains Modality CT
  + contains Manufacturer GE
  + contains CodeMeaning IEC Body Dosimetry Phantom
  coordinates 0,0,512,200

LABEL Dose Report
  contains Modality CT
  + contains Manufacturer GE
  + contains SeriesDescription Dose Report
  coordinates 0,0,512,110

%filter blacklist

LABEL Burned In Annotation
contains ImageType SAVE
contains SeriesDescription SAVE
contains BurnedInAnnotation YES
empty ImageType
empty DateOfSecondaryCapture
empty SecondaryCaptureDeviceManufacturer
empty SecondaryCaptureDeviceManufacturerModelName
empty SecondaryCaptureDeviceSoftwareVersions
```

Each section is indicated by `%filter`, and within sections, a set of criteria are defined under a `LABEL`. 

##### How are images filtered?
You can imagine an image starting at the top of the file, and moving down line by line. If at any point it doesn't pass criteria, it is flagged and placed with the group, and no further checking is done.  For this purpose, the sections are ordered by their specificity and preference. This means that, for the above, by placing blacklist after graylist we are saying that an image that could be flagged to be both in the blacklist and graylist will hit the graylist first. This is logical because the graylist corresponds to a specific set of image header criteria for which we know how to clean. We only resort to general blacklist criteria if we make it far enough and haven't been convinced that there isn't PHI.


##### How do I read a criteria?
Each filter section criteria starts with `LABEL`. this is an identifier to report to the user given that the flag goes off. Each criteria then has the following format:

```
<criteria> <field> <value>
```
where "value" is optional, depending on the filter. For example:

```
LABEL Burned In Annotation
contains ImageType SAVE
```

Reads "flag the image with a Burned In Annotation, which belongs to the blacklist filter, if the ImageType fields contains SAVE." If you want to do an "and" statement across two fields, just use `+`:

```
contains ImageType SAVE
  + contains Manufacturer GE
```

>> "flag the image if the ImageType contains SAVE AND Manufacturer contains GE. To do an "or"

```
contains ImageType SAVE
  || contains Manufacturer GE
```

>> "flag the image if the ImageType contains SAVE OR Manufacturer contains GE.

And you can have multiple criteria for one `LABEL`

```
contains SeriesDescription SAVE
+ contains BurnedInAnnotation YES
empty ImageType
|| empty DateOfSecondaryCapture
```

 - First check: "flag the image if SeriesDescription contains SAVE AND BurnedInAnnotation has YES"
 - Second check: "flag the image if ImageType is empty or DateOfSecondaryCapture is empty."

And to make it even simpler, if you want to check one field for a value a OR b, you can use regular expressions. The following checks ImageType for "CT" OR "MRI"

```
equals ImageType CT|MRI
```

which is equivalent to:

```
equals ImageTyoe CT
|| equals ImageType MRI
```

##### What are the criteria options?
For all of the below, case does not matter. All fields are changed to lowercase before comparison, and stripped of leading and trailing white spaces.

 - **contains** is using a regular expression search, meaning that the word can appear anywhere in the field (eg, a `contains` "save" would flag a value of "saved".
 - **equals** means you want to match an expression exactly. `equals` with "save" would not flag a value of "saved".
 - **empty** means that the header is present in the data, but it's an empty string (eg, ""). 
 - **missing** means that the header is not present in the data.
 - **notEquals** is the inverse of equals
 - **notContains** is the inverse of contains

##### How do I customize the process?
There are several things you can customize! 

- You first don't have to use the application default files. You can make a copy, customize to your liking, and provide the path to the file as an argument. If you have criteria to contribute, we encourage you to do so.
- The name of the filter itself doesn't matter, you are free to use different terms than whitelist, blacklist, etc.


## An example
First, let's load the example "dicom cookies" dataset. We will first run this example within python, and then using a command line client.

```
from deid.data import get_dataset
from deid.dicom import get_files

dicom_files = get_files(get_dataset('dicom-cookies'))
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
DEBUG Adding ADD PatientIdentityRemoved Yes
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
```

and the file we are reading looks like this. It's very intuitive, we have groups of filters (more specific at the top and moving down to more general) and each is named ("dangerouscookie" and "bigimage"). Within each filter we have one criteria group, with a "+" indicating and. We could have more groups under each, but happen to not for this example.

```
FORMAT dicom

%filter dangerouscookie

LABEL Criteria for Dangerous Cookie
contains PatientSex M
  + missing PatientBirthDate
  + notequals OperatorsName bold bread
  coordinates 0,0,512,110


%filter bigimage

LABEL Image Size Good for Machine Learning
equals Rows 2048
  + equals Columns 1536
  coordinates 0,0,512,200

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

We won't be using the header section for this example, but for your FYI, this is the recipe for how we would want to replace information in the header, if we were cleaning the headers. Right now we are just filtering images to flag those that might have PHI. Let's very strictly walk through the logic that will be taken above:

 1. If the header contains field PatientSex "M" (Male), and is missing PatientBirthDate and OperatorsName is not "bold bread," we flag. Otherwise, keep going.
 2. If the header has field Rows 2048 and Columns 1536 we flag.

The flag that is done first (more specific) is the final decision. This means that you should have your known coordinates of PHI (eg, specific modality, manufacturer, etc) first, and followed by more general estimates of PHI. Likely a later group will create flags for more manual inspection.

More examples (and client) coming soon, need to write tests, etc. first!
