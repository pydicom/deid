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
from deid.config import load_deid, get_deid
from deid.dicom import has_burned_pixels

from glob import glob
import datetime
import tempfile
import argparse
import shutil
import sys
import os


def main(args,parser):
    '''inspect currently serves to inspect the header fields of a set
    of dicom files against a standard, and flag images that don't
    pass the different levels of criteria
    '''

    # Global output folder
    #output_folder = args.outfolder
    #if output_folder is None:
    #    output_folder = tempfile.mkdtemp()

    # If a deid is given, check against format
    deid = args.deid
    if deid is not None:
        params = load_deid(deid)
        if params['format'] != args.format:
            bot.error("Format in deid (%s) doesn't match choice here (%s) exiting." %(params['format'],
                                                                                      args.format))
    # Get list of dicom files
    base = args.folder
    if base is None:
        bot.info("No input folder specified, will use demo dicom-cookies.")
        base = get_dataset('dicom-cookies')

    dicom_files = list(get_files(base, pattern=args.pattern)) # todo : consider using generator functionality
    result = has_burned_pixels(dicom_files, deid=deid)

    print('\nSUMMARY ================================\n')
    if len(result['clean']) > 0:
        bot.custom(prefix='CLEAN',
                   message="%s files" %len(result['clean']),
                   color="CYAN")

    if len(result['flagged']) > 0:
        for group,files in result['flagged'].items():
            bot.flag("%s %s files" %(group, len(files)))

    if args.save is True:
        folders = '-'.join([os.path.basename(folder) for folder in base])
        outfile = "pixel-flag-results-%s-%s.tsv" %(folders,datetime.datetime.now().strftime('%y-%m-%d'))
        with open(outfile,'w') as filey:
            filey.writelines('dicom_file\tpixels_flagged\tflag_list\treason\n')
            for clean in result['clean']:
                filey.writelines('%s\tCLEAN\t\t\n' %clean)
            for flagged,details in result['flagged'].items():
                if details['flagged'] is True:
                    for result in details['results']:
                        group = result['group']
                        reason = result['reason']
                        filey.writelines('%s\tFLAGGED\t%s\t%s\n' %(flagged,group,reason))

            print('Result written to %s' %outfile)
            
 
if __name__ == '__main__':
    main()
