'''
clean.py: tasks for data structure based on a deid specification

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


from deid.logger import bot
from deid.identifiers.actions import perform_action

import os
import pickle
import re
import sys
import tempfile
import dateutil.parser

from deid.config import (
    get_deid,
    load_combined_deid
)

# Checking

def check_item(item):
    '''print item fields and values to screen
    '''
    for key,val in item.items():
        bot.info("%s: %s" %(key,val))

# Cleaning

def _clean_item(item, deid, default="KEEP"):
    '''clean a single item according to a deid specification.
    This function is expected to be called from clean_identifiers
    below

    Parameters
    ==========
    item: the item dictionary to clean
    deid: the already loaded deid, with a header section with 
          actions to specify how to clean
    '''

    # Keep track of the fields we've seen, not to blank them
    seen = []
    for action in deid['header']:
        item,fields = perform_action(item=item,
                                     action=action,
                                     return_seen=True)
        seen = seen + [f for f in fields if f not in seen]
    remaining = [x for x in item.keys() if x not in seen]

    # Apply default action to remaining fields
    if len(remaining) > 0 and default != "KEEP":
        bot.debug("%s fields set for default action %s" %(len(remaining),default))
        for field in remaining:
            action = {'action': default, "field":field}
            item = perform_action(item=item, action=action)
    return item



def clean_identifiers(ids, deid=None, default="KEEP"):
    '''clean identifiers will take a dictionary of entity, with key as entity id,
    and value another dictionary of items, with key the item id, and value a dict
    of key:value pairs. eg:
    
    ids['111111']['2.2.222.2222']
       {'key1': 'value1', 'key2': 'value2', .... 'keyN': 'valueN'} 
 
    and use a deid provided to replace identifiers in this data. 
    Once variables are replaced, they are substituted back in ids.    
    Typically, the next step is to replace some data back into image headers
    with dicom.replace_identifiers, or upload this data to a database
    '''
    # if the user has provided a custom deid, load it
    # if the user has provided a custom deid, load it
    if deid is None:
        deid = 'dicom'
    deid = get_deid(deid, load=True)

    # Generate ids dictionary for data put (replace_identifiers) function
    cleaned = dict()
    for item_id, item in ids.items():
        cleaned[item_id] = _clean_item(item=item,
                                       deid=deid,
                                       default=default)
    return cleaned
