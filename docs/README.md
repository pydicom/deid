# De-identifiction (deid)

<script src="assets/js/asciinema-player.js"></script>
<link rel="stylesheet" href="assets/css/asciinema-player.css"/>


This Python module is intended for basic coding of medical images, which means replacing an identifier with a stable alias. We do this for both header and pixel data. For dicom data, we use [pydicom](https://www.github.com/pydicom/pydicom) and for nifti we use [nibabel](http://nipy.org/nibabel/) You can walk through these docs to get started.

## Client
We provide a simple client for working with the de-identification modules on the command line. If you are interested in this, see our [getting started](client.md) with the client. If you want to integrate the functions into your own applications, keep reading.

<asciinema-player src="assets/asciicast/deid.json" poster="data:text/plain,Intro to deid client" title="Introduction to the deid client" author="vsochat@stanford.edu" cols="125" rows="25" speed="2.0" theme="asciinema"></asciinema-player>


## Dicom

 - [Loading Data](loading.md): The starting point for any de-identification process is to read in your files from the system. We provide examples of how to do that.
 - [Configuration](config.md): You next want to tell the software how to handle various fields. If you don't have a good sense, we provide a default configuration that returns HIPAA/PHI related fields, and then removes the rest.
 - [Get Identifiers](get.md): A request for identifiers is a get, meaning it will extract fields from the data, and give you a data structure that you can then (optionally) add to in the case of wanting to substitute any fields.
 - [Put Identifiers](put.md): `put` corresponds to the deidentification step. This is when you give your (possibly changed) request from get to a function to de-identify the data.
 - [Developer Notes](developer.md): explains how a module (eg, the folder `dicom`) is set up, and you should follow this format if you want to add a new module.
