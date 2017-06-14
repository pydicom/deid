'''
utils.py: util functions for working with deid configuration files

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

The functions below assume a configuration file called deid, although the
user can specify a custom name.

'''

from deid.logger import bot
from deid.utils import read_file
from .standards import (
    formats,
    actions,
    sections
)
import os
import re
import sys


def load_deid(path=None):
    '''load_deid will return a loaded in (user) deid configuration file
    that can be used to update a default config.json. If a file path is
    specified, it is loaded directly. If a folder is specified, we look
    for a deid file in the folder. If nothing is specified, we assume
    the user wants to load a deid file in the present working directory.
    If the user wants to have multiple deid files in a directory, this
    can be done with an extension that specifies the module, eg;
   
             deid.dicom
             deid.nifti

    (and this is TBA in terms of proper use case)
    '''
    path = find_deid(path)

    # Read in spec, clean up extra spaces and newlines
    spec = [x.strip('\n').strip(' ') 
           for x in read_file(path) 
           if x.strip('\n').strip(' ') not in ['']]

    config = dict()
    section = None
    for line in spec:

        # Comment
        if line.startswith("#"):
            continue

        # Starts with Format?
        elif bool(re.match('format', line, re.I)):
            fmt = re.sub('FORMAT|(\s+)','',line).lower()
            if fmt not in formats:
                bot.error("%s is not a valid format." %fmt)
                sys.exit(1)

            # Set format
            config['format'] = fmt
            bot.debug("FORMAT set to %s" %fmt)

        # A new section?
        elif line.startswith('%'):
            section = re.sub('[%]|(\s+)','',line).lower()
            if section not in sections:
                bot.error("%s is not a valid section." %section)
                sys.exit(1)

        # An action (replace, blank, remove, keep)
        elif line.upper().startswith(actions):
            if section is None:
                bot.error('You must define a section (e.g. %header) before any action.')
                sys.exit(1)

            # Parse the action
            config = parse_action(section=section,
                                  line=line,
                                  config=config)
        else:
            bot.debug("%s not recognized to be in valid format, skipping." %line)

    return config


def find_deid(path):
    '''find_deid is a helper function to load_deid to find a deid file in
    a folder, or return the path provided if it is the file.
    '''
    if path is None:
        path = os.getcwd()

    # The user has provided a directory
    if os.path.isdir(path):
        contenders = ["%s/%s" %(path,x) for x 
                      in os.listdir(path)
                      if x.startswith('deid')]

        if len(contenders) == 0:
            bot.error("No deid settings files found in %s, exiting." %(path))
            sys.exit(1)

        elif len(contenders) > 1:   
            bot.warning("Multiple deid files found in %s, will use first." %(path))

        path = contenders[0]

    # We have a file path at this point
    if not os.path.exists(path):
        bot.error("Cannot find deid file %s, exiting." %(path))
        sys.exit(1)

    return path


def parse_action(section,line,config):
    '''add action will take a line from a deid config file, a config (dictionary), and
    an active section name (eg header) and add an entry to the config file to perform
    the action.
    '''
    if section not in sections:
        bot.error("%s is not a valid section." %section)
        sys.exit(1)

    if not line.upper().startswith(actions):
        bot.error("%s is not a valid action line." %line)
        sys.exit(1)

    if section not in config:
        config[section] = []

    # We may have to deal with cases of spaces
    parts = line.split(' ')
    action = parts.pop(0).replace(' ','')

    # What field is the action for?
    if len(parts) < 1:
        bot.error("%s requires a FIELD value, but not found." %(action))        
        sys.exit(1)
    field = parts.pop(0)

    # Actions that require a value
    if action in [ "ADD", "REPLACE" ]:
        if len(parts) == 0:
            bot.error("%s requires a VALUE, but not found" %(action))        
            sys.exit(1)
        value = parts.pop(0)
        bot.debug("Adding %s" %line)
        config[section].append({ "action":action,
                                 "field":field,
                                 "value":value })

    # Actions that don't require a value
    elif action in [ "BLANK" "KEEP", "REMOVE" ]:
        bot.debug("Adding %s" %line)
        config[section].append({ "action":action,
                                 "field":field })

    return config

