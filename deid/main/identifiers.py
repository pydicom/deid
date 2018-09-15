#!/usr/bin/env python3

'''

The MIT License (MIT)

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
from deid.dicom import get_files
from deid.data import get_dataset  
from deid.config import load_deid

from deid.dicom import (
    get_identifiers,
    save_identifiers,
    replace_identifiers
)

from glob import glob
import tempfile
import argparse
import sys
import os


def main(args,parser):

    # Global output folder
    output_folder = args.outfolder
    if output_folder is None:
        output_folder = tempfile.mkdtemp()

    # If a deid is given, check against format
    if args.deid is not None:
        params = load_deid(args.deid)
        if params['format'] != args.format:
            bot.error("Format in deid (%s) doesn't match choice here (%s) exiting." %(params['format'],
                                                                                      args.format))
    # Get list of dicom files
    base = args.input
    if base is None:
        bot.info("No input folder specified, will use demo dicom-cookies.")
        base = get_dataset('dicom-cookies')
    basename = os.path.basename(base)
    dicom_files = list(get_files(base)) # todo : consider using generator functionality


    do_get = False
    do_put = False
    ids = None
    if args.action == "all":
        bot.info("GET and PUT identifiers from %s" %(basename))
        do_get = True
        do_put = True

    elif args.action == "get":
        do_get = True
        bot.info("GET and PUT identifiers from %s" %(basename))
    
    elif args.action == "put":
        bot.info("PUT identifiers from %s" %(basename))
        do_put = True
        if args.ids is None:
            bot.error("To PUT without GET you must provide a json file with ids.")
            sys.exit(1)
        ids = args.ids

    # GET identifiers

    if do_get is True:
        ids = get_identifiers(dicom_files)
        if args.do_print is True:
            print(ids)
        else:
            save_identifiers(ids,output_folder)

    if do_put is True:           
       cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                           ids=ids,
                                           deid=args.deid,
                                           overwrite=args.overwrite,
                                           output_folder=output_folder)

       bot.info("%s %s files at %s" %(len(cleaned_files),
                                      args.format,
                                      output_folder))

if __name__ == '__main__':
    main()
