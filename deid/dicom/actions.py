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
from deid.dicom.tags import update_tag
from deid.utils import get_timestamp

import re


# Timestamps


def jitter_timestamp(dicom, field, value):
    """if present, jitter a timestamp in dicom
       field "field" by number of days specified by "value"
       The value can be positive or negative.
 
       Parameters
       ==========
       dicom: the pydicom Dataset
       field: the field with the timestamp
       value: number of days to jitter by. Jitter bug!

    """
    if not isinstance(value, int):
        value = int(value)

    original = dicom.get(field)

    if original is not None:

        # Create default for new value
        new_value = None

        # If we have a string, we need to create a DataElement
        if isinstance(field, str):
            dcmvr = dicom.data_element(field).VR
        else:
            dcmvr = dicom.get(field).VR
            original = dicom.get(field).value

        # DICOM Value Representation can be either DA (Date) DT (Timestamp),
        # or something else, which is not supported.

        if dcmvr == "DA":
            # NEMA-compliant format for DICOM date is YYYYMMDD
            new_value = get_timestamp(original, jitter_days=value, format="%Y%m%d")

        elif dcmvr == "DT":
            # NEMA-compliant format for DICOM timestamp is
            # YYYYMMDDHHMMSS.FFFFFF&ZZXX
            try:
                new_value = get_timestamp(
                    original, jitter_days=value, format="%Y%m%d%H%M%S.%f%z"
                )
            except:
                new_value = get_timestamp(
                    original, jitter_days=value, format="%Y%m%d%H%M%S.%f"
                )

        else:
            # Do nothing and issue a warning.
            bot.warning("JITTER not supported for %s with VR=%s" % (field, dcmvr))

        if new_value is not None and new_value != original:

            # Only update if there's something to update AND there's been change
            dicom = update_tag(dicom, field=field, value=new_value)

    return dicom
