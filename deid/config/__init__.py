'''

DeidRecipe

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

The functions below assume a configuration file called deid, although the
user can specify a custom name.


'''

from deid.config.utils import (
    load_deid,
    get_deid,
    load_combined_deid
)
from deid.config.standards import (
    actions,
    sections,
    formats
)

from deid.logger import bot
import os
import re

bot.level = 3

class DeidRecipe:
    '''Create and work with a deid recipe to filter and perform operations on
       a dicom header. Usage typically looks like:

       deid = 'dicom.deid'
       recipe = DeidRecipe(deid)
       
       If deid is None, the default provided by the application is used.

       Parameters
       ==========
       deid: the deid recipe (or recipes) files to use. If more than one
             is provided, should be done in order of preference for load
             (later in the list overrides earlier loaded).
       base: if True, load a default base (default_base) before custom
       default_base: the default base to load if "base" is True

    '''
    
    def __init__(self, deid=None, base=False, default_base='dicom'):

        # If deid is None, use the default
        if deid is None:
            bot.warning('No specification, loading default base deid.%s' %default_base)
            base = True

        self._init_deid(deid, base=base, default_base=default_base)

    def __str__(self):
        return '[deid]'

    def __repr__(self):
        return '[deid]'

    def load(self, deid):
        '''load a deid recipe into the object. If a deid configuration is
           already defined, append to that. 
        '''
        deid = get_deid(deid)
        if deid is not None:
 
            # Update our list of files
            self._files.append(deid)
            self.files = list(set(self.files))

            # Priority here goes to additional deid
            self.deid = load_combined_deid([self.deid, deid])

    def _get_section(self, name):
        '''return a section (key) in the loaded deid, if it exists
        '''
        section = None
        if self.deid is not None:
            if name in self.deid:
                section = self.deid[name]
        return section


    def get_format(self):
        '''return the format of the loaded deid, if one exists
        '''
        return self._get_section('format')


    def get_filters(self, name=None):
        '''return all filters for a deid recipe, or a set based on a name
        '''
        filters = self._get_section('filter')
        if name is not None and filters is not None:
            filters = filters[name]        
        return filters


    def ls_filters(self):
        '''list names of filter groups
        '''
        filters = self._get_section('filter')
        return list(filters.keys())

    def get_actions(self, action=None, field=None):
        '''get deid actions to perform on a header, or a subset based on a type

           A header action is a list with the following:
           {'action': 'REMOVE', 'field': 'AssignedLocation'},
 
           Parameters
           ==========
           action: if not None, filter to action specified
           field: if not None, filter to field specified

        '''
        header = self._get_section('header')
        if header is not None:
            if action is not None:
                action = action.upper()
                header = [x for x in header if x['action'].upper() == action]      
            if field is not None:
                field = field.upper()
                header = [x for x in header if x['field'].upper() == field]  

        return header


    def _init_deid(self, deid=None, base=False, default_base='dicom'):
        '''initalize the recipe with one or more deids, optionally including 
           the default. This function is called at init time. If you need to add
           or work with already loaded configurations, use add/remove 
    
           Parameters
           ==========
           deid: the deid recipe (or recipes) files to use. If more than one
                 is provided, should be done in order of preference for load
                 (later in the list overrides earlier loaded).
           default_base: load the default base before the user customizations. 

        '''
        if deid is None:
            deid = []

        if not isinstance(deid,list):
            deid = [deid]

        if base is True:
            deid.append(default_base)

        self._files = deid

        if len(deid) == 0:
            bot.info('You can add custom deid files with .load().')
        self.deid = load_combined_deid(deid)
