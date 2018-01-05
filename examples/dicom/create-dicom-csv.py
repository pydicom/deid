from walkdir import filtered_walk, file_paths
import pydicom
import os
import platform
import csv
import operator
from collections.abc import Sequence
from collections import OrderedDict

def load_tags_in_files(tag_file_path):
    tags_in_files = {}
    with open(tag_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader, None) # skip headers
        for row in reader:
            tags_in_files[row[2]] = row
    return tags_in_files

def get_tags_in_files(dicom_path, tag_file_path):
    # create the output directory
    if not os.path.exists(os.path.dirname(tag_file_path)):
        os.makedirs(os.path.dirname(tag_file_path))

    # get the tags
    tags_in_files = {}
    dicom_file_paths = file_paths(filtered_walk(dicom_path, included_files=['*.dcm']))
    for dicom_file_path in dicom_file_paths:
        dicom_file = pydicom.read_file(dicom_file_path)
        for item in dicom_file:
            if item.keyword not in tags_in_files:
                group = '0x%04x' %item.tag.group
                element = '0x%04x' %item.tag.element
                tags_in_files[item.keyword] = group,element,item.keyword,item.name

    # sort the tags
    tags_in_files = OrderedDict(sorted(tags_in_files.items(), key=(lambda k: (k[1][0], k[1][1]))))

    # write out the file
    with open(tag_file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['group', 'element', 'keyword', 'name'])
        for item in tags_in_files:
            writer.writerow(tags_in_files[item])
    
    return tags_in_files

def directory_to_csv(dicom_path, csv_file_path, tags_in_files, tags_to_exclude):
    tags_in_files = tags_in_files.copy() # copy because we're going to modify
    for tag_to_exclude in tags_to_exclude:
        if tag_to_exclude in tags_in_files:
            del tags_in_files[tag_to_exclude]
    
    # sort by group and then element number
    tags_in_files = OrderedDict(sorted(tags_in_files.items(), key=(lambda k: (k[1][0], k[1][1]))))
    dicom_file_paths = file_paths(filtered_walk(dicom_path, included_files=['*.dcm']))

    with open(csv_file_path, 'w') as f:
        writer = csv.writer(f)
        
        # write the headers
        header_row = list(tags_in_files.keys())
        header_row.append('FilePath')
        writer.writerow(header_row)

        # write the rows
        for dicom_file_path in dicom_file_paths:
            dicom_file = pydicom.read_file(dicom_file_path)

            row_vals = []
            for keyword in tags_in_files:
                tag_val = dicom_file.get(keyword)
                
                if tag_val is None:
                    tag_val = ''
                else:
                    if isinstance(tag_val, Sequence) and not isinstance(tag_val, (str, bytes, bytearray)):
                        tag_val = '^'.join([str(x) for x in tag_val])
                    elif not isinstance(tag_val, str):
                        tag_val = str(tag_val)

                    tag_val = tag_val.replace(',','^').replace('\n', '').replace('\r','')
                row_vals.append(tag_val)

            row_vals.append(dicom_file_path)
            writer.writerow(row_vals)


if __name__ == "__main__":
    osx = platform.system().lower() == "darwin"
    if osx:
        # osx
        dicom_path = os.path.abspath('%s/Documents/_data/out' %os.path.expanduser('~'))
        validate_path = os.path.abspath('%s/Documents/_data/validate' %os.path.expanduser('~'))
    else:
        # win
        dicom_path = os.path.abspath('f:\\data\\out')
        validate_path = os.path.abspath('f:\\data\\validate')

    tag_file_path = os.path.join(validate_path, 'tags_in_files.csv')
    csv_file_path = os.path.join(validate_path, 'dicom.csv')

    tags_in_files = get_tags_in_files(dicom_path, tag_file_path)    
    # print(tags_in_files)

    tags_in_files = load_tags_in_files(tag_file_path)
    tags_to_exclude = {'PixelData': ['0x7fe0','0x0010','Pixel Data','PixelData']}
    directory_to_csv(dicom_path, csv_file_path, tags_in_files, tags_to_exclude)
