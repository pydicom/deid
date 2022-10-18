__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

"""
groups: functions to derive groups of fields or values
"""


from pydicom.multival import MultiValue

from deid.logger import bot

from .fields import expand_field_expression, get_fields


def extract_values_list(dicom, actions, fields=None):
    """Given a list of actions for a named group (a list) extract values from
    the dicom based on the list of actions provided. This function
    always returns a list intended to update some lookup to be used
    to further process the dicom.
    """
    values = set()

    # The function can be provided fields to save re-parsing
    if not fields:
        fields = get_fields(dicom)

    for action in actions:

        # Extract some subset of fields based on action
        subset = expand_field_expression(
            field=action["field"], dicom=dicom, contenders=fields
        )

        # Just grab the entire value string for a field, no parsing
        if action["action"] == "FIELD":
            for uid, field in subset.items():
                if field.element.value not in ["", None]:
                    if isinstance(field.element.value, MultiValue):
                        values.update(field.element.value)
                    else:
                        values.add(field.element.value)

        # Split action, can optionally have a "by" and/or minlength parameter
        elif action["action"] == "SPLIT":

            # Default values for split are length 1 and character empty space
            bot.debug("Parsing action %s" % action)
            split_by = " "
            minlength = 1

            if "value" in action:
                for param in action["value"].split(";"):
                    param_name, param_val = param.split("=")
                    param_name = param_name.strip()
                    param_val = param_val.strip()

                    # Set a custom parameter length
                    if param_name == "minlength":
                        minlength = int(param_val)
                        bot.debug("Minimum length set to %s" % minlength)
                    elif param_name == "by":
                        split_by = param_val.strip("'").strip('"')
                        bot.debug("Splitting value set to %s" % split_by)

            for uid, field in subset.items():
                new_values = (str(field.element.value) or "").split(split_by)
                for new_value in new_values:
                    if len(new_value) >= minlength:
                        values.add(new_value)

        else:
            bot.warning(
                "Unrecognized action %s for values list extraction." % action["action"]
            )

    return list(values)


def extract_fields_list(dicom, actions, fields=None):
    """Given a list of actions for a named group (a list) extract values from
    the dicom based on the list of actions provided. This function
    always returns a list intended to update some lookup to be used
    to further process the dicom.
    """
    subset = {}

    if not fields:
        fields = get_fields(dicom)

    for action in actions:

        if action["action"] == "FIELD":
            subset.update(
                expand_field_expression(
                    field=action["field"], dicom=dicom, contenders=fields
                )
            )

        else:
            bot.warning(
                "Unrecognized action %s for fields list extraction." % action["action"]
            )
    return subset
