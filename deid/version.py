__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

__version__ = "0.3.21"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsoch@users.noreply.github.com"
NAME = "deid"
PACKAGE_URL = "https://github.com/pydicom/deid"
KEYWORDS = "open source, python, anonymize, dicom"
DESCRIPTION = "best effort deidentify dicom with python and pydicom"
LICENSE = "LICENSE"

INSTALL_REQUIRES = (
    ("matplotlib", {"min_version": None}),
    ("numpy", {"min_version": "1.20"}),
    ("pydicom", {"min_version": "2.2.2"}),
    ("python-dateutil", {"min_version": None}),
)
