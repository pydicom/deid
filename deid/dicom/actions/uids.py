__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import uuid

from pydicom.uid import generate_uid as pydicom_generate_uid

from deid.logger import bot
from deid.utils import parse_keyvalue_pairs


def basic_uuid(item, value, field, **kwargs):
    """A basic function to replace a field with a uuid.uuid4() string"""
    return str(uuid.uuid4())


def pydicom_uuid(item, value, field, **kwargs):
    """
    Use pydicom to generate the UID. Optional kwargs include:

    prefix (str): provide a custom prefix
    stable_remapping (bool): if true, use the orignal value for entropy.
    This ensures stability across different runs that use the same UID.

    The prefix must match '^(0|[1-9][0-9]*)(\\.(0|[1-9][0-9]*))*\\.$'
    """
    opts = parse_keyvalue_pairs(kwargs.get("extras"))

    # We always provide a prefix so the stable remapping is done
    prefix = opts.get("prefix", "2.25.")
    stable_remapping = opts.get("stable_remapping", True)
    entropy_srcs = []

    # They would need to unset the default prefix
    if stable_remapping is True and not prefix:
        bot.warning("A prefix must be provided to use stable remapping.")

    if stable_remapping is True:
        original = str(field.element.value)
        entropy_srcs.append(original)
    return pydicom_generate_uid(prefix=prefix, entropy_srcs=entropy_srcs)


def suffix_uuid(item, value, field, **kwargs):
    """Return the same field, with a uuid suffix.

    Provided in docs: https://pydicom.github.io/deid/examples/func-replace/
    """
    # a field can either be just the name string, or a DicomElement
    if hasattr(field, "name"):
        field = field.name
    prefix = field.lower().replace(" ", " ")
    return prefix + "-" + str(uuid.uuid4())


def dicom_uuid(item, value, field, dicom, **kwargs):
    """
    Generate a dicom uid that better conforms to the dicom standard.
    """
    # a field can either be just the name string, or a DicomElement
    if hasattr(field, "name"):
        field = field.name

    opts = parse_keyvalue_pairs(kwargs.get("extras"))
    org_root = opts.get("org_root", "anonymous-organization")

    bigint_uid = str(uuid.uuid4().int)
    full_uid = org_root + "." + bigint_uid

    # A DICOM UID is limited to 64 characters
    return full_uid[0:64]
