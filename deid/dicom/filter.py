'''

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

from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from deid.logger import bot
import os
import re

# These filters are based off the the CTP Dicom Filter
# http://mircwiki.rsna.org/index.php?title=The_CTP_DICOM_Filter
# We don't apply them to the tag, as in their examples:

# !ImageType.contains("SECONDARY")

# we apply them to the dataset, with the tag as an argument:
# dicom.contains("ImageType","SECONDARY")

def apply_filter(dicom, field, filter_name, value):
    '''essentially a switch statement to apply a filter to a dicom file.

       Parameters
       ==========
       dicom: the pydicom.dataset Dataset (pydicom.read_file)
       field: the name of the field to apply the filter to
       filer_name: the name of the filter to apply (e.g., contains)
       value: the value to set, if filter_name is valid

    '''
    filter_name = filter_name.lower().strip()

    if filter_name == "contains":
        return dicom.contains(field,value)

    if filter_name == "notcontains":
        return dicom.notContains(field,value)

    elif filter_name == "equals":
        return dicom.equals(field,value)

    elif filter_name == "missing":
        return dicom.missing(field)

    elif filter_name == "present":
        return not dicom.missing(field)

    elif filter_name == "empty":
        return dicom.empty(field)

    elif filter_name == "notequals":
        return dicom.notEquals(field,value)

    bot.warning("%s is not a valid filter name, returning False" %filter_name)
    return False



################################################################################
# Equals
################################################################################


def equalsBase(self, field, term, ignore_case=True, not_equals=False):
    '''base of equals, with variable for ignore case (default True)
    '''

    is_equal = False

    contenders = self.get(field)

    if not isinstance(contenders,list):
        contenders = [contenders]    

    # In this loop we can only switch to True
    for contender in contenders:
        if contender is not None:
            if ignore_case:
                if not isinstance(contender,Sequence):                
                    try:
                        contender = str(contender).lower().strip()
                        term = str(term).lower().strip()
                    except AttributeError:
                        pass # we are dealing with number

                if contender == term:
                    is_equal = True

    # If we want to know not_equals, reverse
    if not_equals is True:
        is_equal = not is_equal

    return is_equal


def equals(self,field,term):
    '''returns true if the value of the identifier exactly 
       equals the string argument; otherwise, it returns false.'''
    return self.equalsBase(field,term)


def notEquals(self,field,term):
    return self.equalsBase(field=field,
                           term=term,
                           not_equals=True)



Dataset.equalsBase = equalsBase
Dataset.equals = equals
Dataset.notEquals = notEquals

################################################################################
# Empty and Null
#
# missing: means the field is not present (None)
# empty: means the field is present and empty
################################################################################


def missing(self, field):
    '''missing returns True if the dicom is missing the field entirely
       This means that the entire field is None
    '''
    content = self.get(field)
    if content == None:
        return True
    return False

 
def empty(self,field):
    '''empty returns True if the value is found to be ""
    '''
    content = self.get(field)
    if content == "":
        return True
    return False


Dataset.empty = empty
Dataset.missing = missing


################################################################################
# Matches and Contains
# 
# contains: searches across entire field
# matches: looks for exact match
################################################################################


def compareBase(self,field,expression,func,ignore_case=True):
    '''compareBase takes either re.search (for contains) or
       re.match (for matches) and returns True if the given regular
       expression is contained or matched
    '''
    is_match = False

    contenders = self.get(field)

    if not isinstance(contenders,list):
        contenders = [contenders]    

    for contender in contenders:
        if contender is not None:

            if not isinstance(contender,Sequence):                
                if ignore_case:
                    try:
                        contender = str(contender).lower().strip()
                        expression = str(expression).lower().strip()
                    except AttributeError:
                        pass # we are dealing with number
                             # sequence, or other private tag

                if func(expression,contender):
                    is_match = True

    return is_match


def matches(self,field,expression):
    '''matches returns true if the value of the identifier matches 
       the regular expression specified in the string argument; 
       otherwise, it returns false.
    '''
    return self.compareBase(field=field,
                            expression=expression,
                            func=re.match)


def contains(self,field,expression):
    '''contains returns true if the value of the identifier 
       contains the the string argument anywhere within it; 
       otherwise, it returns false.
    '''
    return self.compareBase(field=field,
                            expression=expression,
                            func=re.search)

def notContains(self,field,expression):
    '''notContains returns true if the value of the identifier 
       does not contain the the string argument anywhere within it; 
    '''
    return not self.compareBase(field=field,
                                expression=expression,
                                func=re.search)


Dataset.compareBase = compareBase
Dataset.matches = matches
Dataset.contains = contains
Dataset.notContains = notContains

################################################################################
# Starts and Endswith
################################################################################


def startsWith(self,field,term):
    '''startsWith returns true if the value of the identifier 
       starts with the string argument; otherwise, it returns false.
    '''
    expression = "^%s" %term
    return self.compareBase(field=field,
                            expression=expression,
                            func=re.match)
    
def endsWith(self,field,term):
    '''endsWith returns true if the value of the identifier ends with 
       the string argument; otherwise, it returns false.
    '''
    expression = "%s$" %term
    return self.compareBase(field=field,
                            expression=expression,
                            func=re.match)
    
Dataset.startsWith = startsWith
Dataset.endsWith = endsWith
