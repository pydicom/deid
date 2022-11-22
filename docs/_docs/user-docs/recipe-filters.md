---
title: Recipe Filters
category: User Documentation
order: 2
---

As you recall from the [configuration]({{ site.baseurl }}/getting-started/dicom-config/)
notes page, the deid recipe allows you to configure both cleaning of pixels
and changing header values. This document will cover the first, how to write
and apply filters to clean images.

<a id="filters">
### Filters

You might want to flag images based on their header values. For example, "I have a directory
of dicom images, and I want to find those with `Modality` as `CT`. You can create
one or more filter groups to do this. If you create more than one, an image is attributed
to the filter group that comes first in the deid recipe file (indicating higher priority).
For example, an image that would be flagged with a general Blacklist criteria that is first flagged with Greylist
(meaning we know how to clean it) belongs to Greylist. We check higher priority
first to be computationally more efficient, because we can stop checking the
image when we hit the first criteria flag.

<a id="filter-groups">
#### Filter Groups
While you are free to define your own groups and criteria, we provide a [default deid](https://github.com/pydicom/deid/blob/master/deid/data/deid.dicom) that has the following levels defined within:

 - **Greylist** is typically checked first, and an image being flagged for this groups means that contains PHI in a reliable, known configuration. The greylist checks are based on image headers like modality, and manufacturer that we are positive about the locations of pixels that need to be scrubbed. If an image is greylisted, we can confidently clean it, and continue processing. This strategy is similar to the MIRC-CTP protocol.

 - **Whitelist**: images also must pass through sets of criteria that serve as flags that the image is reliable to not contain any PHI.  These images can be passed without intervention (Note from Vanessa, I don't see many circumstances for which this might apply).

 - **Blacklist** images that are not Greylisted or Blacklisted are largely unknowns. They may contain PHI in an unstructured fashion, and we need to be conservative and precaucious. Blacklist images may be passed through a more sophisticated filter (such as a character recognition algorithm), deleted, or passed through and possibly marked (in the DICOM header or on the image) to note the images are blacklisted (with the requesting researcher defining the best method).

<a id="filter-example">
#### Filter Example

I'll again show you the previous example, but give more detail this time.
The start of a filter might look like this:

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
The formatting of this is inspired by both [CTP](http://mircwiki.rsna.org/index.php?title=The_CTP_DICOM_Filter)
and my early work with [Singularity Containers](https://sylabs.io/docs/), which is based on RPM.

<a id="how-are-images-filtered">
##### How are images filtered?
You can imagine an image starting at the top of the file, and moving down line by line.
If at any point it doesn't pass criteria, it is flagged and placed with the group,
and no further checking is done.  For this purpose, the sections are ordered by
their specificity and preference. This means that, for the above, by placing
blacklist after graylist we are saying that an image that could be flagged
to be both in the blacklist and graylist will hit the graylist first. This is
logical because the graylist corresponds to a specific set of image header
criteria for which we know how to clean. We only resort to general blacklist
criteria if we make it far enough and haven't been convinced that there isn't PHI.

<a id="how-do-i-read-a-criteria">
##### How do I read a criteria?
Each filter section criteria starts with `LABEL`. this is an identifier to
report to the user given that the flag goes off. Each criteria then has the following format:

```
<criteria> <field> <value>
```
where "value" is optional, depending on the filter. For example:

```
LABEL Burned In Annotation
contains ImageType SAVE
```

Reads "flag the image with a Burned In Annotation, which belongs to the blacklist filter,
if the ImageType fields contains SAVE." If you want to do an "and" statement across
two fields, just use `+`:

```
contains ImageType SAVE
  + contains Manufacturer GE
```

> "flag the image if the ImageType contains SAVE AND Manufacturer contains GE. To do an "or"

```
contains ImageType SAVE
  || contains Manufacturer GE
```

> "flag the image if the ImageType contains SAVE OR Manufacturer contains GE.

And you can have multiple criteria for one `LABEL`

```
contains SeriesDescription SAVE
+ contains BurnedInAnnotation YES
empty ImageType
|| empty DateOfSecondaryCapture
```

 - First check: "flag the image if SeriesDescription contains SAVE AND BurnedInAnnotation has YES"
 - Second check: "flag the image if ImageType is empty or DateOfSecondaryCapture is empty."

And to make it even simpler, if you want to check one field for a value a OR b,
you can use regular expressions. The following checks ImageType for "CT" OR "MRI"

```
equals ImageType CT|MRI
```

which is equivalent to:

```
equals ImageType CT
|| equals ImageType MRI
```

What if you want to evaluate an inner statement? Eg: "flag the image if Criteria 1 and (Criteria 2 OR Criteria 3)? The inner parentheses would need to be evaluated first. You would represent the content of the inner parentheses (Criteria 1 or Criteria 2) on the same line:

```
LABEL Ct Dose Series
  contains Criteria1
  + contains Criteria2 Value2 || contains Criteria3 Value3
  coordinates 0,0,512,200
```

<a id="what-are-the-criteria-options">
##### What are the criteria options?
For all of the below, case does not matter. All fields are changed to lowercase before comparison, and stripped of leading and trailing white spaces.

 - **contains** is using a regular expression search, meaning that the word can appear anywhere in the field (eg, a `contains` "save" would flag a value of "saved".
 - **equals** means you want to match an expression exactly. `equals` with "save" would not flag a value of "saved".
 - **empty** means that the header is present in the data, but it's an empty string (eg, "").
 - **missing** means that the header is not present in the data.
 - **notEquals** is the inverse of equals
 - **notContains** is the inverse of contains

<a id="how-do-i-customize-the-process">
##### How do I customize the process?
There are several things you can customize!

- You first don't have to use the application default files. You can make a copy, customize to your liking, and provide the path to the file as an argument. If you have criteria to contribute, we encourage you to do so.
- The name of the filter itself doesn't matter, you are free to use different terms than whitelist, blacklist, etc.
