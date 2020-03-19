"""

Copyright (c) 2017-2020 Vanessa Sochat

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
from deid.dicom.tags import get_private
from pydicom.sequence import Sequence
from pydicom.dataset import RawDataElement, Dataset
from pydicom.dataelem import DataElement
import re


def extract_item(item, prefix=None, entry=None):
    """a helper function to extract sequence, will extract values from 
       a dicom sequence depending on the type.

       Parameters
       ==========
       item: an item from a sequence.
    """
    # First call, we define entry to be a lookup dictionary
    if entry is None:
        entry = {}

    # Skip raw data elements
    if not isinstance(item, RawDataElement):
        header = item.keyword

        # If there is no header or field, we can't evaluate
        if header in [None, ""]:
            return entry

        if prefix is not None:
            header = "%s__%s" % (prefix, header)

        value = item.value
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, Sequence):
            return extract_sequence(value, prefix=header)

        entry[header] = value
    return entry


def extract_sequence(sequence, prefix=None):
    """return a pydicom.sequence.Sequence recursively
       as a flattened list of items. For example, a nested FieldA and FieldB
       would return as:

       {'FieldA__FieldB': '111111'}

       Parameters
       ==========
       sequence: the sequence to extract, should be pydicom.sequence.Sequence
       prefix: the parent name
    """
    items = {}
    for item in sequence:

        # If it's a Dataset, we need to further unwrap it
        if isinstance(item, Dataset):
            for subitem in item:
                items.update(extract_item(subitem, prefix=prefix))

        # Private tags are DataElements
        elif isinstance(item, DataElement):
            items[item.tag] = extract_item(item, prefix=prefix)

        else:
            bot.warning(
                "Unrecognized type %s in extract sequences, skipping." % type(item)
            )
    return items


def find_by_values(values, dicom):
    """Given a list of values, find fields in the dicom that contain any
       of those values, as determined by a regular expression search.
    """
    # Values must be strings
    values = [str(x) for x in values]

    fields = []

    # Includes private tags and values, if still part of dicom
    contenders = get_fields(dicom)

    # Create single regular expression to search by
    regexp = "(%s)" % "|".join(values)
    for field, value in contenders.items():
        if re.search(regexp, value, re.IGNORECASE):
            fields.append(field)

    return fields


def expand_field_expression(field, dicom, contenders=None):
    """Get a list of fields based on an expression. If 
       no expression found, return single field. Options for fields include:

        endswith: filter to fields that end with the expression
        startswith: filter to fields that start with the expression
        contains: filter to fields that contain the expression
        allfields: include all fields
        exceptfields: filter to all fields except those listed ( | separated)   
    """
    # Expanders that don't have a : must be checked for
    expanders = ["all"]

    # if no contenders provided, use all in dicom headers
    if contenders is None:
        contenders = dicom.dir()

    # Case 1: field is an expander without an argument (e.g., no :)
    if field.lower() in expanders:

        if field.lower() == "all":
            fields = contenders
        return fields

    # Case 2: The field is a specific field OR an expander with argument (A:B)
    fields = field.split(":", 1)
    if len(fields) == 1:
        return fields

    # if we get down here, we have an expander and expression
    expander, expression = fields
    expression = expression.lower()
    fields = []

    # Derive expression based on field expander
    if expander.lower() == "endswith":
        expression = "(%s)$" % expression
    elif expander.lower() == "startswith":
        expression = "^(%s)" % expression

    # Loop through fields, have special handling for private tags
    for field in contenders:
        field_name = field
        if not isinstance(field, str):
            field_name = str(field)

        # Apply expander to string for name, but add field to return (could be a tag)
        if expander.lower() in ["endswith", "startswith", "contains"]:
            if re.search(expression, field_name.lower()):
                fields.append(field)

        elif expander.lower() == "except":
            if not re.search(expression, field_name.lower()):
                fields.append(field)

    return fields


def dicom_dir(dicom):
    """Given a dicom file, return all fields (including private) if they
       are not removed. With private this might look like:

       ...
      'WindowCenterWidthExplanation',
      'WindowWidth',
      (0011, 0003),
      (0019, 0010),

      and both can be used as indices into the dicom (dicom.get(x))
    """
    # This becomes a list of strings and tags to be used as keys
    return dicom.dir() + [t.tag for t in get_private(dicom)]


def get_fields(dicom, skip=None, expand_sequences=True):
    """get fields is a simple function to extract a dictionary of fields
       (non empty) from a dicom file. This includes expanded sequenced,
       and parses private tag values as well, example below:

       'ViewPosition': 'AP',
       'WindowCenter': '2048',
       'WindowWidth': '4096',
       (0011, 0003): 'Agfa DR',      # private tags start here
       (0019, 0010): 'Agfa ADC NX',
       (0019, 1007): 'YES',

       Parameters
       ==========
       dicom: the dicom file to get fields for.
       skip: an optional list of fields to skip
       expand_sequences: if True, expand values that are sequences.
    """
    if skip is None:
        skip = []

    if not isinstance(skip, list):
        skip = [skip]

    fields = dict()

    # Includes private tags, if they are not removed
    contenders = dicom_dir(dicom)

    for contender in contenders:
        if contender in skip:
            continue

        try:
            value = dicom.get(contender)

            # Private tags will be DataElement types
            if isinstance(value, DataElement):
                fields[contender] = value.value

            # Adding expanded sequences
            elif isinstance(value, Sequence) and expand_sequences is True:
                fields.update(extract_sequence(value, prefix=contender))
            else:
                if value not in [None, ""]:
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    fields[contender] = str(value)
        except:
            # This gets triggered for PixelData
            pass

    return fields
