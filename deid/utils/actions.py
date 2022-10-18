__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import re
from datetime import datetime, timedelta

import dateutil.parser

from deid.logger import bot


def parse_value(dicom, value, item=None, field=None, funcs=None):
    """
    Parse_value will parse the value field of an action.

    This function returns either:
    1. the string (string or from function)
    2. a variable looked up (var:FieldName)
    """
    # custom function lookup
    funcs = funcs or {}

    # If item is passed as None
    if item is None:
        item = dict()

    # Does the user want a custom value?
    if re.search("[:]", value):
        value_type, value_option = value.split(":", 1)
        if value_type.lower() == "var":

            # If selected variable not provided, skip
            if value_option not in item:
                return None
            return item[value_option]

        # The user wants to use a deid provided function
        elif value_type.lower() == "deid_func":

            # There can be additional key=value pairs
            try:
                value_option, extras = value_option.split(" ", 1)
            except:
                extras = ""
                pass

            if value_option not in funcs:
                bot.warning("%s not a known deid provided function." % (value_option))
                return None

            print(extras)
            # item is the lookup, value from the recipe, and field
            # The field is an entire dicom element object
            return funcs[value_option](
                dicom=dicom, value=value, field=field, item=item, extras=extras
            )

        # The user is providing a specific function
        elif value_type.lower() == "func":

            if value_option not in item:
                bot.warning("%s not found in item lookup." % (value_option))
                return None

            # item is the lookup, value from the recipe, and field
            # The field is an entire dicom element object
            return item[value_option](dicom=dicom, value=value, field=field, item=item)

        bot.warning("%s is not a valid value type, skipping." % (value_type))
        return None
    return value


def parse_keyvalue_pairs(pairs):
    """
    Given a listing of extra arguments, parse into lookup dict.
    """
    values = {}
    if not pairs:
        return values
    for pair in pairs.split(" "):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        value = value.strip()

        # Ensure we convert booleans and none/null
        if value == "true":
            value = True
        if value == "false":
            value = False
        if value in ["none", "null"]:
            value = None
        values[key.strip()] = value
    return values


def get_func(function_name):
    """
    Get_func will return a function that is defined from a string.

    the function is assumed to be in this file

    Parameters
    ==========
    return a function from globals based on a name string
    """
    env = globals()
    if function_name in env:
        return env[function_name]
    return None


# Timestamps


def get_timestamp(item_date, item_time=None, jitter_days=None, format=None):
    """
    Get_timestamp will return (default) a UTC timestamp.

    This will have some date and (optional) time. A different format can be
    provided to change default behavior. eg: "%Y%m%d"
    """
    if format is None:
        format = "%Y-%m-%dT%H:%M:%SZ"

    if item_date in ["", None]:
        bot.warning("No date in header, cannot create timestamp.")
        return None

    item_time = item_time or ""

    try:
        timestamp = dateutil.parser.parse("%s%s" % (item_date, item_time))
    except (dateutil.parser.ParserError, OverflowError):
        timestamp = datetime.strptime("%s%s" % (item_date, item_time), format)

    if jitter_days is not None:
        jitter_days = int(float(jitter_days))
        timestamp = timestamp + timedelta(days=jitter_days)

    return timestamp.strftime(format)
