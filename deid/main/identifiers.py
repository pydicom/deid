#!/usr/bin/env python3

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"


import os
import tempfile

from deid.config import load_deid
from deid.data import get_dataset
from deid.dicom import get_files
from deid.dicom.header import get_identifiers, replace_identifiers
from deid.logger import bot


def main(args, parser):

    # Global output folder
    output_folder = args.outfolder
    if output_folder is None:
        output_folder = tempfile.mkdtemp()

    # If a deid is given, check against format
    if args.deid is not None:
        params = load_deid(args.deid)
        if params["format"] != args.format:
            bot.error(
                "Format in deid (%s) doesn't match choice here (%s) exiting."
                % (params["format"], args.format)
            )
    # Get list of dicom files
    base = args.input
    if base is None:
        bot.info("No input folder specified, will use demo dicom-cookies.")
        base = get_dataset("dicom-cookies")
    basename = os.path.basename(base)
    dicom_files = list(get_files(base))  # todo : consider using generator functionality

    do_get = False
    do_put = False
    ids = None
    if args.action == "all":
        bot.info("GET and PUT identifiers from %s" % (basename))
        do_get = True
        do_put = True

    elif args.action == "get":
        do_get = True
        bot.info("GET and PUT identifiers from %s" % (basename))

    elif args.action == "put":
        bot.info("PUT identifiers from %s" % (basename))
        do_put = True
        if args.ids is None:
            bot.exit("To PUT without GET you must provide a json file with ids.")

        ids = args.ids

    # GET identifiers

    if do_get is True:
        ids = get_identifiers(dicom_files)

    if do_put is True:
        cleaned_files = replace_identifiers(
            dicom_files=dicom_files,
            ids=ids,
            deid=args.deid,
            overwrite=args.overwrite,
            output_folder=output_folder,
        )

        bot.info("%s %s files at %s" % (len(cleaned_files), args.format, output_folder))
