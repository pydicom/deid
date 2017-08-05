'''
header.py: functions to extract identifiers from dicom headers

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
from deid.utils import read_json

from .tags import (
    remove_tag,
    remove_sequences
)
from deid.identifiers.utils import (
    create_lookup,
    load_identifiers
)

from deid.config import load_deid
from pydicom import read_file
from pydicom.errors import InvalidDicomError
import dateutil.parser
import tempfile

from .utils import get_func, save_dicom
from .actions import perform_action

from .fields import (
    get_fields,
    get_fields_byVR
)

import os

here = os.path.dirname(os.path.abspath(__file__))


######################################################################
# MAIN GET FUNCTIONS
######################################################################


def get_identifiers(dicom_files,
                    force=True,
                    config=None,
                    entity_id=None,
                    item_id=None,
                    expand_sequences=True):

    '''extract all identifiers from a dicom image.
    This function cannot be sure if more than one source_id 
    is present in the data, so it returns a lookup dictionary 
    by patient and item id.
    :param dicom_files: the dicom file(s) to extract from
    :param force: force reading the file (default True)
    :param config: if None, uses default in provided module folder
    :param entity_id: if specified, override default in config
    :param item_id: if specified, overrides 
    :param expand_sequences: if True, expand sequences. otherwise, skips
    '''

    bot.debug('Extracting identifiers for %s dicom' %(len(dicom_files)))

    if config is None:
        config = "%s/config.json" %(here)

    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))

    config = read_json(config)['get']

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    ids = dict() # identifiers

    # We will skip PixelData
    skip = config['skip']

    # Organize the data based on the following
    if entity_id is None:
        entity_id = config['ids']['entity']
    if item_id is None:
        item_id = config['ids']['item']


    for dicom_file in dicom_files:
        dicom = read_file(dicom_file,force=True)

        # Read in / calculate preferred values
        entity = dicom.get(entity_id)
        item = dicom.get(item_id)

        if entity is None or item is None:
            bot.warning("Cannot find entity or item id for %s, skipping." %(dicom_file))
            continue

        if entity not in ids:
            ids[entity] = dict()
         
        ids[entity][item] = get_fields(dicom,
                                       skip=skip,
                                       expand_sequences=expand_sequences)

    return ids


def remove_private_identifiers(dicom_files,
                               save=True,
                               overwrite=False,
                               output_folder=None,
                               force=True):

    '''remove_private_identifiers is a wrapper for the 
    simple call to dicom.remove_private_tags, it simply
    reads in the files for the user and saves accordingly
    '''
    updated_files = []

    for dicom_file in dicom_files:
        dicom = read_file(dicom_file,force=force)
        dicom.remove_private_tags()
        dicom_name = os.path.basename(dicom_file)
        bot.debug("Removed private identifiers for %s" %dicom_file)

        if save:
            dicom = save_dicom(dicom=dicom,
                               dicom_file=dicom_file,
                               output_folder=output_folder,
                               overwrite=overwrite)

        updated_files.append(dicom)
    return updated_files


def replace_identifiers(dicom_files,
                        ids,
                        deid=None,
                        save=True,
                        overwrite=False,
                        output_folder=None,
                        entity_id=None,
                        item_id=None,
                        force=True,
                        config=None,
                        default_action="KEEP",
                        strip_sequences=True,
                        remove_private=True):
    '''replace identifiers will replace dicom_files with data from ids based
    on a combination of a config (default is remove all) and a user deid spec
    :param dicom_files: the dicom file(s) to extract from
    :param force: force reading the file (default True)
    :param save: if True, save to file. Otherwise, return dicom objects
    :param config: if None, uses default in provided module folder
    :param overwrite: if False, save updated files to temporary directory
    '''
    if config is None:
        config = "%s/config.json" %(here)
    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))
    # Validate any provided deid
    if deid is not None:
        if not isinstance(deid,dict):
            deid = load_deid(deid)
            if deid['format'] != 'dicom':
                bot.error('DEID format must be dicom.')
                sys.exit(1)
    config = read_json(config)
    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]
    # Organize the data based on the following
    if entity_id is None:
        entity_id = config['get']['ids']['entity']
    if item_id is None:
        item_id = config['get']['ids']['item']
    # Is a default specified?
    bot.debug("Default action is %s" %default_action)
    # Parse through dicom files, update headers, and save
    updated_files = []
    for dicom_file in dicom_files:
        dicom = read_file(dicom_file,force=force)
        dicom_name = os.path.basename(dicom_file)
        # Read in / calculate preferred values
        entity = dicom.get(entity_id)
        item = dicom.get(item_id) 
        fields = dicom.dir()
        # Remove sequences first, maintained in DataStore
        if strip_sequences is True:
            dicom = remove_sequences(dicom)
        if deid is not None:
            for entity in ids:
                if item in ids[entity]:
                    for action in deid['header']:
                        dicom,seen = perform_action(dicom=dicom,
                                                item=ids[entity][item],
                                                action=action,
                                                fields=fields,
                                                return_seen=True)
                        fields = [x for x in fields if x not in seen]
        # Next perform actions in default config, only if not done
        for action in config['put']['actions']:
            if action['field'] in fields:
                 dicom, seen = perform_action(dicom=dicom,
                                              action=action,
                                              return_seen=True)
                 fields = [x for x in fields if x not in seen]
        # Apply default action, only if not keep
        if default_action != "KEEP":
            for field in fields:
                dicom = perform_action(dicom=dicom,
                                       action={'action': default_action, 
                                               'field': field })
        if remove_private is True:
            dicom.remove_private_tags()
        else:
            bot.warning("Private tags were not removed!")
        # Save to file?
        if save:
            dicom = save_dicom(dicom=dicom,
                               dicom_file=dicom_file,
                               output_folder=output_folder,
                               overwrite=overwrite)
        updated_files.append(dicom)
    return updated_files
