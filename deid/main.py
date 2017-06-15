#!/usr/bin/env python3

'''

The MIT License (MIT)

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

from glob import glob
import deid
import tempfile
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(
    description="Deid (de-identification) command line tool.")

    # Single image, must be string
    parser.add_argument("--input","-i", dest='folder', 
                        help="input folder to search for images. If not provided, test data will be used.", 
                        type=str, default=None)

    parser.add_argument("--version","-v", dest='version', 
                        help="show deid software version", 
                        default=False, action='store_true')

    parser.add_argument("--print","-p", dest='print', 
                        help="if set, only print output to the screen.", 
                        default=False, action='store_true')

    parser.add_argument("--format","-f", dest='format', 
                        help="format of images to de-identify, must be specified if deid is not provided", 
                        default="dicom", choices=['dicom'])

    # Does the user want to have verbose logging?
    parser.add_argument('--quiet',"-q", dest="quiet", 
                        help="Quiet the verbose output", 
                        default=False, action='store_true')

    parser.add_argument("--outfolder","-o", dest='outfolder', 
                        help="full path to save output, will use temporary folder if not specified", 
                        type=str, default=None)

    parser.add_argument('--overwrite', dest="overwrite", 
                        help="overwrite pre-existing files in output directory, if they exist.", 
                        default=False, action='store_true')

    # A path to a deid file, if customization wanted
    parser.add_argument("--deid", dest='deid', 
                        help="Path to a folder with, or deid file to specify de-identification preferences.", 
                        type=str, default=None)

    # A path to an ids file, required if user wants to put (without get)
    parser.add_argument("--ids", dest='ids', 
                        help="Path to a json file with identifiers, required for PUT if you don't do get (via all)", 
                        type=str, default=None)


    # Action
    parser.add_argument("--action","-a", dest='action', 
                        help="specify to get, put (replace), or all. Default will get identifiers.", 
                        default=None, choices=['get','put','all'], required=True)

    return parser


def main():

    parser = get_parser()

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    # if environment logging variable not set, make silent
    if args.quiet is True:
        os.environ['MESSAGELEVEL'] = "INFO"

    if args.version is True:
        print(deid.__version__)
        sys.exit(0)

    output_folder = args.outfolder
    if output_folder is None and args.print is False:
        output_folder = tempfile.mkdtemp()

    # Initialize the message bot, with level above
    from deid.logger import bot
    from deid.dicom import get_files
    from deid.data import get_dataset  

    # If a deid is given, check against format
    if args.deid is not None:
        from deid.config import load_deid
        params = load_deid(args.deid)
        if params['format'] != args.format:
            bot.error("Format in deid (%s) doesn't match choice here (%s) exiting." %(params['format'],
                                                                                      args.format))

    # Get list of dicom files
    base = args.folder
    if base is None:
        bot.info("No input folder specified, will use demo dicom-cookies.")
        base = get_dataset('dicom-cookies')
    basename = os.path.basename(base)
    dicom_files = get_files(base)


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
        from deid.dicom import get_identifiers
        ids = get_identifiers(dicom_files)
        if args.print is True:
            print(ids)
        else:
            from deid.identifiers import save_identifiers
            save_identifiers(ids,output_folder)

    if do_put is True:           
       from deid.dicom import replace_identifiers
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
