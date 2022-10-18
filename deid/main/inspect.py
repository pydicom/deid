#!/usr/bin/env python3

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import datetime
import os

from deid.config import load_deid
from deid.data import get_dataset
from deid.dicom import get_files, has_burned_pixels
from deid.logger import bot


def main(args, parser):
    """
    Inspect the header fields of dicom files.

    inspect currently serves to inspect the header fields of a set
    of dicom files against a standard, and flag images that don't
    pass the different levels of criteria
    """

    # If a deid is given, check against format
    deid = args.deid
    if deid is not None:
        params = load_deid(deid)
        if params["format"] != args.format:
            bot.error(
                "Format in deid (%s) doesn't match choice here (%s) exiting."
                % (params["format"], args.format)
            )
    # Get list of dicom files
    base = args.folder
    if base is None:
        bot.info("No input folder specified, will use demo dicom-cookies.")
        base = get_dataset("dicom-cookies")

    dicom_files = list(
        get_files(base, pattern=args.pattern)
    )  # todo : consider using generator functionality
    result = has_burned_pixels(dicom_files, deid=deid)

    print("\nSUMMARY ================================\n")
    if result["clean"]:
        bot.custom(
            prefix="CLEAN", message="%s files" % len(result["clean"]), color="CYAN"
        )

    if result["flagged"]:
        for group, files in result["flagged"].items():
            bot.flag("%s %s files" % (group, len(files)))

    if args.save:
        folders = "-".join([os.path.basename(folder) for folder in base])
        outfile = "pixel-flag-results-%s-%s.tsv" % (
            folders,
            datetime.datetime.now().strftime("%y-%m-%d"),
        )

        with open(outfile, "w") as filey:
            filey.writelines("dicom_file\tpixels_flagged\tflag_list\treason\n")

            for clean in result["clean"]:
                filey.writelines("%s\tCLEAN\t\t\n" % clean)

            for flagged, details in result["flagged"].items():
                if details["flagged"] is True:
                    for result in details["results"]:
                        group = result["group"]
                        reason = result["reason"]
                        filey.writelines(
                            "%s\tFLAGGED\t%s\t%s\n" % (flagged, group, reason)
                        )

            print("Result written to %s" % outfile)
