---
title: Introduction
category: Getting Started
permalink: /getting-started/index.html
order: 1
---

Deid does two things: clean header and image data, and filter based on headers.
These algorithms are not sophisticated - they perform their duties based on
parsing header metadata. Here we will provide a simple walkthrough to get started
with deid. In the following pages, we will show you how to load data,
configure a custom recipe to deidentify and filter, and then clean pixels.

## Dicom Pipeline

A complete deid pipeline typically means some level of cleaning and filtering, and then saving final images.

 - [Loading Data]({{ site.baseurl }}/getting-started/dicom-loading): The starting point for any de-identification process is to read in your files.
 - [Configuration]({{ site.baseurl }}/getting-started/dicom-config): You next want to tell the software how to handle various fields.
 - [Get Identifiers]({{ site.baseurl }}/getting-started/dicom-get): A request for identifiers is a get, or extraction of data that can be modified.
 - [Clean Pixels]({{ site.baseurl }}/getting-started/dicom-pixels): Before you scrape headers, you might need to use them to flag images.
 - [Put Identifiers]({{ site.baseurl }}/getting-started/dicom-put): A "put" corresponds to putting cleaned headers back into the images.

If you are interested in other examples (with snippets of code) see our [examples]({{ site.baseurl }}/examples/) pages.
For more detailed user documentation on writing recipes, see the [user documentation]({{ site.baseurl }}/user-docs/) base.
