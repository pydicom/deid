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
import uuid


def basic_uuid(item, value, field, **kwargs):
    """A basic function to replace a field with a uuid.uuid4() string"""
    return str(uuid.uuid4())


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
