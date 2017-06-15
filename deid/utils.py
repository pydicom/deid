#!/usr/bin/env python

'''
utils.py: part of deid package

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

import collections
import fnmatch
import os
import json
import re
import requests

import shutil
import json
import som.__init__ as hello
from deid.logger import bot
import sys

import subprocess

import tempfile
import tarfile
import zipfile


# Python less than version 3 must import OSError
if sys.version_info[0] < 3:
    from exceptions import OSError


######################################################################################
# Local commands and requests
######################################################################################

def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(__file__))


def run_command(cmd,error_message=None,sudopw=None,suppress=False):
    '''run_command uses subprocess to send a command to the terminal.
    :param cmd: the command to send, should be a list for subprocess
    :param error_message: the error message to give to user if fails, 
    if none specified, will alert that command failed.
    :param execute: if True, will add `` around command (default is False)
    :param sudopw: if specified (not None) command will be run asking for sudo
    '''
    if sudopw == None:
        sudopw = os.environ.get('pancakes',None)

    if sudopw != None:
        cmd = ' '.join(["echo", sudopw,"|","sudo","-S"] + cmd)
        if suppress == False:
            output = os.popen(cmd).read().strip('\n')
        else:
            output = cmd
            os.system(cmd)
    else:
        try:
            process = subprocess.Popen(cmd,stdout=subprocess.PIPE)
            output, err = process.communicate()
        except OSError as error: 
            if error.errno == os.errno.ENOENT:
                bot.error(error_message)
            else:
                bot.error(err)
            return None
    
    return output



############################################################################
## FILE OPERATIONS #########################################################
############################################################################

def write_file(filename,content,mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj,filename,mode="w",print_pretty=True):
    '''write_json will (optionally,pretty print) a json object to file
    :param json_obj: the dict to print to json
    :param filename: the output file to write to
    :param pretty_print: if True, will use nicer formatting   
    '''
    with open(filename,mode) as filey:
        if print_pretty == True:
            filey.writelines(json.dumps(json_obj, indent=4, separators=(',', ': ')))
        else:
            filey.writelines(json.dumps(json_obj))
    return filename



def read_file(filename,mode="r"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    with open(filename,mode) as filey:
        content = filey.readlines()
    return content



def read_json(filename,mode="r"):
    '''read_json will open a file, "filename" and read the string as json
    '''
    with open(filename,mode) as filey:
        content = json.loads(filey.read())
    return content




def recursive_find(base,pattern=None):
    '''recursive find dicoms will search for dicom files in all directory levels
    below a base. It uses get_dcm_files to find the files in the bases.
    '''
    if pattern is None:
        pattern = "*"
    files = []
    for root, dirnames, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            files.append(os.path.join(root, filename))

    return files



############################################################################
## COMPRESSED FILES ########################################################
############################################################################


def detect_compressed(folder,compressed_types=None):
    '''detect compressed will return a list of files in 
    some folder that are compressed, by default this means
    .zip or .tar.gz, but the called can specify a custom list
    :param folder: the folder base to use.
    :param compressed_types: a list of types to include, should
    be extensions in format like *.tar.gz, *.zip, etc.
    '''
    compressed = []
    if compressed_types == None:
        compressed_types = ["*.tar.gz",'*zip']
    bot.debug("Searching for %s" %", ".join(compressed_types))

    for filey in os.listdir(folder):
        for compressed_type in compressed_types:
            if fnmatch.fnmatch(filey, compressed_type):
                compressed.append("%s/%s" %(folder,filey))
    bot.debug("Found %s compressed files in %s" %len(compressed),folder)
    return compressed


def unzip_dir(zip_file,dest_dir=None):
    '''unzip_dir will extract a zipfile to a directory. If
    an extraction destination is not defined, a temporary
    directory will be created and used.
    :param zip_file: the .zip file to unzip
    :param dest_dir: the destination directory
    '''

    if dest_dir == None:
        dest_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(zip_file,"r") as zf:
        zf.extractall(dest_dir)
    return dest_dir



def zip_dir(zip_dir, zip_name, output_folder=None):
    '''zip_dir will zip up and entire zip directory
    :param folder_path: the folder to zip up
    :param zip_name: the name of the zip to return
    :output_folder:
    '''
    tmpdir = tempfile.mkdtemp()
    output_zip = "%s/%s" %(tmpdir,zip_name)
    zf = zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, allowZip64=True)
    for root, dirs, files in os.walk(zip_dir):
        for file in files:
            zf.write(os.path.join(root, file))
    zf.close()
    if output_folder != None:
        shutil.copyfile(output_zip,"%s/%s"%(output_folder,zip_name))
        shutil.rmtree(tmpdir)
        output_zip = "%s/%s"%(output_folder,zip_name)
    return output_zip



def untar_dir(tar_file,dest_dir=None):
    '''untar_dir will extract a tarfile to a directory. If
    an extraction destination is not defined, a temporary
    directory will be created and used.
    :param tar_file: the .tar.gz file to untar/decompress
    :param dest_dir: the destination directory
    '''

    if dest_dir == None:
        dest_dir = tempfile.mkdtemp()

    contents = []
    if tarfile.is_tarfile(tar_file):
        with tarfile.open(tar_file) as tf:
            tf.extractall(dest_dir)
    return dest_dir
