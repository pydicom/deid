# Anonymization toward De-identifiction (deid)

This Python module is intended for basic coding of medical images, which means "cleaning" image headers and pixel data, and integrating with your own functions to replace with anonymous identifiers. Per HIPAA, this process is technically called "anonymization," meaning we did our best effort. What this module does not do:

 - does *not* provide a workflow manager to perform these actions. If you need one, see [sendit](https://www.github.com/pydicom/sendit) or [dicom-database](https://www.github.com/pydicom/dicom-database) use `deid` for this task.
 - does *not* implement any custom API calls to retrieve identifiers from some specific database. If you are from Stanford and looking for those tools, [see here](https://www.github.com/vsoch/som).

What this module does do:

 - Anonymize header data based on a specific logic of replacing, blanking, removing, or some custom function (e.g., "replace field X with item Y,")
 - Pass images through a filter for quarantine based on header logic, and if pixel coordinates are available, can black them out.
 - For each of the above, you can use defaults (blacklist, whitelist, graylist), or create your own customized logic.
 - provides functions for developers, and executables and containers for users.

For dicom data, we use [pydicom](https://www.github.com/pydicom/pydicom) and for nifti we (will) use [nibabel](http://nipy.org/nibabel/).

## Getting Started
If you are *not* a developer, or interested in getting started with using and understanding the software, you should start out by reading our [getting-started](getting-started.md) guide.  If you are a developer and are interested in using `deid` to implement a custom pipeline, see the following sections:

## Dicom

 - [Loading Data](loading.md): The starting point for any de-identification process is to read in your files from the system. We provide examples of how to do that.
 - [Configuration](config.md): You next want to tell the software how to handle various fields. If you don't have a good sense, we provide a default configuration that returns fields for you to inspect, and removes them from the data.
 - [Get Identifiers](get.md): A request for identifiers is a get, meaning it will extract fields from the data, and give you a data structure that you can then (optionally) add to in the case of wanting to substitute any fields.
 - [Clean Pixels](pixels.md): Before you scrape headers, you might need to use them to flag images that have burned in pixel annotations, and deal with them appropriately.
 - [Put Identifiers](put.md): `put` corresponds to the anonymization step. This is when you give your (possibly changed) request from get to a function to de-identify the data.
 - [Developer Notes](developer.md): explains how a module (eg, the folder `dicom`) is set up, and you should follow this format if you want to add a new module.


## Dicom Tools
 - [Tags](tags.md): A few helpful functions for searching and filtering tags.
