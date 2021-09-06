#!/usr/bin/env python

"""
Copyright (c) 2016-2021 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


def create_recipe(actions, fields=None, values=None):
    """helper method to create a recipe file"""
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
    """helper function to load a dicom"""
    from deid.dicom import get_files
    from pydicom import read_file

    dicom_files = get_files(dataset)
    return read_file(next(dicom_files))


def get_file(dataset):
    """helper to get a dicom file"""
    from deid.dicom import get_files

    dicom_files = get_files(dataset)
    return next(dicom_files)
