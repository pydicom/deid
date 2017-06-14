'''
utils.py: util functions for returning identifier objects

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

from .validators import (
    get_universal_source,
    validate_identifiers,
    validate_items,
    validate_item
)

import sys
import re
import os


def create_lookup(response,lookup_field=None):
    '''create_identifier_lookup will take a response, which should be a list
    of results (the API returns a "results" object, and the client 
    returns the list under "results". A lookup dictionary is returned,
    indexed by "id"
    '''
    if lookup_field is None:
        lookup_field = "id"

    if not isinstance(response,list):
        response = [response]

    lookup = dict()
    for entry in response:
        key = entry[lookup_field]
        if key in lookup:
            bot.warning("%s already in lookup, will use last in list." %(key))
        lookup[key] = entry
    return lookup


def create_identifier(entity_id,id_source,id_timestamp=None,items=None,
                      custom_fields=None,sources=None):
    '''create_identifier will return a json (dict) of required elements for an entity,
    a field to go under an identifier. The following is required:
    :param entity_id: mandatory key for uniquely identifying the entity (e.g. "1234567-8")
    :param id_source: mandatory issuer for the above id (e.g., "stanford")
    :param id_timestamp: when the id was looked up, to help with changed/merged ids (optional)
    :param custom_fields: not required, a dictionary of custom key pairs to include as data
    :param sources: a custom list of sources (eg, ['stanford']) to accept. If not defined, defaults
    are used
    :returns entity: an entity data structure, not wrapped, or None if not valid
    '''
    entity = {"id":entity_id,
              "id_source":id_source}

    # Custom fields and id_timestamp are optional
    if custom_fields != None:
        entity['custom_fields'] = custom_fields 

    if id_timestamp != None:
        entity["id_timestamp"] = id_timestamp

    if items != None:
        if not isinstance(items,list):
            items = [items]
        entity['items'] = items

    valid = validate_identifiers(identifiers=entity,
                                 sources=sources)
    if valid == True:
        return entity

    return None


def create_items(item_ids,id_sources,sources=None,custom_fields=None,verbose=False):
    '''create items is a wrapper for create items, taking in lists of item_id and id_source.
    if id_source is not a list, it's assumed to be equivalent for all items.
    :param item_ids: should be a list of items.
    :param id_sources: if a list is given, it must be equal in length to item ids. Otherwise,
    the common identifier (one term) is used for all items.
    :param custom_fields: not required, a list of dict of custom key pairs to include as data, or a single
    custom thing to use as data.
    :param sources: a custom list of sources (eg, ['stanford']) to accept. If not defined, defaults
    are used
    :param verbose: verbose is set to False, assuming we have multiple items! This will simply
    not print successful validations - errors are still printed for user.
    '''
    items = []

    # If item_ids is a string, assume one and put into list
    if not isinstance(item_ids,list):
        item_ids = [item_ids]    

    # If id_source is a list, must be equal in length to ids
    universal_source = get_universal_source(source=id_sources,
                                            comparator=item_ids)

    # If custom_fields is a list, must be equal in length to ids
    universal_field = get_universal_source(source=custom_fields,
                                           comparator=item_ids)

    # Iterate through items to return list of dict
    for i in range(len(item_ids)):

        # Do we have a shared item source?
        if universal_source != None:
            item_source = universal_source
        else:
            item_source = id_sources[i]

        # Do we have a shared custom_fields?
        if universal_field != None:
            item_field = universal_field
        else:
            item_field = custom_fields[i]

        item = create_item(item_id=item_ids[i],
                           id_source=item_source,
                           custom_fields=item_field,
                           sources=sources,
                           verbose=verbose)
    
        items.append(item)
    return items


def create_item(item_id,id_source,custom_fields,sources=None,verbose=True):
    '''create item will take input for an item, and return the item if it's valid
    :param item_id: the item id to store, mandatory
    :param id_source: mandatory issuer for the above id (e.g., "pacs")
    :param custom_fields: not required, a dictionary of custom key pairs to include as data
    :param id_timestamp: when the id was looked up, to help with changed/merged ids (optional)
    :param sources: a custom list of sources (eg, ['stanford']) to accept. If not defined, defaults
    '''
    item = {"id":item_id,
            "id_source":id_source}

    # Custom fields and id_timestamp are optional
    if custom_fields != None:
        item['custom_fields'] = custom_fields 

    if id_timestamp != None:
        item["id_timestamp"] = id_timestamp

    valid = validate_item(item,sources=sources,
                          custom_fields=custom_fields,
                          verbose=verbose)
    if valid == True:
        return item

    return None
