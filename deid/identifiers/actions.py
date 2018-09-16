'''
actions.py: perform general actions with an input data structure, and
            return a new output.

Copyright (c) 2017-2018 Vanessa Sochat

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
'''

from deid.config.standards import actions as valid_actions
from deid.identifiers.utils import expand_field_expression, to_int

from deid.logger import bot
from deid.utils import recursive_find
from deid.identifiers import get_timestamp
import tempfile
import os
import re
import sys



def perform_action(action, item, return_seen=False):
    '''perform action takes  
    :param item: a dictionary with keys as fields, values as values
    :param action: the action from the parsed deid to take
        "field" (eg, PatientID) the header field to process
        "action" (eg, REPLACE) what to do with the field
        "value": if needed, the field from the response to replace with
    '''
    field = action.get('field')   # e.g: PatientID, endswith:ID
    value = action.get('value')   # "suid" or "var:field"
    action = action.get('action') # "REPLACE"
  
    # Keep track of fields we have seen
    seen = []

    # If there is an expander applied to field, we iterate over
    fields = list(item.keys())
    fields = expand_field_expression(field=field,
                                     contenders=fields)
    for field in fields:
        seen.append(field)
        item = _perform_action(field=field,
                               item=item,
                               action=action,
                               value=value)
    if return_seen:
        return item,seen
    return item


def _perform_action(field,item,action,value=None):
    '''_perform_action is the base function for performing an action.
    It is equivalent to the dicom module version, except we work with
    dictionary field/value instead of dicom headers.
    If no action is done, None is returned
    '''    
    done = False
    if action not in valid_actions:
        bot.warning('%s in not a valid choice [%s]. Defaulting to blanked.' %(action,
                                                                              ".".join(valid_actions)))
        action = "BLANK"

    if field in item and action != "ADD":

        # Blank the value
        if action == "BLANK":
            item[field] = ""
            done = True

        # Code the value with something in the response
        elif action == "REPLACE":
            value = parse_value(item,value)
            if value is not None:
                done = True
                item[field] = value
            else:
                bot.warning("REPLACE failed for %s" %field)

        # Code the value with something in the response
        elif action == "JITTER":
            value = parse_value(item,value)
            if value is not None:
                done = True
                item = jitter_timestamp(field=field,
                                        value=value,
                                        item=item)
            else:
                bot.warning('JITTER failed for %s' %field)

        # Do nothing. Keep the original
        elif action == "KEEP":
            done = True
            bot.debug('KEEP %s' %field)

        # Remove the field entirely
        elif action == "REMOVE":
            del item[field]
            done = True
        if not done:            
            bot.warning("%s not done for %s" %(action,field))

    elif action == "ADD":
        value = parse_value(item,value)
        if value is not None:
            item[field] = value
        else:
            bot.warning('ADD failed for %s' %field)

    return item


def parse_value(item,value):
    '''parse_value will parse the value field of an action,
    either returning the string, or a variable looked up
    in the case of var:FieldName
    '''
    # Does the user want a custom value?
    if re.search('[:]',value):
        value_type,value_option = value.split(':') 
        if value_type.lower() == "var": 

            # If selected variable not provided, skip
            if value_option not in item:
                return None
            return item[value_option]
        bot.warning('%s is not a valid value type, skipping.' %(value_type))
        return None
    return value


# Timestamps
def jitter_timestamp(field,value,item):
    '''if present, jitter a timestamp in dicom
    field "field" by number of days specified by "value"
    The value can be positive or negative.
    '''
    value = to_int(value)
    original = item.get(field,None)
    if original is not None:
        jittered = get_timestamp(item_date=original,
                                 jitter_days=value,
                                 format="%Y%m%d")
        bot.debug("JITTER %s + (%s): %s" %(original,
                                           value,
                                           jittered))
        item[field] = jittered
    return item
