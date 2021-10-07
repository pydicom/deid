"""

Copyright (c) 2017-2021 Vanessa Sochat

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

from deid.logger import bot
from pydicom.tag import tag_in_exception
from pydicom.sequence import Sequence
from pydicom._dicom_dict import DicomDictionary, RepeatersDictionary
from pydicom.tag import Tag
import re

################################################################################
# Functions for Finding / Getting Tags
################################################################################


def add_tag(identifier, VR="ST", VM=None, name=None, keyword=None):
    """Add tag will take a string for a tag (e.g., ) and define a new tag for it.
    By default, we give the type "Short Text."
    """
    tag = Tag("0x" + identifier)
    manifest = {
        "tag": tag,
        "VR": VR,
        "VM": VM,
        "keyword": keyword,
        "name": name,
    }
    return manifest


def get_tag(field):
    """get_tag will return a dictionary with tag indexed by field. For each entry,
    a dictionary lookup is included with VR.

    Parameters
    ==========
    field: the keyword to get tag for, eg "PatientIdentityRemoved"

    """
    found = [
        {key: value} for key, value in DicomDictionary.items() if value[4] == field
    ]
    manifest = None

    if len(found) > 0:

        # (VR, VM, Name, Retired, Keyword
        found = found[0]  # shouldn't ever have length > 1
        tag = Tag(list(found)[0])
        VR, VM, longName, _, keyword = found[tag]

        manifest = {
            "tag": tag,
            "VR": VR,
            "VM": VM,
            "keyword": keyword,
            "name": longName,
        }

    return manifest


def find_tag(term, VR=None, VM=None, retired=False):
    """find_tag will search over tags in the DicomDictionary and return the tags found
    to match some term.
    """
    searchin = DicomDictionary
    if retired:
        searchin = RepeatersDictionary

    found = [
        value
        for key, value in searchin.items()
        if re.search(term, value[4]) or re.search(term, value[2])
    ]

    # Filter by VR, VM, name, these are exact
    if VR is not None:
        found = _filter_tags(found, 0, VR)
    if VM is not None:
        found = _filter_tags(found, 1, VM)
    return found


def _filter_tags(tags, idx, fields=None):
    """filter tags is a helper function to take some list of tags in the format
    [ (VR, VM, longname, retired, keyword).. ]
    where each of the items above has some index, idx, and filter that index
    down to what is provided in fields.
    """
    if not isinstance(fields, list):
        fields = [fields]
    return [x for x in tags if x[idx] in fields]


################################################################################
# Manipulating Tags in Data
################################################################################


def remove_sequences(dicom):
    """remove sequences from a dicom by removing the associated tag.
    We use dicom.iterall() to get all nested sequences.

    Parameters
    ==========
    dicom: the loaded dicom to remove sequences
    """
    for elem in dicom.iterall():
        if isinstance(elem.value, Sequence) and dicom.get(elem.tag) != None:
            del dicom[elem.tag]
    return dicom


def update_tag(dicom, field, value):
    """update tag will update a value in the header, if it exists
    if not, nothing is added. This check is the only difference
    between this function and change_tag.
    If the user wants to add a value (that might not exist)
    the function add_tag should be used with a private identifier
    as a string.

    Parameters
    ==========
    dicom: the pydicom.dataset Dataset (pydicom.read_file)
    field: the name of the field to update
    value: the value to set, if name is a valid tag

    """
    if field not in dicom:
        return dicom

    # Case 1: Dealing with a string tag (field name)
    if isinstance(field, str):
        tag = get_tag(field)
        if tag:
            dicom.add_new(tag["tag"], tag["VR"], value)
        else:
            bot.error("%s is not a valid field to add. Skipping." % (field))

    # Case 2: we already have a tag for the field name (type BaseTag)
    else:
        tag = dicom.get(field)
        dicom.add_new(field, tag.VR, value)

    return dicom


#########################################################################
# Private Tags
#########################################################################


def get_private(dicom):
    """get private tags

    Parameters
    ==========
    dicom: the pydicom.dataset Dataset (pydicom.read_file)
    """
    datasets = [dicom]
    private_tags = []
    while len(datasets) > 0:
        ds = datasets.pop(0)
        taglist = sorted(ds.keys())
        for tag in taglist:
            with tag_in_exception(tag):
                if tag in ds:
                    try:
                        data_element = ds[tag]
                        if data_element.tag.is_private:
                            bot.debug(data_element.name)
                            private_tags.append(data_element)
                            if tag in ds and data_element.VR == "SQ":
                                sequence = data_element.value
                                for dataset in sequence:
                                    datasets.append(dataset)
                    except IndexError:
                        bot.debug("tag %s key present without value" % tag)
                    except NotImplementedError:
                        bot.debug("tag %s is invalid, skipping" % tag)
    return private_tags


def has_private(dicom):
    """has_private will return True if the header has private tags

    Parameters
    ==========
    dicom: the pydicom.dataset Dataset (pydicom.read_file)

    """
    private_tags = len(get_private(dicom))
    print("Found %s private tags" % private_tags)
    if private_tags > 0:
        return True
    return False
