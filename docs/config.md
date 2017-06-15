# Configuration

The de-identification process has three parts:

 - define a set of rules for de-identification (optional)
 - [get](get.md) current fields (if you need to use them to look up replacements, etc)
 - [put](put.md) (possibly updated) identifiers back into the data, and deidentify fully.

This document will talk about the first step of this process, how you can configure rules for the software.

## Defaults
The application does the following, by default, taking a conservative de-identification process:

 1. All fields considered HIPAA are returned to you for inspection.
 2. You can replace none or all of these fields with your identifiers of choice
 3. The data will be rewritten with your changes, and all other fields will be removed.
 4. A header field will be added that says the data has been de-identified.

However, you might want to do either of the following:

 - ask the application to return more fields (beyond default, and if present) from the dicom header
 - have a specific action for some set of headers, where actions include `BLANK`, `REPLACE`, `REMOVE`, and `KEEP`
 - perform some custom functions between `get` and `put`.

We will show you a working example of the above as you continue this walkthrough. For now, let's talk about a few options, and show examples of settings. The settings that you choose depend on your use case, and we strongly suggest that you take the most conservative approach that is possible for your use case. 

### Option 1. Blanked Header
In the case that you get a response after extraction and replace no fields, the header fields will be completely removed, other than a field to indicate this has been done (recommended for most). 

### Option 2. Blanked Header with Study identifier
If you need to save some identifier as a lookup, we recommend a conservative approach that leaves the minimal required (de-identified) study identifier eg, (PatientID) is replaced with (StudyID), removing the rest. Any identifiers that you might want to save should be kept separately from where you intend to release the data, and this of course will require IRB approval.


### Option 3: Custom
For a custom de-identification, then you need to make a config file called `deid` that should be provided with your function calls. The format of this file is discussed below, and can be used to specify preferences for different kinds of datasets (dicom or nifti) and things to identify (pixels and headers).

## Rules
You can create a specification of rules, a file called `deid`, for the application to customize its behavior. Let's look at an example:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
BLANK OrdValue
KEEP Modality
REPLACE id
REMOVE ReferringPhysicianName
```

In the above example, we specify the commands are intended to use the dicom module by first `FORMAT` label. This is a message to the application that the following commands are intended to come from this exact module folder. We then know that we are dealing with functions relevant to the header of the image by way of the `%header` section. The section then consists of a series of commands, each specifying an action to be taken on a particular field. The allowed actions are the follow:

 - ADD: Add a new field to the dataset(s). If the value is a string, it's assumed to be the value that is desired to be added. If the value is in the form `var:OrdValue` then the application will expect to find the value to replace in a variable in the request called `OrdValue` (more on this later).
 - BLANK: If you want to blank a field instead of remove it, use this option. Note that there is a [bug](https://github.com/pydicom/pydicom/issues/372) related to how to properly blank fields, so in some cases you might see an error. For this reason I (@vsoch) have chosen to make the default removing for now.
 - KEEP: implies that the value should not be replaced, removed, or blanked.
 - REPLACE: implies that the value should be replaced by a string, or a variable in the format `var:FieldName`.
 - REMOVE: completely remove the field from the dataset. This is the default action.

For the above, given that there are conflicting commands, the more conservative is given preference. For example:

```
REMOVE > BLANK > REPLACE > KEEP/ADD
``` 

For example, if I add or keep a header, but then also specify to blank or remove it, it will be blanked or removed. If I specify to blank a header and remove it, it will be removed. If I specify to replace a header and blank it, it will be blanked. Most of the time, you won't need to specify remove, because it is the default. If we were to come up with a pretend config file to represent the default, it would look like this:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REMOVE *

```

The suggested approach that you should take, replacing the main entity data with some identifier that you've selected, would look something like this:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
```

If you wanted to also replace the image (InstanceSOPUID) with an identifier, that might look like this:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

And the expectation would be that you provide variables with keys `source_id` and `id` appended to the response from get that is handed to the put action. In the future when we add support for other data types, the config might look something like this (note the added nifti section):

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE InstanceSOPUID var:source_id

FORMAT nifti

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE InstanceSOPUID var:source_id
```

and when we have procedures (functions) to perform on data, for example, scrubbing pixels, those will be specified in a separate `%pixels` section: 

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id

%pixels

RUN clean_pixels
```

In the above example, the function `clean_pixels` would be expected to be importable from the dicom module:

```
from deid.dicom import clean_pixels
```

For more complex tasks like converting from dicom to nifti, the user is (for now) suggested to work with the formats separately, meaning a config file for the dicoms (meaning with `FORMAT dicom`) to output to a folder with nifti files, and then using a separate `deid` with `FORMAT nifti` for that folder. It could be possible to combine these into one file at some point, i need to think about it.

Now that you know how configuration works, we should look at some examples for generating a basic [get](get.md), which is will get a set of fields and values from your dicom files.
