---
title: Introduction
category: Getting Started
permalink: /getting-started/index.html
order: 1
---

Deid does two things: clean header and image data, and filter based on headers.
These algorithms are not sophisticated - they perform their duties based on
parsing header metadata. Here we will provide getting started guides for each of the above
along with showing an example of a complete deid pipeline, including loading data,
configuring a custom recipe to deidentify and filter, and then cleaning pixels.

## Client

If you don't want to work in Python, or have developed a recipe that you want to run
from the command line, check out the [client usage]({{ site.baseurl }}/getting-started/client)
documentation.

## The Deid Recipe

The deid recipe is where you can identify rules to clean images, or to interact with header
metadata. Read our getting started guide on how to manage [recipes]({{ site.baseurl }}/examples/recipe) 
to filter and clean your images.

## Clean

Once you have a recipe, here is a guide to walk through how to [clean]({{ site.baseurl }}/getting-started/dicom-pixels) 
your image. "Clean" generally means replacing, removing, or otherwise editing header data, 
or blacking out pixels based on a set of known coordinates.

## Dicom
If you aren't sure where to start, here is a good spot! The following pages review a complete 
deid pipeline typically means some level of cleaning and filtering, and then saving final images.

 - [Loading Data]({{ site.baseurl }}/getting-started/dicom-loading): The starting point for any de-identification process is to read in your files.
 - [Configuration]({{ site.baseurl }}/getting-started/dicom-config): You next want to tell the software how to handle various fields.
 - [Get Identifiers]({{ site.baseurl }}/getting-started/dicom-get): A request for identifiers is a get, or extraction of data that can be modified.
 - [Clean Pixels]({{ site.baseurl }}/getting-started/dicom-pixels): Before you scrape headers, you might need to use them to flag images.
 - [Put Identifiers]({{ site.baseurl }}/getting-started/dicom-put): `put` corresponds to the anonymization step, putting cleaned headers back into the images.

If you are interested in other examples (with snippets of code) see our [examples]({{ site.baseurl }}/examples/) pages.
