__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2025, Vanessa Sochat"
__license__ = "MIT"

import re
from collections import defaultdict
from functools import cache

from pydicom import FileDataset
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
        Use whole_string to match the entire string exactly (True),
        or partially (False).
        Use re to search a field for a regular expression, meaning
        the name, the keyword (nested) or the string tag.
        name.lower: includes nested keywords (e.g., Sequence_Child)
        self.element.name: is the human friendly name "Sequence Child"
        self.element.keyword: is the name without nesting "Child"
        Usage example: if the object contains PatientName then the
        following expressions will return True:
        - Patient's Name (tag name)
        - patient's name (lowercase tag name)
        - PatientName (tag keyword)
        - PatientN (tag keyword partial match, with whole_string=False)
        - (0010,0010) (parentheses-enclosed, comma-separated group, element)
        - 00100010 (stripped group, element)

        Usage examples for private tags:
        - Standard hex format: 0033101E
        - Parentheses format: (0033,101E)
        - Private creator syntax (stripped): 0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E
        - Private creator syntax (parentheses): (0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)

        Private tag syntax format:
        - GROUP: 4-digit hexadecimal group number
        - PRIVATE_CREATOR: Private creator string in double quotes
        - ELEMENT_OFFSET: 2-digit hexadecimal element number (last 8 bits of full element)
        """
        if isinstance(expression, str):
            expression = re.compile(expression, re.IGNORECASE)

        if (
            expression.search(self.name.lower())
            or expression.search(
                f"({self.element.tag.group:04X},{self.element.tag.element:04X})".lower()
            )
            or expression.search(self.stripped_tag)
            or expression.search(self.element.name)
            or expression.search(self.element.keyword)
        ):
            return True

        if self.element.is_private and (self.element.private_creator is not None):
            # Handle private tag syntax matching
            # Private tags can be referenced using two formats:
            # 1. Stripped format: GROUP,"PRIVATE_CREATOR",ELEMENT_OFFSET
            #    Example: 0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E
            # 2. Parentheses format: (GROUP,"PRIVATE_CREATOR",ELEMENT_OFFSET)
            #    Example: (0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)
            #
            # The GROUP is the 4-digit hex group number (e.g., 0033)
            # The PRIVATE_CREATOR is the private creator string in quotes
            # The ELEMENT_OFFSET is the 2-digit hex element number (masked to last 8 bits)
            stripped_private_tag = f'{self.element.tag.group:04X},"{self.element.private_creator}",{(self.element.tag.element & 0xFF):02X}'
            private_tag = "(" + stripped_private_tag + ")"
            if re.search(expression, stripped_private_tag) or re.search(
                expression, private_tag
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
        contenders = get_fields_with_lookup(dicom)

    # Case 1: field is an expander without an argument (e.g., no :)
    if field.lower() in expanders:
        if field.lower() == "all":
            fields = contenders.fields
        return fields

    # Case 2: The field is a specific field OR an expander with argument (A:B)
    fields = field.split(":", 1)
    if len(fields) == 1:
        return {field.uid: field for field in contenders.get_exact_matches(fields[0])}

    # if we get down here, we have an expander and expression
    expander, expression = fields
    expression = expression.lower()
    fields = {}

    # Derive expression based on field expander
    if expander.lower() == "endswith":
        expression = "(%s)$" % expression
    elif expander.lower() == "startswith":
        expression = "^(%s)" % expression

    expression_re = None
    # Loop through fields, all are strings STOPPED HERE NEED TO ADDRESS EMPTY NAME
    for uid, field in contenders.items():
        if isinstance(field, str) and string_matches_expander(
            expander, expression, field
        ):
            fields[uid] = field
        elif isinstance(field, DicomField) and field_matches_expander(
            expander, expression, expression_re, field
        ):
            fields[uid] = field

    return fields


def string_matches_expander(expander, expression_string, string):
    """
    Check if a string matches an expression for a given expander operator.
    """
    if expander.lower() in ["endswith", "startswith", "contains"]:
        return expression_string in string

    elif expander.lower() == "except":
        return expression_string not in string

    # Note: "select" expanders are not applicable to string values, as
    # they do not have any attributes.
    return False


def field_matches_expander(expander, expression_string, expression_re, field):
    """
    Check if a field matches an expression for a given expander operator.

    The `expression_re` argument is an optional arg that can be used to cache
    the compiled regex for re-use in later invocations.
    """
    # Apply expander to string for name OR to tag string
    if expander.lower() == "select":
        return field.select_matches(expression_string)

    if expression_re is None:
        expression_re = re.compile(expression_string, re.IGNORECASE)

    if expander.lower() in ["endswith", "startswith", "contains"]:
        return field.name_contains(expression_re)

    elif expander.lower() == "except":
        return not field.name_contains(expression_re)

    return False


# NOTE: this hashing function is required to enable caching on
# `get_fields_inner`. While it is not ideal to override the hashing
# behavior of the PyDicom FileDataset class, it appears to be the
# only way to enable the use of caching without incurring significant
# performance overhead. Note that adding a proxy class around this
# decreases performance substantially (50% slowdown measured).
FileDataset.__hash__ = lambda self: id(self)


class FieldsWithLookups:
    """
    This class is a wrapper around a dictionary of DicomField objects keyed by uid,
    with some supplemental lookup tables to enable rapid field lookup.
    """

    def __init__(self, fields):
        self.fields = fields

        self.lookup_tables = {
            "name": defaultdict(list),
            "tag": defaultdict(list),
            "stripped_tag": defaultdict(list),
            "element_name": defaultdict(list),
            "element_keyword": defaultdict(list),
        }
        for uid, field in fields.items():
            self._add_field_to_lookup(field)

    def get_exact_matches(self, field):
        """
        Get exact matches for a field name or tag.

        Returns a list of DicomField objects.
        """
        exact_match_contenders = (
            self.lookup_tables["name"][field]
            + self.lookup_tables["tag"][field]
            + self.lookup_tables["stripped_tag"][field]
            + self.lookup_tables["element_name"][field]
            + self.lookup_tables["element_keyword"][field]
        )
        return exact_match_contenders

    def __getitem__(self, key):
        return self.fields[key]

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __iter__(self):
        return iter(self.fields)

    def items(self):
        return self.fields.items()

    def values(self):
        return self.fields.values()

    def add(self, uid, field):
        self.fields[uid] = field
        self._add_field_to_lookup(field)

    def _get_field_lookup_keys(self, field):
        if not isinstance(field, DicomField):
            self.lookup_tables["name"][field].append(field)
            return {"name": [field]}
        lookup_keys = {}
        if field.name:
            lookup_keys["name"] = [field.name]
        if field.tag:
            lookup_keys["tag"] = [field.tag]
        if field.stripped_tag:
            lookup_keys["stripped_tag"] = [field.stripped_tag]
        if field.element.name:
            lookup_keys["element_name"] = [field.element.name]
        if field.element.keyword:
            lookup_keys["element_keyword"] = [field.element.keyword]
        if field.element.is_private:
            lookup_keys["name"] = lookup_keys.get("name", []) + [
                f'({field.element.tag.group:04X},"{field.element.private_creator}",{(field.element.tag.element & 0x00FF):02X})',
                f'{field.element.tag.group:04X},"{field.element.private_creator}",{(field.element.tag.element & 0x00FF):02X}',
            ]
        return lookup_keys

    def _add_field_to_lookup(self, field):
        for table_name, lookup_keys in self._get_field_lookup_keys(field).items():
            for key in lookup_keys:
                self.lookup_tables[table_name][key].append(field)

    def remove(self, uid):
        if uid in self.fields:
            field = self.fields[uid]
            del self.fields[uid]
            for table_name, lookup_keys in self._get_field_lookup_keys(field).items():
                for key in lookup_keys:
                    if field in self.lookup_tables[table_name][key]:
                        self.lookup_tables[table_name][key].remove(field)
                        if not self.lookup_tables[table_name][key]:
                            del self.lookup_tables[table_name][key]


def get_fields_with_lookup(dicom, skip=None, expand_sequences=True, seen=None):
    """Expand all dicom fields into a list, along with lookup tables keyed on
    different field properties.

    Each entry is a DicomField. If we find a sequence, we unwrap it and
    represent the location with the name (e.g., Sequence__Child)
    """
    fields, new_seen, new_skip = _get_fields_inner(
        dicom,
        skip=tuple(skip) if skip else None,
        expand_sequences=expand_sequences,
        seen=tuple(seen) if seen else None,
    )
    skip = new_skip
    seen = new_seen
    return FieldsWithLookups(fields)


@cache
def _get_fields_inner(dicom, skip=None, expand_sequences=True, seen=None):
    skip = list(skip) if skip else []
    seen = list(seen) if seen else []
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

    return fields, seen, skip
