#!/usr/bin/env python3

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import argparse
import os
import sys
import tempfile
from glob import glob

from deid.version import __version__


def get_parser():
    parser = argparse.ArgumentParser(
        description="Deid (de-identification, anonymization) command line tool."
    )

    # Global Variables
    parser.add_argument(
        "--quiet",
        "-q",
        dest="quiet",
        help="Quiet the verbose output",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="print version and exit.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--outfolder",
        "-o",
        dest="outfolder",
        help="full path to save output, will use temporary folder if not specified",
        type=str,
        default=None,
    )

    parser.add_argument(
        "--format",
        "-f",
        dest="format",
        help="format of images, default is dicom",
        default="dicom",
        choices=["dicom"],
    )

    parser.add_argument(
        "--overwrite",
        dest="overwrite",
        help="overwrite pre-existing files in output directory, if they exist.",
        default=False,
        action="store_true",
    )

    subparsers = parser.add_subparsers(
        help="action for deid to perform",
        title="actions",
        description="actions for deid to perform",
        dest="command",
    )

    subparsers.add_parser(
        "version", help="print version and exit"  # pylint: disable=unused-variable
    )

    # Checks (checks / tests for various services)
    inspect = subparsers.add_parser(
        "inspect", help="various checks for PHI and quality"
    )

    inspect.add_argument(
        nargs="+",
        dest="folder",
        help="input folder or single image. If not provided, test data will be used.",
        type=str,
        default=None,
    )

    inspect.add_argument(
        "--deid",
        dest="deid",
        help="deid file with preferences, if not specified, default used.",
        type=str,
        default=None,
    )

    inspect.add_argument(
        "--pattern",
        dest="pattern",
        help="A pattern to match files in input folder.",
        type=str,
        default=None,
    )

    inspect.add_argument(
        "--save",
        "-s",
        dest="save",
        help="save result to output tab separated file.",
        default=False,
        action="store_true",
    )

    ids = subparsers.add_parser(
        "identifiers", help="extract and replace identifiers from headers"
    )

    ids.add_argument(
        "--deid",
        dest="deid",
        help="deid file with preferences, if not specified, default used.",
        type=str,
        default=None,
    )

    # A path to an ids file, required if user wants to put (without get)
    ids.add_argument(
        "--ids",
        dest="ids",
        help="Path to a json file with identifiers, required for PUT if you don't do get (via all)",
        type=str,
        default=None,
    )

    ids.add_argument(
        "--input",
        dest="input",
        help="Input folder or single image to perform action on.",
        type=str,
        default=None,
    )

    # Action
    ids.add_argument(
        "--action",
        "-a",
        dest="action",
        help="specify to get, put (replace), or all. Default will get identifiers.",
        default=None,
        choices=["get", "put", "all", "inspect"],
        required=True,
    )

    return parser


def main():

    parser = get_parser()
    try:
        args = parser.parse_args()
    except Exception:
        sys.exit(0)

    if args.command == "version" or args.version:
        print(__version__)
        sys.exit(0)

    # if environment logging variable not set, make silent
    os.environ["MESSAGELEVEL"] = "INFO"
    if args.quiet is True:
        os.environ["MESSAGELEVEL"] = "QUIET"

    # Initialize the message bot, with level above
    from deid.logger import bot  # pylint: disable=unused-import

    if args.command == "identifiers":
        from .identifiers import main
    elif args.command == "inspect":
        from .inspect import main
    else:
        parser.print_help()
        sys.exit(1)

    # Run main for selection
    return main(args, parser)


if __name__ == "__main__":
    main()
