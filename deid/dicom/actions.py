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
from deid.config.standards import actions as valid_actions

from .fields import expand_field_expression

from deid.utils import get_timestamp, parse_value

from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from .tags import add_tag, update_tag, blank_tag, remove_tag

import re

# Actions


def perform_action(dicom, action, item=None, fields=None, return_seen=False):
    """perform action takes  

       Parameters
       ==========
       dicom: a loaded dicom file (pydicom read_file)
       item: a dictionary with keys as fields, values as values
       fields: if provided, a filtered list of fields for expand
       action: the action from the parsed deid to take
          "deid" (eg, PatientID) the header field to process
          "action" (eg, REPLACE) what to do with the field
          "value": if needed, the field from the response to replace with
    """
    field = action.get("field")  # e.g: PatientID, endswith:ID
    value = action.get("value")  # "suid" or "var:field"
    action = action.get("action")  # "REPLACE"

    # Validate the action
    if action not in valid_actions:
        bot.warning("%s in not a valid choice. Defaulting to blanked." % action)
        action = "BLANK"

    # If there is an expander applied to field, we iterate over
    fields = expand_field_expression(field=field, dicom=dicom, contenders=fields)

    # Keep track of fields we have seen
    seen = []

    # An expanded field must END with that field
    expanded_regexp = "__%s$" % field

    for field in fields:
        seen.append(field)

        # Handle top level field
        _perform_action(dicom=dicom, field=field, item=item, action=action, value=value)

    # Expand sequences
    if item:
        expanded_fields = [x for x in item if re.search(expanded_regexp, x)]

        # FieldA__FieldB
        for expanded_field in expanded_fields:
            _perform_expanded_action(
                dicom=dicom,
                expanded_field=expanded_field,
                item=item,
                action=action,
                value=value,
            )

    if return_seen:
        return dicom, seen
    return dicom


def _perform_action(dicom, field, action, value=None, item=None):
    """_perform_action is the base function for performing an action.
       perform_action (above) typically is called using a loaded deid,
       and perform_addition is typically done via an addition in a config
       Both result in a call to this function. If an action fails or is not
       done, None is returned, and the calling function should handle this.
    """
    if field in dicom and action != "ADD":

        # Blank the value
        if action == "BLANK":
            dicom = blank_tag(dicom, field)

        # Code the value with something in the response
        elif action == "REPLACE":

            value = parse_value(item, value, field)
            if value is not None:
                # If we make it here, do the replacement
                dicom = update_tag(dicom, field=field, value=value)
            else:
                bot.warning("REPLACE %s unsuccessful" % field)

        # Code the value with something in the response
        elif action == "JITTER":
            value = parse_value(item, value, field)
            if value is not None:

                # Jitter the field by the supplied value
                dicom = jitter_timestamp(dicom=dicom, field=field, value=value)
            else:
                bot.warning("JITTER %s unsuccessful" % field)

        # elif "KEEP" --> Do nothing. Keep the original

        # Remove the field entirely
        elif action == "REMOVE":
            dicom = remove_tag(dicom, field)

    elif action == "ADD":
        value = parse_value(item, value, field)
        if value is not None:
            dicom = add_tag(dicom, field, value, quiet=True)


def _perform_expanded_action(dicom, expanded_field, action, value=None, item=None):
    """akin to _perform_action, but we expect to be dealing with an expanded
       sequence, and need to step into the Dicom data structure. 

       Add, jitter, and delete are currently not supported.

       The field is expected to have the format FieldA__FieldB where the
       last one is where we want to do the replacement.
    """
    field = expanded_field.split("__")[-1]

    while field != expanded_field:
        next_field, expanded_field = expanded_field.split("__", 1)

        # Case 1: we have a Dataset
        if isinstance(dicom, Dataset):
            dicom = dicom.get(next_field)

        elif isinstance(dicom, Sequence):
            for sequence in dicom:
                for subitem in sequence:
                    if subitem.keyword == next_field:
                        dicom = subitem
                        break

    # Field should be equal to expanded_field, and in dicom
    if isinstance(dicom, Dataset):
        return _perform_action(
            dicom=dicom, field=field, item=item, action=action, value=value
        )

    elif isinstance(dicom, Sequence):
        for sequence in dicom:
            for subitem in sequence:
                if subitem.keyword == field:
                    dicom = subitem
                    break

    if not dicom:
        return

    # Not sure if this is possible
    if dicom.keyword != field:
        bot.warning("Early return, looking for %s, found %s" % (field, dicom.keyword))
        return

    # Blank the value
    if action == "BLANK":
        if dicom.VR not in ["US", "SS"]:
            dicom.value = ""

    # Code the value with something in the response
    elif action == "REPLACE":

        value = parse_value(item, value, field)
        if value is not None:
            dicom.value = value

    # elif "KEEP" --> Do nothing. Keep the original


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

    original = dicom.get(field, None)

    if original is not None:
        dcmvr = dicom.data_element(field).VR

        # DICOM Value Representation can be either DA (Date) DT (Timestamp),
        # or something else, which is not supported.

        if dcmvr == "DA":
            # NEMA-compliant format for DICOM date is YYYYMMDD
            new_value = get_timestamp(original, jitter_days=value, format="%Y%m%d")

        elif dcmvr == "DT":
            # NEMA-compliant format for DICOM timestamp is
            # YYYYMMDDHHMMSS.FFFFFF&ZZXX
            new_value = get_timestamp(
                original, jitter_days=value, format="%Y%m%d%H%M%S.%f%z"
            )
        else:
            # Do nothing and issue a warning.
            new_value = None
            bot.warning("JITTER not supported for %s with VR=%s" % (field, dcmvr))
        if new_value is not None and new_value != original:
            # Only update if there's something to update AND there's been change
            dicom = update_tag(dicom, field=field, value=new_value)
    return dicom
