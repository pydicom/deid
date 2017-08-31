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
    sections,
    filters
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

    spec = [x for x in spec if x not in ['', None]]
    config = dict()
    section = None

    while len(spec) > 0:

        line = spec.pop(0)

        # Clean up white trailing/leading space
        line=line.strip()

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
 
            # Remove any comments
            line = line.split('#',1)[0].strip()

            # Is there a section name?
            section_name = None
            parts = line.split(' ')
            if len(parts) > 1:
                section_name = ' '.join(parts[1:])          

            section = re.sub('[%]|(\s+)','',parts[0]).lower()
            if section not in sections:
                bot.error("%s is not a valid section." %section)
                sys.exit(1)

            config = add_section(config=config,
                                 section=section,
                                 section_name=section_name)

        # An action (replace, blank, remove, keep, jitter)
        elif line.upper().startswith(actions):
              
            # Start of a filter group
            if line.upper().startswith('LABEL') and section == "filter":

                # This is an index of starting points for groups
                keep_going = True
                members = []
                while keep_going is True:
                    next_line = spec[0]                
                    if next_line.upper().strip().startswith('LABEL'):
                        keep_going = False
                    elif next_line.upper().strip().startswith("%"):
                        keep_going = False
                    else:
                        new_member = spec.pop(0)
                        members.append(new_member)

                # Add the filter label to the config
                config = parse_label(config=config,
                                     section=section,
                                     label=line,
                                     section_name=section_name,
                                     members=members)

            # Parse the action
            else:
                config = parse_action(section=section,
                                      section_name=section_name,
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


def parse_label(section,config,section_name,members,label=None):
    '''parse label will add a (optionally named) label to the filter
    section, including one or more criteria'''
    criteria = {'filters':[]}
    if label is not None:                                   
        label = (label.lower().replace('label','',1)
                              .split('#')[0]
                              .strip())
        criteria['name'] = label
    
    entry = []
    while len(members) > 0:
        member = members.pop(0).strip()

        # If if doesn't start with a +, it's a new criteria
        if not member.startswith('+') or not member.startswith('||'):
            if len(entry) > 0:
                criteria['filters'].append(entry.copy())
                entry = []

        operator = None
        values = None

        if member.startswith('+'):
            operator = 'and'
            member = member.replace('+','',1)
        elif member.startswith('||'):
            operator = 'or'
            member = member.replace('||','',1)
       
        # Now that operators removed, parse member
        if not member.lower().startswith(filters):
            bot.warning('%s filter is not valid, skipping.' %member.lower())
        else:
            action, member = member.split(' ',1)
            if action.lower() in ['contains','notcontains','equals','notequals']:
                field,values = member.split(' ',1)
            elif action.lower() in ['missing', 'empty']:
                field = member.strip()
            else:
                bot.error('%s is not a valid filter action.' %action.lower())
                sys.exit(1)

            entry_action = {'action':action.lower(),
                            'field': field}

            if values is not None:
                entry_action['values'] = values            
            if operator is not None:
                entry_action['operator'] = operator            

            entry.append(entry_action.copy())

    # Add the last entry
    if len(entry) > 0:
        criteria['filters'].append(entry.copy())

    print("adding to %s" %section_name)
    config[section][section_name].append(criteria)
    return config


def add_section(config,section,section_name=None):
    '''add section will add a section (and optionally)
    section name to a config
    '''
    if section is None:
        bot.error('You must define a section (e.g. %header) before any action.')
        sys.exit(1)

    if section == 'filter' and section_name is None:
        bot.error("You must provide a name for a filter section.")
        sys.exit(1)

    if section not in sections:
        bot.error("%s is not a valid section." %section)
        sys.exit(1)
            
    if section not in config:

        # If a section is named, we have more one level (dict)
        if section_name is not None:
            config[section] = {}
            config[section][section_name] = []
        else:
            config[section] = []
        return config

    # Section is in config
    if section_name is not None and section_name not in config[section]:
        config[section][section_name] = []

    return config


def parse_action(section,line,config,section_name=None):
    '''add action will take a line from a deid config file, a config (dictionary), and
    an active section name (eg header) and add an entry to the config file to perform
    the action.

    Parameters
    =========
    section: a valid section name from the deid config file
    line: the line content to parse for the section/action
    config: the growing/current config dictionary
    section_name: optionally, a section name

    '''
            
    if not line.upper().startswith(actions):
        bot.error("%s is not a valid action line." %line)
        sys.exit(1)

    # We may have to deal with cases of spaces
    parts = line.split(' ')
    action = parts.pop(0).replace(' ','')

    # What field is the action for?
    if len(parts) < 1:
        bot.error("%s requires a FIELD value, but not found." %(action))        
        sys.exit(1)

    field = parts.pop(0)

    # Actions that require a value
    if action in [ "ADD", "REPLACE", "JITTER" ]:
        if len(parts) == 0:
            bot.error("%s requires a VALUE, but not found" %(action))        
            sys.exit(1)
        value = ' '.join(parts[0:])  # get remained of line
        value = value.split('#')[0]  # remove comments
        bot.debug("Adding %s" %line) #
        config[section].append({ "action":action,
                                 "field":field,
                                 "value":value })

    # Actions that don't require a value
    elif action in [ "BLANK", "KEEP", "REMOVE" ]:
        bot.debug("%s: adding %s" %(section,line))
        config[section].append({ "action":action,
                                 "field":field })

    return config

