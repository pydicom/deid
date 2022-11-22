---
title: 2. Configuration
category: Getting Started
order: 4
---

Deid does two things, generally cleaning pixels and headers of dicom images.
We do this by way of a file called a deid recipe. Here is a quick example
that is intended for dicom images:

```
FORMAT dicom

%filter dangerouscookie

LABEL Criteria for Dangerous Cookie
contains PatientSex M
  + notequals OperatorsName bold bread
  coordinates 0,0,512,110

%header

ADD PatientIdentityRemoved YES
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

Don't worry that we haven't talked about this format yet! Generally, you could
probably guess that we are going to create a filter called "dangerouscookie"
based on some set of criteria, and perform some actions on image headers.
Let's first discuss each of the sections.

<a id="sections">
## Sections

A section is a part of the recipe that starts with a "%". You can think of
a section as a chunk of text that is parsed for some purpose. For example,
`%filter` is a section where it's expected that you've defined filters, and
`%header` is expected to have actions to update and change headers.


|  Section    | Description                                               | Example                                 |
|-------------|-----------------------------------------------------------|-----------------------------------------|
| %filter     | a named set of filter criteria used when running the DicomCleaner | %filter filterName              |
| %header     | actions to be taken to update, or otherwise change an image header | %header                        |
| %labels     | extra metadata (key value pairs) to add to a recipe | Maintainer @vsoch                             |

> What functions do the recipe sections correspond to?

Good question! Let's talk about the two primary functions of deid, and how
to write recipes to do those things.

<a id="clean-pixels">
## Clean Pixels

The general application flow of the clean function is the following:

```
[define criteria] -> [filter] -> [clean images] -> [save]
```

The "filter" tag broadly encompasses an inspection of the header data. The "clean"
action corresponds with either:

 - an action applied to a header field, like "REPLACE FieldA with value B" or
 - replacing pixels in the image with a black box to hide text and other identifiers

For reading more about how the Deid software does this by way of a file called
a deid recipe, read about deid [recipe filters]({{ site.baseurl }}/user-docs/recipe-filters/).

<a id="clean-headers">
## Clean Headers

The general application flow to clean headers looks like this:

```
[define actions] -> [get identifiers] --> [update identifiers] --> [replace identifiers]
```

And then optionally save the updated files!

More detail is provided about cleaning headers in the [recipe headers]({{ site.baseurl }}/user-docs/recipe-headers/)
pages.


> Where do I go from here?

 - [Recipe Filters]({{ site.baseurl }}/user-docs/recipe-filters/)
 - [Recipe Headers]({{ site.baseurl }}/user-docs/recipe-headers/)
 - [Recipe Labels]({{ site.baseurl }}/user-docs/recipe-labels/)
