"""

Copyright (c) 2018-2021 Vanessa Sochat

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
import dateutil.parser
from datetime import timedelta, datetime
import re


def parse_value(dicom, value, item=None, field=None):
    """parse_value will parse the value field of an action,
    either returning:
        1. the string (string or from function)
        2. a variable looked up (var:FieldName)
    """
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


def get_func(function_name):
    """get_func will return a function that is defined from a string.
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
    """get_timestamp will return (default) a UTC timestamp
    with some date and (optional) time. A different format can be
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
