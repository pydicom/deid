#!/usr/bin/env python3
"""
CLI 'main' entrypoint for pixel scrubbing
"""
import os
import tempfile
import argparse  # for typing only
from deid.dicom import get_files
from deid.dicom.pixels import DicomCleaner
from deid.logger import bot


def pixel_main(args: argparse.Namespace, parser: argparse.ArgumentParser = None):
    """
    CLI interface for pixel cleaning.
    Used as `main` by py:func:`deid.main.main`

    Also see `getting-started/dicom-pixels`

    Parameters
    ==========
    args:  Likely created by py:func:`deid.main.get_parser`.
           Uses output_folder, deid

    parser: for compatibility with other *.main functions. Ignored.
    """

    output_folder = args.outfolder
    if output_folder is None:
        output_folder = tempfile.mkdtemp()

    if args.input is None:
        bot.exit("No input folder specified. Specify inputs as additional arguments.")
    dicom_files = list(get_files(args.input))

    bot.info("Looking at %i input dicoms" % len(dicom_files))

    # NOTE: self.results and self.file is updated each call to detect
    #       may want new client for each file to be safe?
    client = DicomCleaner(output_folder=output_folder, deid=args.deid)
    for dcm in dicom_files:
        #: py:func:`deid.dicom.pixels.detect._has_burned_pixels_single` dictionary
        has_burn_in = client.detect(dcm)
        client.clean()
        # prefix and extension empty to reuse same name as input
        # folder=None means use self.output_folder
        client.save_dicom(output_folder=None, prefix="", extension="")
