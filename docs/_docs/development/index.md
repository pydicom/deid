---
title: Development Notes
permalink: /development/index.html
category: Development
order: 1
---

This readme is intended to explain how the functions work (on the back end) for those
wishing to create a module for a new image type. The basic idea is that each folder
(module, eg `dicom`) contains a base processing template that tells the functions to
`get_identifiers` how to process different header values for the datatype
(e.g, DICOM).

 - [Add an Image Format]({{ site.baseurl }}/development/add-format/)
 - [Linting and Formatting]({{ site.baseurl }}/development/linting-format/)
