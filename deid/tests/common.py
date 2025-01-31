#!/usr/bin/env python

from deid.config import DeidRecipe
from deid.dicom import get_files, utils


def create_recipe(actions, fields=None, values=None):
    """
    Helper method to create a recipe file
    """
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
    dicom_files = get_files(dataset)
    return utils.dcmread(next(dicom_files))


def get_same_file(dataset):
    """
    get a consistent dicom file
    """
    dicom_files = list(get_files(dataset))
    return dicom_files[0]


def get_file(dataset):
    """
    get a dicom file
    """
    dicom_files = get_files(dataset)
    return next(dicom_files)
