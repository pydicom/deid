# Configuration

The de-identification process has three parts:

 - define a set of rules for de-identification (optional)
 - [get](get.md) current fields (if you need to use them to look up replacements, etc)
 - [update](update.md) identifiers however you need for your de-identification process.
 - [put](put.md) (possibly updated) identifiers back into the data, and deidentify fully.

This document will talk about the first step of this process, how you can configure rules for the software. If you are interested in the command line client for these commands (and not functions) you should see [the client](client.md).

## Defaults
The application does the following, by default, taking a conservative de-identification process:

 1. All fields are returned to you for inspection.
 2. You can replace none or all of these fields with your identifiers of choice
 3. The data will be rewritten with your changes, and all other fields will be blanked.
 4. A header field will be added that says the data has been de-identified.

However, you might want to do either of the following:

 - have a specific action for some set of headers, where actions include `BLANK`, `REPLACE`, `JITTER`, `REMOVE`, and `KEEP`
 - perform some custom functions between `get`, `update`, and `put`.

We will show you a working example of the above as you continue this walkthrough. For now, let's review configuration settings. 

### Standard De-identification
For a standard de-identification, you will likely want to extract data, replace some fields, and put back the replacements. In this case you need to make a config file called `deid` that should be provided with your function calls. The format of this file is discussed below, and can be used to specify preferences for different kinds of datasets (dicom or nifti) and things to identify (pixels and headers).

## Rules
You can create a specification of rules, a file called `deid`, for the application to customize its behavior. Let's look at an example:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
BLANK OrdValue
KEEP Modality
REPLACE id var:entity_id
JITTER StudyDate var:entity_timestamp
REMOVE ReferringPhysicianName
```

In the above example, we tell the application exactly how to deal with header fields for dicom. We do that by way of sections (the lines that begin with `%` like `%header` and actions (eg, `KEEP`). Each of these variables will be discussed in detail, next.

### Format
The first thing that should appear in a recipe file is the `FORMAT` label. This is a message to the application that the following commands are intended for dicom files, and the name `dicom` matches exactly with the module we have provided, [dicom](../deid/dicom). 


### Sections
Each section corresponds to a part of the data (eg, header or pixels) and then defines actions that can be taken for it.

#### Actions
Although different sections can have their own actions defined, for simplicity many sections share the same set:

 - ADD
 - BLANK
 - JITTER
 - KEEP
 - REMOVE
 - REPLACE

And the command in the file will either have the format of `<ACTION> <FIELD> <VALUE>` or in the case of binary actions, just `<ACTION> <VALUE>`. For example, both of the following are valid:

```
#<ACTION> <FIELD> <VALUE>
ADD PatientIdentityRemoved Yes
#<ACTION> <FIELD>
KEEP PixelData
```

In the case that your need to do something like "replace FIELD with my other variable," then you want to format the value to tell the application that it should find the field in the data structure you pass it (discussed later). That format looks like this:

```
#<ACTION> <FIELD> <VALUE>
REPLACE PatientID var:suid
```

In the above, we tell the software to replace the field `PatientID` with whatever value is defined under variable `suid`. Now let's talk about how the actions are relevant to different sections, first the header.


#### Header
We know that we are dealing with functions relevant to the header of the image by way of the `%header` section. This section can have a series of commands called actions that tell the software how to deal with different fields. For the header section, the following actions are allowed, and each is specific to an action to be taken on a header field/value:

 - ADD: Add a new field to the dataset(s). If the value is a string, it's assumed to be the value that is desired to be added. If the value is in the form `var:OrdValue` then the application will expect to find the value to replace in a variable in the request called `OrdValue` (more on this later).
 - BLANK: If you want to blank a field instead of remove it, use this option. This is the default action.
 - KEEP: implies that the value should not be replaced, removed, or blanked.
 - REPLACE: implies that the value should be replaced by a string, or a variable in the format `var:FieldName`.
 - REMOVE: completely remove the field from the dataset.

For the above, given that there are conflicting commands, the more conservative is given preference. For example:

```
REMOVE > BLANK > REPLACE > JITTER/KEEP/ADD
``` 

For example, if I add or keep a header, but then also specify to blank or remove it, it will be blanked or removed. If I specify to blank a header and remove it, it will be removed. If I specify to replace a header and blank it, it will be blanked. Most of the time, you won't need to specify remove, because it is the default. If we were to come up with a pretend config file to represent the default, it would look like this:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REMOVE *
KEEP PixelData
KEEP SamplesPerPixel
KEEP Columns
KEEP Rows
```

The above would remove everything except for the pixel data, and a few fields that are relevant to its dimensions. It would add a field to indicate the patient's identity was removed.

##### Jitter
For jitter, you can add a hard coded number, or a variable to specify it:

```
JITTER StudyDate var:jitter
JITTER Date 31
JITTER PatientBirthDate -31
```

##### Field Expansion
In some cases, it might be extremely tenuous to list every field ending in the same thing, to perform the same action for. For example:

```
JITTER StudyDate var:jitter
JITTER Date var:jitter
JITTER PatientBirthDate var:jitter
```

could much better be captured as:

```
JITTER endswith:Date var:jitter
```

and this is the idea of an `expander`. And expander is an optional filter applied to a header field (the middle value) to select some subset of header values. Currently, we support `startswith` and `endswith`. The following examples show what fields are selected based on each filter:

```
JITTER endswith:Date var:jitter
['AcquisitionDate', 'ContentDate', 'InstanceCreationDate', 'PatientBirthDate', 'PerformedProcedureStepStartDate', 'SeriesDate', 'StudyDate']


REMOVE startswith:Patient                  
['PatientAddress', 'PatientAge', 'PatientBirthDate', 'PatientID', 'PatientName', 'PatientPosition', 'PatientSex']
```


#### Pixels
The `%pixels` section has not been implemented yet, but will allow for specification of how to de-identify pixel data.

#### Labels
The `%labels` section is a way for the user to supply custom commands to an application that aren't relevant to the header or pixels. For example, If I wanted to carry around a version or a maintainer address, I could do that as follows:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID cookie-monster

%labels
ADD MAINTAINER vsochat@stanford.edu
ADD VERSION 1.0
```

As you can see, the labels follow the same action commands as before, in the case that the application needs them. In case you are interested in what the application sees when it reads the file above (if you are a developer) it looks like this:

```
{
   "labels":[
      {
         "field":"MAINTAINER",
         "value":"vsochat@stanford.edu",
         "action":"ADD"
      },
      {
         "field":"VERSION",
         "value":"1.0",
         "action":"ADD"
      }
   ],

   "format":"dicom",
   "header":[
      {
         "field":"PatientIdentityRemoved",
         "value":"Yes",
         "action":"ADD"
      },
      {
         "field":"PatientID",
         "value":"cookie-monster",
         "action":"REPLACE"
      }
   ]
}
```

And you are free to map the actions (eg, `ADD`, `REMOVE`) onto whatever functionality is relevant to your application, or just skip the action entirely and use the fields and values.

## Examples
The suggested approach that you should take, replacing the main entity data with some identifier that you've selected, would look something like this:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
```

If you wanted to also replace the image (SOPInstanceUID) with an identifier, that might look like this:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

And the expectation would be that you provide variables with keys `source_id` and `id` appended to the response from get that is handed to the put action. 

## Future Additions

### Format nifti
In the future when we add support for other data types, the config might look something like this (note the added nifti section):

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

### Section pixels
and when we have procedures (functions) to perform on data, for example, scrubbing pixels, those will be specified in a separate `%pixels` section: 

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id

%pixels

ADD clean_pixels
```

In the above example, the function `clean_pixels` would be expected to be importable from the dicom module:

```
from deid.dicom import clean_pixels
```

For more complex tasks like converting from dicom to nifti, the user is (for now) suggested to work with the formats separately, meaning a config file for the dicoms (meaning with `FORMAT dicom`) to output to a folder with nifti files, and then using a separate `deid` with `FORMAT nifti` for that folder. It could be possible to combine these into one file at some point, i need to think about it.

Now that you know how configuration works, we should look at some examples for generating a basic [get](get.md), which is will get a set of fields and values from your dicom files.
