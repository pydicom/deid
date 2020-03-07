"""

groups: functions to derive groups of fields or values

Copyright (c) 2020 Vanessa Sochat

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
from .tags import remove_sequences
from .fields import get_fields, expand_field_expression

import os


def extract_values_list(dicom, actions):
    """Given a list of actions for a named group (a list) extract values from
       the dicom based on the list of actions provided. This function
       always returns a list intended to update some lookup to be used
       to further process the dicom.
    """
    values = []
    fields = get_fields(dicom)
    for action in actions:

        # Just grab the entire value string for a field, no parsing
        if action["action"] == "FIELD":
            subset = expand_field_expression(
                field=action["field"], dicom=dicom, contenders=fields
            )
            [values.append(dicom.get(field)) for field in subset]

        # Split action, can optionally have a "by" and/or minlength parameter
        elif action["action"] == "SPLIT":
            subset = expand_field_expression(
                field=action["field"], dicom=dicom, contenders=fields
            )

            # Default values for split are length 1 and character empty space
            bot.debug("Parsing action %s" % action)
            split_by = " "
            minlength = 1

            if "value" in action:
                for param in action["value"].split(";"):
                    param_name, param_val = param.split("=")

                    # Set a custom parameter legnth
                    if param_name == "minlength":
                        minlength = int(param_val)
                        bot.debug("Minimum length set to %s" % minlength)
                    elif param_name == "by":
                        split_by = param_val.strip("'").strip('"')
                        bot.debug("Splitting value set to %s" % split_by)

            for field in subset:
                new_values = dicom.get(field, "").split(split_by)
                for new_value in new_values:
                    if len(new_value) > minlength:
                        values.append(new_value)

        else:
            bot.warning(
                "Unrecognized action %s for values list extraction." % action["action"]
            )

    return values


def extract_fields_list(dicom, actions):
    """Given a list of actions for a named group (a list) extract values from
       the dicom based on the list of actions provided. This function
       always returns a list intended to update some lookup to be used
       to further process the dicom.
    """
    subset = []
    fields = get_fields(dicom)
    for action in actions:

        if action["action"] == "FIELD":
            subset += expand_field_expression(
                field=action["field"], dicom=dicom, contenders=fields
            )

        else:
            bot.warning(
                "Unrecognized action %s for fields list extraction." % action["action"]
            )
    return subset
