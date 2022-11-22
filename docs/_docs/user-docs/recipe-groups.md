---
title: Recipe Groups
category: User Documentation
order: 4
---

The [recipe headers]({{ site.baseurl }}/user-docs/recipe-headers/) page taught you
how to write a recipe that has one or more commands to parse a dicom image header.
For example, we might have:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved YES
BLANK OrdValue
KEEP Modality
REPLACE id var:entity_id
JITTER StudyDate var:entity_timestamp
REMOVE ReferringPhysicianName
```

But what if we want to optimize our parsing by creating custom groups of tags
that are based on the field names, or the values? This is the intended use
case for groups - a group is a group of tags, either identified by
fields or values, for which an action can be applied. For the examples
below, we will use this sample header provided by [@wetzelj](https://github.com/wetzelj). Thank you!

```
(0008,0050) : SH   Len: 10     AccessionNumber                Value: [999999999 ]
(0008,0070) : LO   Len: 8      Manufacturer                   Value: [SIEMENS ]
(0008,1090) : LO   Len: 22     ManufacturersModelName         Value: [SOMATOM Definition AS+]
(0009,0010) : LO   Len: 20     PrivateCreator10xx             Value: [SIEMENS CT VA1 DUMMY]
(0010,0010) : PN   Len: 14     PatientsName                   Value: [SIMPSON^HOMER^J^]
(0010,0020) : LO   Len: 12     PatientID                      Value: [000991991991 ]
(0010,1000) : LO   Len: 8      OtherPatientIDs                Value: [E123456]
(0010,1001) : PN   Len: 8      OtherPatientNames              Value: [E123456]
(0010,21B0) : LT   Len: 90     AdditionalPatientHistory       Value: [MR SIMPSON LIKES DUFF BEER]
(0019,1091) : DS   Len: 6      <Unknown Tag>                  Value: [E123456]
(0019,1092) : DS   Len: 6      <Unknown Tag>                  Value: [M123456]
```

<a id="fields">
## Fields

A fields section looks like the following:

```
FORMAT dicom

%fields patient_info
FIELD PatientID
FIELD startswith:OtherPatient
FIELD endswith:Name
```

There would be multiple ways to do this (for example you could have used `startswith:Patient` to target both `PatientsName`
and `PatientID`) but generally this will produce a list of fields that are named "patient_info." Here is the list
rendered out pretty:

```
patient_info
------------
PatientID
OtherPatientIDs
OtherPatientNames
PatientsName
```

We can then use this in recipe header sections where we want to apply an action to one or more fields
as follows:

```
%header

REPLACE fields:patient_info func:generate_uid
```

And this reads nicely as "Replace fields defined in patient_info to be the variable
I'm defining with the function generate_uid (which should be added to each item
after lookup).

This of course means that the actions supported for the `%fields` section includes:

 - **FIELD** reference to a full name of a field, or any parsing of any [expander]({{ site.baseurl }}/examples/header-expanders/).

<a id="values">
## Values

It could be that you want to generate a list of _values_ extracted from the dicom
to use as flags for checking other fields. For example, if I know that the Patient's ID
is in PatientID, I would want to extract the patient's name from that field,
and then search across fields looking for any instance of a first or last name.
This is the purpose of the `%values` group. Instead of defining rules to create
a list of fields, we write rules to extract values. Let's take a look at an
example:

```
%values patient_info
SPLIT PatientsName splitval='^';minlength='4'
FIELD PatientID
FIELD OtherPatientIDs
```

You'll notice that we have `FIELD` again, but since this is in a `%values`
section, this is saying "Find the fields Patient ID and Other Patient IDs, and whatever
_values_ you find there, add to the list `patient_info`." You'll also
notice that the first line uses a new action `SPLIT`:

```
SPLIT PatientsName splitval='^';minlength='4'
```

This action says to start with the field `PatientsName`, split based on the `^`
character, and keep results that have a length greater than or equal to 4.
Let's talk about these actions in detail. Field is the same, but we also have split:

 - **FIELD** refers to the full name of a field, or any parsing of any [expander]({{ site.baseurl }}/examples/header-expanders/). Instead of including these field names, we grab the values from them, and add to our list.
 - **SPLIT** indicates that we want to apply a split operation to a field (or expansion of fields) and for all, to split by a character (defaults to a space) and take a minimum length (defaults to 1).

The result of the above operation might look like this - and remember that this is a list of values.

```
patient_info
------------
HOMER
SIMPSON
```

You could then reference these values for some header action. For example, let's say
we want to remove any field that contains these identifiers:

```
%header
REMOVE values:patient_info
```

The implication of the above is that we are checking all fields for these values.
This would be functionally equivalent:

```
%header
REMOVE ALL values:patient_info
```

Or you could chose some other field name, or field expander, if you want to limit
the removal to some subset.

If you haven't yet, take a look at how at generate a basic [get]({{ site.baseurl }}/getting-started/dicom-get/),
which is will get a set of fields and values from your dicom files.
