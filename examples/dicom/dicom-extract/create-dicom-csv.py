from walkdir import filtered_walk, file_paths
import pydicom
import os
import platform
import csv
from collections.abc import Sequence
from collections import OrderedDict


def load_tags_in_files(tag_file_path):
    """
    load tags_in_files reads a csv file containing dicom tags 
    and creates a dictionary

    Args:
        tag_file_path (str): Path to the tag file to load.

    Returns:
        dict: A dictionary containing the tags loaded.
    """
    tags_in_files = {}
    with open(tag_file_path, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip headers
        for row in reader:
            tags_in_files[row[2]] = row
    return tags_in_files


def get_tags_in_files(dicom_path, tag_file_path):
    """
    get_tags_in_files iterates over a directory, finds dicom files with
    a .dcm extension, and finds all unique dicom tag instances. it then
    writes the tags out as a csv file.

    Args:
        dicom_path (str): Path to scan for dicom files.
        tag_file_path (str): Path and file name for the output csv file.

    Returns:
        dict: A dictionary containing the tags loaded.
    """
    # create the output directory
    if not os.path.exists(os.path.dirname(tag_file_path)):
        os.makedirs(os.path.dirname(tag_file_path))

    # get the tags
    tags_in_files = {}
    dicom_file_paths = file_paths(filtered_walk(dicom_path, included_files=["*.dcm"]))
    for dicom_file_path in dicom_file_paths:
        dicom_file = pydicom.read_file(dicom_file_path)
        for item in dicom_file:
            if item.keyword not in tags_in_files:
                group = "0x%04x" % item.tag.group
                element = "0x%04x" % item.tag.element
                tags_in_files[item.keyword] = group, element, item.keyword, item.name

    # sort the tags
    tags_in_files = OrderedDict(
        sorted(tags_in_files.items(), key=(lambda k: (k[1][0], k[1][1])))
    )

    # write out the file
    with open(tag_file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["group", "element", "keyword", "name"])
        for item in tags_in_files:
            writer.writerow(tags_in_files[item])

    return tags_in_files


def directory_to_csv(dicom_path, csv_file_path, tags_in_files, tags_to_exclude):
    """
    directory_to_csv iterates over a directory, finds dicom files with
    a .dcm extension and then creates a spreadsheet containing all of 
    the tag values for the tags in the csv for every dicom file

    Args:
        dicom_path (str): Path to scan for dicom files.
        csv_file_path (str): Path and file name for the output csv file.
        tags_in_files (dict): Dictionary containing tags to include in the csv
        tags_to_exclude (dict): Dictionary containing tags to exclude in the csv

    Returns:
        None
    """
    tags_in_files = tags_in_files.copy()  # copy because we're going to modify
    for tag_to_exclude in tags_to_exclude:
        if tag_to_exclude in tags_in_files:
            del tags_in_files[tag_to_exclude]

    # sort by group and then element number
    tags_in_files = OrderedDict(
        sorted(tags_in_files.items(), key=(lambda k: (k[1][0], k[1][1])))
    )
    dicom_file_paths = file_paths(filtered_walk(dicom_path, included_files=["*.dcm"]))

    with open(csv_file_path, "w") as f:
        writer = csv.writer(f)

        # write the headers
        header_row = list(tags_in_files.keys())
        header_row.append("FilePath")
        writer.writerow(header_row)

        # write the rows
        for dicom_file_path in dicom_file_paths:
            dicom_file = pydicom.read_file(dicom_file_path)

            row_vals = []
            for keyword in tags_in_files:
                tag_val = dicom_file.get(keyword)

                if tag_val is None:
                    tag_val = ""
                else:
                    if isinstance(tag_val, Sequence) and not isinstance(
                        tag_val, (str, bytes, bytearray)
                    ):
                        tag_val = "^".join([str(x) for x in tag_val])
                    elif not isinstance(tag_val, str):
                        tag_val = str(tag_val)

                    tag_val = (
                        tag_val.replace(",", "^").replace("\n", "").replace("\r", "")
                    )
                row_vals.append(tag_val)

            row_vals.append(dicom_file_path)
            writer.writerow(row_vals)


if __name__ == "__main__":
    """
    Need an easy way to for a person to validate their deidentification worked. 
    This example 1st scans a directory and creates a unique set of dicom tags
    across all files. It then reads the values for all tags in all files and
    creates a csv file which can be loaded into excel or a database to review. 
    """
    osx = platform.system().lower() == "darwin"
    if osx:
        # osx
        dicom_path = os.path.abspath("%s/Documents/_data/out" % os.path.expanduser("~"))
        validate_path = os.path.abspath(
            "%s/Documents/_data/validate" % os.path.expanduser("~")
        )
    else:
        # win
        dicom_path = os.path.abspath("f:\\data\\out")
        validate_path = os.path.abspath("f:\\data\\validate")

    tag_file_path = os.path.join(validate_path, "tags_in_files.csv")
    csv_file_path = os.path.join(validate_path, "dicom.csv")

    # tags_in_files = get_tags_in_files(dicom_path, tag_file_path)
    # print(tags_in_files)

    tags_in_files = load_tags_in_files(tag_file_path)
    tags_to_exclude = {"PixelData": ["0x7fe0", "0x0010", "Pixel Data", "PixelData"]}
    directory_to_csv(dicom_path, csv_file_path, tags_in_files, tags_to_exclude)
