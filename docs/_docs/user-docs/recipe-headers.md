---
title: Recipe Headers
category: User Documentation
order: 3
---

As you recall from the [configuration]({{ site.baseurl }}/getting-started/dicom-config/) 
notes page, the deid recipe allows you to configure both cleaning of pixels 
and changing header values. This document covers the second - how to get, update,
and replace header values.

## Application Flow

Cleaning headers in dicom images typically has four parts:

 1. define a set of rules for updating values
 2. [get]({{ site.baseurl }}/getting-started/get) current fields (if you need to use them to look up replacements, etc)
 3. update these fields as you see needed
 4. [put]({{ site.baseurl }}/getting-started/put) (possibly updated) identifiers back into the data, and deidentify fully.

this document will talk about the first step in this process, 
how you can configure rules for the software. If you are interested in the command 
line client for these commands (and not functions) you should read about 
[the client]({{ site.baseurl }}/user-docs/client/).

## Defaults

The application does the following, by default, taking a conservative de-identification process:

 1. All fields are returned to you for inspection.
 2. You can replace none or all of these fields with your identifiers of choice
 3. The data will be rewritten with your changes, and all other fields will be blanked.
 4. A header field will be added that says the data has been anonymized.

However, you might want to do either of the following:

 - have a specific action for some set of headers, where actions include `BLANK`, `REPLACE`, `JITTER`, `REMOVE`, and `KEEP`
 - perform some custom functions between `get`, `update`, and `put`.

We will show you a working example of the above as you continue this walkthrough. For now, let's review configuration settings. 

### Standard Anonymization
For a best effort anonymization, you will likely want to extract data, replace some fields, 
and put back the replacements. In this case you need to make a config file that should be provided with your function calls. 

> The configuration files for deid are called "deid recipes"
 
The format of this file is discussed below, and can be used to specify preferences 
for different kinds of datasets (dicom or nifti) and things to identify (pixels and headers).

## Rules
You can create a specification of rules for the application to customize its behavior. 
The file standard that I've been using is to call all files `deid` and use a reverse extension to indicate tag,
so `deid.dicom` is a deid recipe for dicom, and `deid.chest-xray` might be a recipe for chest xray.
`deid.dicom.chest-xray` could combine those two things, suggesting a recipe for dicom chest xrays.
Let's look at an example:

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

In the above example, we tell the application exactly how to deal with header fields for dicom. 
We do that by way of sections (the lines that begin with `%` like `%header` and actions (eg, `KEEP`). 
Each of these variables will be discussed in detail, next.

### Format
The first thing that should appear in a recipe file is the `FORMAT` label. This is a message to the 
application that the following commands are intended for dicom files, and the name `dicom` 
matches exactly with the "dicom" module in the deid module. 

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

And the command in the file will either have the format of `<ACTION> <FIELD> <VALUE>` or 
in the case of binary actions, just `<ACTION> <VALUE>`. For example, both of the following are valid:

```
#<ACTION> <FIELD> <VALUE>
ADD PatientIdentityRemoved Yes
#<ACTION> <FIELD>
KEEP PixelData
```

#### Dynamic Values

**var**

In the case that your need to do something like "replace FIELD with my other variable," 
then you want to format the value to tell the application that it should find the field 
in the data structure you pass it (discussed later). That format looks like this:

```
#<ACTION> <FIELD> <VALUE>
REPLACE PatientID var:suid
```

In the above, we tell the software to replace the field `PatientID` with whatever 
value is defined under variable `suid`. Now let's talk about how the actions are 
relevant to different sections, first the header.


**func**

It might also be the case that you want to replace a field value with something
generated on the fly from a function. In this case, you should define a "func:function_name"
instead:

```
#<ACTION> <FIELD> <VALUE>
REPLACE PatientID func:generate_suid
```

When you do this, the function is expected to be defined in the customized
item dictionary that you pass in (e.g., modified output from `get_identifiers`)
See the [Frame of Reference]({{ site.baseurl }}/examples/header-manipulation/) example
for a walkthrough of how to do this.


#### Header
We know that we are dealing with functions relevant to the header of the image 
by way of the `%header` section. This section can have a series of commands called 
actions that tell the software how to deal with different fields. For the header 
section, the following actions are allowed, and each is specific to an action to 
be taken on a header field/value:

 - ADD: Add a new field to the dataset(s). If the value is a string, it's assumed to be the value that is desired to be added. If the value is in the form `var:OrdValue` then the application will expect to find the value to replace in a variable in the request called `OrdValue` (more on this later).
 - BLANK: If you want to blank a field instead of remove it, use this option. This is the default action.
 - KEEP: implies that the value should not be replaced, removed, or blanked.
 - REPLACE: implies that the value should be replaced by a string, or a variable in the format `var:FieldName`.
 - REMOVE: completely remove the field from the dataset.

For the above, given that there are conflicting commands, the more conservative is given preference. For example:

```
REMOVE > BLANK > REPLACE > JITTER/KEEP/ADD
``` 

For example, if I add or keep a header, but then also specify to blank or remove it, 
it will be blanked or removed. If I specify to blank a header and remove it, it will be removed. 
If I specify to replace a header and blank it, it will be blanked. Most of the time, 
you won't need to specify remove, because it is the default. If we were to come up with 
a pretend config file to represent the default, it would look like this:

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

The above would remove everything except for the pixel data, and a few fields 
that are relevant to its dimensions. It would add a field to indicate the 
patient's identity was removed.

##### Jitter
For jitter, you can add a hard coded number, or a variable to specify it:

```
JITTER StudyDate var:jitter
JITTER Date 31
JITTER PatientBirthDate -31
```

##### Field Expansion
In some cases, it might be extremely tenuous to list every field ending in the same thing, 
to perform the same action for. For example:

```
JITTER StudyDate var:jitter
JITTER Date var:jitter
JITTER PatientBirthDate var:jitter
```

could much better be captured as:

```
JITTER endswith:Date var:jitter
```

and this is the idea of an `expander`. And expander is an optional filter 
applied to a header field (the middle value) to select some subset of header 
values. Currently, we support `startswith`, `endswith`, `contains`, `allexcept`,
and `allfields`.
 
The following examples show what fields are selected based on each filter. For
all examples, the test is done making the values lowercase.

**endswith**

The endswith filter will look for header field names that end with a particular expression.
Lower and upper casing does not matter, so writing `endswith:Date` is akin to writing
`endswith:Date`.

```
JITTER endswith:Date var:jitter
['AcquisitionDate', 'ContentDate', 'InstanceCreationDate', 'PatientBirthDate', 'PerformedProcedureStepStartDate', 'SeriesDate', 'StudyDate']
```

**startswith**

The startswith filter will look for header field names that start with a particular expression.
Casing also doesn't matter.

```
REMOVE startswith:Patient                  
['PatientAddress', 'PatientAge', 'PatientBirthDate', 'PatientID', 'PatientName', 'PatientPosition', 'PatientSex']
```

**contains**

The contains filter searches for a string of interest in the field. For example, if
we ask for fields that contain "Name" will look for header field names that contain the string 
"Name" in any casing.


```
BLANK contains:Name
['InstitutionName', 'NameOfPhysiciansReadingStudy', 'OperatorsName', 'PatientName', 'ReferringPhysicianName']
```

Notice how we get Name in uppercase (when our search string was lowercase) and
it can appear anywhere in the field.

**all**

All fields will allow you to apply a filter to all fields. In the example below,
we have a function "remove_identifiers" defined in the python environment, and
will run it over all fields, returning a value to update the field in question.

```
ADD ALL func:remove_identifiers
```

**except**

Akin to all fields, except provide a list of fields that you want to disclude from
a global selector. Here are some examples to include all fields except StudyDate 
or StudyTime.

```
BLANK except:StudyDate|StudyTime
BLANK except:StudyTime
```

If you are familiar with regular expressions, you'll notice the "|" which 
means "or" in the regular expression. You are free to write whatever regular
expression fits your needs to disclude particular fields here.

## Example

The suggested approach that you should take, replacing the main entity data 
with some identifier that you've selected, would look something like this:

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

And the expectation would be that you provide variables with keys `source_id` and `id` 
appended to the response from get that is handed to the put action. 

## Future Additions

### Format nifti
In the future when we add support for other data types, the config might look 
something like this (note the added nifti section):

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

Now that you know how configuration works, you have a few options.
If you want to write a text file and get going with cleaning your files, you should 
look at some examples for generating a basic [get]({{ sitebase.url }}/getting-started/dicom-get/), 
which is will get a set of fields and values from your dicom files. For a full walk through
example with a recipe, see the [recipe example]({{ sitebase.url }}/examples/recipe)
