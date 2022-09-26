__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import re

from pydicom.dataelem import DataElement
from pydicom.dataset import Dataset, FileMetaDataset, RawDataElement
from pydicom.sequence import Sequence

from deid.logger import bot


class DicomField:
    """
    A dicom field.

    A dicom field holds the element, and a string that represents the entire
    nested structure (e.g., SequenceName__CodeValue).
    """

    def __init__(self, element, name, uid, is_filemeta=False):
        self.element = element
        self.name = name  # nested names (might not be unique)
        self.uid = uid  # unique id includes parent tags
        self.is_filemeta = is_filemeta

    def __str__(self):
        return "%s  [%s]" % (self.element, self.name)

    def __repr__(self):
        return self.__str__()

    @property
    def tag(self):
        """
        Return a string of the element tag.
        """
        return str(self.element.tag)

    @property
    def stripped_tag(self):
        """
        Return the stripped element tag
        """
        return re.sub("([(]|[)]|,| )", "", str(self.element.tag))

    # Contains

    def name_contains(self, expression):
        """
        Determine if a name contains a pattern or expression.

        Use re to search a field for a regular expression, meaning
        the name, the keyword (nested) or the string tag.

        name.lower: includes nested keywords (e.g., Sequence_Child)
        self.tag: is the string version of the tag
        self.element.name: is the human friendly name "Sequence Child"
        self.element.keyword: is the name without nesting "Child"
        """
        if (
            re.search(expression, self.name.lower())
            or re.search(expression, self.tag)
            or re.search(expression, self.stripped_tag)
            or re.search(expression, self.element.name)
            or re.search(expression, self.element.keyword)
        ):
            return True
        return False

    def value_contains(self, expression):
        """
        Use re to search a field value for a regular expression
        """
        values = self.element.value

        # If we are not dealing with a list
        if not isinstance(values, list):
            values = [values]

        values = [str(x) for x in values]

        for value in values:
            if re.search(expression, value, re.IGNORECASE):
                return True
        return False

    def select_matches(self, expression):
        """
        Determine whether the element has a specific selected attribute
        """
        attribute, value = expression.split(":", 1)
        attribute = attribute.upper()

        if attribute == "VR":
            value = value[0:2].upper()
            return self.element.VR == value

        elif attribute == "GROUP":
            value = int(value, 16)
            return self.element.tag.group == value

        return False


def extract_item(item, prefix=None, entry=None):
    """
    Extract values from a dicom sequence depending on the type.

    A helper function to extract sequence, will extract values from
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
    """
    Extract a sequence recursively.

    return a pydicom.sequence.Sequence recursively
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


def expand_field_expression(field, dicom, contenders=None):
    """
    Get a list of fields based on an expression.

    If no expression found, return single field. Options for fields include:

    endswith: filter to fields that end with the expression
    startswith: filter to fields that start with the expression
    contains: filter to fields that contain the expression
    select: filter based on DICOM element properties
    allfields: include all fields
    exceptfields: filter to all fields except those listed ( | separated)

    Returns: a list of DicomField objects
    """
    # Expanders that don't have a : must be checked for
    expanders = ["all"]

    # if no contenders provided, use top level of dicom headers
    if contenders is None:
        contenders = get_fields(dicom)

    # Case 1: field is an expander without an argument (e.g., no :)
    if field.lower() in expanders:
        if field.lower() == "all":
            fields = contenders
        return fields

    # Case 2: The field is a specific field OR an expander with argument (A:B)
    fields = field.split(":", 1)
    if len(fields) == 1:
        return {
            uid: field
            for uid, field in contenders.items()
            if field.name_contains("^" + fields[0] + "$")
        }

    # if we get down here, we have an expander and expression
    expander, expression = fields
    expression = expression.lower()
    fields = {}

    # Derive expression based on field expander
    if expander.lower() == "endswith":
        expression = "(%s)$" % expression
    elif expander.lower() == "startswith":
        expression = "^(%s)" % expression

    # Loop through fields, all are strings STOPPED HERE NEED TO ADDRESS EMPTY NAME
    for uid, field in contenders.items():

        # Apply expander to string for name OR to tag string
        if expander.lower() in ["endswith", "startswith", "contains"]:
            if field.name_contains(expression):
                fields[uid] = field

        elif expander.lower() == "except":
            if not field.name_contains(expression):
                fields[uid] = field

        elif expander.lower() == "select":
            if field.select_matches(expression):
                fields[uid] = field

    return fields


def get_fields(dicom, skip=None, expand_sequences=True, seen=None):
    """Expand all dicom fields into a list.

    Each entry is a DicomField. If we find a sequence, we unwrap it and
    represent the location with the name (e.g., Sequence__Child)
    """
    skip = skip or []
    seen = seen or []
    fields = {}  # indexed by nested tag

    if not isinstance(skip, list):
        skip = [skip]

    # Retrieve both dicom and file meta fields if dicom came from a file
    datasets = [d for d in [dicom, dicom.get("file_meta")] if d]

    def add_element(element, name, uid, is_filemeta):
        """
        Add an element to fields, but only if it has not been seen.

        The uid is derived from the tag (group, element) and includes
        nesting, so the "same" tag on different levels is considered
        different.
        """
        if uid not in seen:
            fields[uid] = DicomField(element, name, uid, is_filemeta)
            seen.append(uid)

    while datasets:

        # Grab the first dataset, usually just the dicom
        dataset = datasets.pop(0)

        # If the dataset does not have a prefix, we are at the start
        dataset.prefix = getattr(dataset, "prefix", None)
        dataset.uid = getattr(dataset, "uid", None)
        is_filemeta = isinstance(dataset, FileMetaDataset)

        # Includes private tags, sequences flattened, non-null values
        for contender in dataset:

            # All items should be data elements, skip based on keyword or tag
            if contender.keyword in skip or str(contender.tag) in skip:
                continue

            # The name represents nesting
            name = contender.keyword
            uid = str(contender.tag)

            if dataset.prefix is not None:
                name = "%s__%s" % (dataset.prefix, name)
            if dataset.uid is not None:
                uid = "%s__%s" % (dataset.uid, uid)

            # if it's a sequence, extract with prefix and index
            if isinstance(contender.value, Sequence) and expand_sequences is True:

                # Add the contender (usually type Dataset) to fields
                add_element(contender, name, uid, is_filemeta)

                # A nested dataset can be parsed as such
                for idx, item in enumerate(contender.value):
                    if isinstance(item, Dataset):
                        item.prefix = name
                        item.uid = uid + "__%s" % idx
                        datasets.append(item)

                    # A Raw data element we can add to our list
                    elif isinstance(item, DataElement):
                        name = "%s__%s" % (name, item.keyword)
                        uid = "%s__%s__%s" % (uid, str(item.tag), idx)
                        add_element(item, name, uid, is_filemeta)

            # A DataElement can be extracted as is
            elif isinstance(contender, DataElement):
                add_element(contender, name, uid, is_filemeta)

            else:
                bot.warning(
                    "Unrecognized type %s in extract sequences, skipping." % type(item)
                )

    return fields
