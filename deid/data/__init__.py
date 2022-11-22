__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import os

data_base = os.path.abspath(os.path.dirname(__file__))


def get_dataset(dataset=None):
    """
    Get a dataset by name.

    get_dataset will return some data provided by the application,
    based on a user-provided label. In the future, we can add https endpoints
    to retrieve online datasets.
    """
    try:
        from deid_data import data
    except ImportError:
        raise ValueError("install deid data with `pip install deid-data`")

    return data.get_dataset(dataset)
