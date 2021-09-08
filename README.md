# Deidentify (deid)

Best effort anonymization for medical images in Python.

[![DOI](https://zenodo.org/badge/94163984.svg)](https://zenodo.org/badge/latestdoi/94163984)
[![Build Status](https://travis-ci.org/pydicom/deid.svg?branch=master)](https://travis-ci.org/pydicom/deid)

Please see our [Documentation](https://pydicom.github.io/deid/).

These are basic Python based tools for working with medical images and text, specifically for de-identification.
The cleaning method used here mirrors the one by CTP in that we can identify images based on known
locations. We are looking for collaborators to develop and validate an OCR cleaning method! Please reach out if you would like to help work on this.


## Installation

### Local
For the stable release, install via pip:

```bash
pip install deid
```

For the development version, install from Github:

```bash
pip install git+git://github.com/pydicom/deid
```

### Docker

```bash
docker build -t pydicom/deid .
docker run pydicom/deid --help
```

## Issues
If you have an issue, or want to request a feature, please do so on our [issues board](https://www.github.com/pydicom/deid/issues).
