'''
clean.py: clean data structure based on a deid specification

Copyright (c) 2017 Vanessa Sochat

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

from deid.config import load_deid
from deid.data import get_deid


def clean_item(item, deid, default="KEEP"):
    '''clean a single item according to a deid specification.
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
    if len(remaining) > 0:
        bot.warning("%s fields set for default action %s" %(len(remaining),default))
        bot.debug(",".join(remaining))
        for field in remaining:
            action = {'action': default, "field":field}
            item = perform_action(item=item, action=action)
    return item


def clean_identifiers(ids, deid, default="KEEP"):
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
    if not isinstance(deid,dict):
        deid = load_deid(deid)
    # Generate ids dictionary for data put (replace_identifiers) function
    cleaned = dict()
    for entity, items in ids.items():
        cleaned[entity] = dict()
        item_ids=list(items.keys())
        for item_id in item_ids:
            item = items[item_id]
            cleaned[entity][item_id] = clean_item(item=item,
                                                  deid=deid,
                                                  default=default)
    return cleaned
