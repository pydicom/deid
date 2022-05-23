"""

Copyright (c) 2022 Vanessa Sochat

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

from deid.utils import parse_keyvalue_pairs
from pydicom.uid import generate_uid as pydicom_generate_uid
from deid.logger import bot
import uuid


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
