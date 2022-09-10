__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

"""
Simple loading functions for datasets

   from deid.data import get_dataset
"""


import os

from deid.logger import bot
from deid.utils import get_installdir

data_base = os.path.dirname(os.path.abspath(__file__))


def get_dataset(dataset=None):
    """
    Get a dataset by name.

    get_dataset will return some data provided by the application,
    based on a user-provided label. In the future, we can add https endpoints
    to retrieve online datasets.
    """
    data_base = get_installdir()
    valid_datasets = {
        "dicom-cookies": os.path.join(data_base, "data", "dicom-cookies"),
        "animals": os.path.join(data_base, "data", "animals"),
        "humans": os.path.join(data_base, "data", "humans"),
        "ultrasounds": os.path.join(data_base, "data", "ultrasounds"),
    }

    if dataset is not None:
        # In case the user gave an extension
        dataset = os.path.splitext(dataset)[0].lower()
        if dataset in valid_datasets:
            return valid_datasets[dataset]

    bot.info("Valid datasets include: %s" % (",".join(list(valid_datasets.keys()))))
