# Deidentify (deid)

Best effort anonymization for medical images in Python.

[![DOI](https://zenodo.org/badge/94163984.svg)](https://zenodo.org/badge/latestdoi/94163984)
[![Build Status](https://travis-ci.org/pydicom/deid.svg?branch=master)](https://travis-ci.org/pydicom/deid)

Please see our [Documentation](https://pydicom.github.io/deid/).

These are basic Python based tools for working with medical images and text, specifically for de-identification.
The cleaning method used here mirrors the one by CTP in that we can identify images based on known
locations. We are looking for collaborators to develop and validate an OCR cleaning method! Please reach out if you would like to help work on this.

## HIPAA-safe Quickstart (use synthetic data only)

**Never test with real Protected Health Information (PHI).** Start with synthetic DICOM files so you can practice safely.

Install:
pip install deid deid-data pydicom

Minimal check in Python (loads one synthetic DICOM file):
from deid.data import get_dataset
from deid.dicom import get_files, DicomCleaner

    # synthetic sample dataset name: "dicom-cookies"
    data_dir = get_dataset("dicom-cookies")
    test_file = next(get_files(data_dir))

    cleaner = DicomCleaner()      # create a simple cleaner
    cleaner.detect(test_file)     # analyze for potential burned-in PHI regions
    # cleaner.clean(...)          # optional: perform cleaning based on a recipe
    # cleaner.save_dicom(...)     # optional: save a cleaned copy

Notes:

- Use only synthetic datasets during evaluation (e.g., "dicom-cookies").
- Before sharing outputs or logs, verify they don’t contain identifiers.

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
