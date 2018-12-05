'''

header.py: functions to extract identifiers from dicom headers

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
from deid.utils import read_json

from .tags import (
    remove_tag,
    remove_sequences
)
from deid.identifiers.utils import (
    create_lookup,
    load_identifiers
)

from deid.dicom.tags import get_private
from deid.config import DeidRecipe

from pydicom import read_file
from pydicom.errors import InvalidDicomError
import dateutil.parser
import tempfile

from .utils import get_func, save_dicom
from .actions import perform_action
from pydicom.dataset import Dataset

from .fields import (
    get_fields,
    get_fields_byVR
)

import os

here = os.path.dirname(os.path.abspath(__file__))


################################################################################
# MAIN GET FUNCTIONS
################################################################################

def get_shared_identifiers(dicom_files,
                           force=True,
                           config=None,
                           aggregate=None,
                           expand_sequences=True):
    '''

    extract shared identifiers across a set of dicom files, intended for
    cases when a set of images (dicom) are being compressed into one file
    and the file (still) should have some searchable metadata. By default,
    we remove fields that differ between files. To aggregate unique, define
    a list of aggregate fields (aggregate).

    '''

    bot.debug('Extracting shared identifiers for %s dicom' %(len(dicom_files)))

    if aggregate is None:
        aggregate = []

    if config is None:
        config = "%s/config.json" %(here)

    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))
    config = read_json(config, ordered_dict=True)['get']

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]
    ids = dict() # identifiers

    # We will skip PixelData
    skip = config['skip']
    for dicom_file in dicom_files:
        dicom = read_file(dicom_file,force=True)
        fields = get_fields(dicom,
                            skip=skip,
                            expand_sequences=expand_sequences)
        for key,val in fields.items():

            # If it's there, only keep if the same
            if key in ids:

                # Items to aggregate are appended, not removed
                if key in aggregate:
                    if val not in ids[key]:
                        ids[key].append(val)
                else:

                    # Keep only if equal between
                    if ids[key] == val:
                        continue
                    else:
                        del ids[key]
                        skip.append(key)
            else:
                if key in aggregate:
                    val = [val]
                ids[key] = val

    # For any aggregates that are one item, unwrap again
    for field in aggregate:
        if field in ids:
            if len(ids[field])==1:
                ids[field] = ids[field][0]

    return ids



def get_identifiers(dicom_files,
                    force=True,
                    config=None,
                    expand_sequences=True,
                    skip_fields=None):
    ''' extract all identifiers from a dicom image.
        This function returns a lookup by file name

        Parameters
        ==========
        dicom_files: the dicom file(s) to extract from
        force: force reading the file (default True)
        config: if None, uses default in provided module folder
        expand_sequences: if True, expand sequences. otherwise, skips
        skip_fields: if not None, added fields to skip

    '''
    bot.debug('Extracting identifiers for %s dicom' %(len(dicom_files)))

    if config is None:
        config = "%s/config.json" %(here)

    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))
    config = read_json(config, ordered_dict=True)['get']

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    ids = dict() # identifiers

    # We will skip PixelData
    skip = config['skip']
    if skip_fields is not None:
        if not isinstance(skip_fields,list):
            skip_fields = [skip_fields]
        skip = skip + skip_fields
 
    for dicom_file in dicom_files:
        dicom = read_file(dicom_file,force=True)

        if dicom_file not in ids:
            ids[dicom_file] = dict()

        ids[dicom_file] = get_fields(dicom,
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
    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

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



def _prepare_replace_config(dicom_files, deid=None, config=None):
    ''' replace identifiers will replace dicom_files with data from ids based
        on a combination of a config (default is remove all) and a user deid

        Parameters
        ==========
        dicom_files: the dicom file(s) to extract from
        force: force reading the file (default True)
        save: if True, save to file. Otherwise, return dicom objects
        config: if None, uses default in provided module folder
        overwrite: if False, save updated files to temporary directory
    
    '''

    if config is None:
        config = "%s/config.json" %(here)
    if not os.path.exists(config):
        bot.error("Cannot find config %s, exiting" %(config))
    
    if not isinstance(deid, DeidRecipe):
        deid = DeidRecipe(deid)
    config = read_json(config, ordered_dict=True)

    if not isinstance(dicom_files,list):
        dicom_files = [dicom_files]

    return dicom_files, deid, config


def replace_identifiers(dicom_files,
                        ids,
                        deid=None,
                        save=True,
                        overwrite=False,
                        output_folder=None,
                        force=True,
                        config=None,
                        strip_sequences=True,
                        remove_private=True):

    '''replace identifiers using pydicom, can be slow when writing
    and saving new files'''

    dicom_files, recipe, config = _prepare_replace_config(dicom_files, 
                                                          deid=deid,
                                                          config=config)

    # Parse through dicom files, update headers, and save
    updated_files = []
    for d in range(len(dicom_files)):
        dicom_file = dicom_files[d]
        dicom = read_file(dicom_file,force=force)
        dicom_name = os.path.basename(dicom_file)
        fields = dicom.dir()

        # Remove sequences first, maintained in DataStore
        if strip_sequences is True:
            dicom = remove_sequences(dicom)

        if recipe.deid is not None:
            if dicom_file in ids:
                for action in deid.get_actions():
                    dicom = perform_action(dicom=dicom,
                                           item=ids[dicom_file],
                                           action=action) 
            else:
                bot.warning("%s is not in identifiers." %dicom_name)
                continue

        # Next perform actions in default config, only if not done
        for action in config['put']['actions']:
            if action['field'] in fields:
                 dicom = perform_action(dicom=dicom,
                                        action=action)
        if remove_private is True:
            try:
                dicom.remove_private_tags()
            except:
                bot.error('''Private tags for %s could not be completely removed, usually
                             this is due to invalid data type. Removing others.''' % dicom_name)
                private_tags = get_private(dicom)
                for ptag in private_tags:
                    del dicom[ptag.tag]
                continue
        else:
            bot.warning("Private tags were not removed!")

        ds = Dataset()
        for field in dicom.dir():
            try:
                ds.add(dicom.data_element(field))
            except:
                pass

        # Copy original data attributes
        attributes = ['is_little_endian',
                      'is_implicit_VR',
                      'is_decompressed',
                      'read_encoding',
                      'read_implicit_vr',
                      'read_little_endian',
                      '_parent_encoding']

        # We aren't including preamble, we will reset to be empty 128 bytes
        ds.preamble = b"\0" * 128

        for attribute in attributes:
            if hasattr(dicom, attribute):
                ds.__setattr__(attribute, dicom.__getattribute__(attribute))

        # Original meta data                     # or default empty dataset
        file_metas = getattr(dicom, 'file_meta', Dataset())
        
        # Media Storage SOP Instance UID can be identifying
        if hasattr(file_metas, 'MediaStorageSOPInstanceUID'):
            file_metas.MediaStorageSOPInstanceUID = ''

        # Save meta data
        ds.file_meta = file_metas
       
       # Save to file?
        if save is True:
            ds = save_dicom(dicom=ds,
                            dicom_file=dicom_file,
                            output_folder=output_folder,
                            overwrite=overwrite)
        updated_files.append(ds)

    return updated_files
