#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"


def create_recipe(actions, fields=None, values=None):
    """
    Helper method to create a recipe file
    """
    from deid.config import DeidRecipe

    recipe = DeidRecipe()

    # .clear() only supported Python 3.3 and after
    del recipe.deid["header"][:]
    recipe.deid["header"] = actions

    if fields is not None:
        recipe.deid["fields"] = fields

    if values is not None:
        recipe.deid["values"] = values

    return recipe


def get_dicom(dataset):
    """
    helper function to load a dicom
    """
    from pydicom import read_file

    from deid.dicom import get_files

    dicom_files = get_files(dataset)
    return read_file(next(dicom_files))


def get_same_file(dataset):
    """
    get a consistent dicom file
    """
    from deid.dicom import get_files

    dicom_files = list(get_files(dataset))
    return dicom_files[0]


def get_file(dataset):
    """
    get a dicom file
    """
    from deid.dicom import get_files

    dicom_files = get_files(dataset)
    return next(dicom_files)
