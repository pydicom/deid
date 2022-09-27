__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

from typing import Union

from pydicom import FileDataset

DcmOrStr = Union[str, FileDataset]
