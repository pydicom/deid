---
title: Introduction
category: Examples
permalink: /examples/index.html
order: 1
---

Here we have some examples to get you started! These examples correspond with
the subfolders of the repository [examples](https://github.com/pydicom/deid/tree/master/examples)
folder.

<a id="the-deid-recipe">
## The Deid Recipe

In this small tutorial, we will walk through reading and interacting with a deid recipe,
replacing header values, and saving new images. This is the recommended tutorial if you
want a quick start overview of deid.

 - [Code](https://github.com/pydicom/deid/tree/master/examples/recipe) on Github
 - [Tutorial]({{ site.baseurl }}/examples/recipe)
 - Recipes Files provided as [examples](https://github.com/pydicom/deid/tree/master/examples/deid) or [installed with deid](https://github.com/pydicom/deid/tree/master/deid/data).

<a id="header-manipulation">
## Header Manipulation

 - [Replace with Function]({{ site.baseurl }}/examples/func-replace/) shows how to dynamically replace or update header values from a function.
 - [Replace Sequences]({{ site.baseurl }}/examples/func-sequence-replace/) similar, but replacement of nested sequences.
 - [Header Expanders]({{ site.baseurl }}/examples/header-expanders/) can be used to select one or more header fields to apply an action to

<a id="cleaning-pixels">
## Cleaning Pixels

See an example of just "inspection" (flagging images based on criteria) or "clean"
(replacing values and writing black boxes after inspect) in these examples.

 - [Code](https://github.com/pydicom/deid/tree/master/examples/dicom/pixels) on Github

<a id="dicom-extract">
## Dicom Extract
These examples generally refer to the action of "getting data out of dicom files and putting
them somewhere else."

 - [Top Level Examples](https://github.com/pydicom/deid/tree/master/examples/dicom/dicom-extract) folder to see all scripts.
 - [Create Dicom CSV](https://github.com/pydicom/deid/blob/master/examples/dicom/dicom-extract/create-dicom-csv.py) meaning extraction of header values into comma separated values file.
