'''
clean.py: functions for pixel scrubbing

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

from deid.logger import bot
from pydicom import read_file
import matplotlib
matplotlib.use('pdf')
import tempfile
import os
import re

bot.level = 3

class DicomCleaner():
    '''take an input dicom file, check for burned pixels, and then clean,
       with option to save / output in multiple formats. This object should
       map to one dicom file, and the usage flow is the following:

       cleaner = DicomCleaner()
       summary = cleaner.detect(dicom_file)
      
       cleaner.clean()
    '''
    
    def __init__(self, output_folder=None,
                       add_padding=False,
                       margin=3,
                       deid=None,
                       font=None):

        if output_folder is None:
            output_folder = tempfile.mkdtemp()

        if font is None:
            font = self.default_font
        self.font = font

        self.output_folder = output_folder
        self.deid = deid
        self.results = None

    def default_font(self):
        '''define the font style for saving png figures
           if a title is provided
        '''
        return {'family': 'serif',
                'color':  'darkred',
                'weight': 'normal',
                'size': 16}

    def detect(self, dicom_file):
        '''detect will initiate the cleaner for a new dicom file.
        '''
        from deid.dicom.pixels.detect import has_burned_pixels
        self.results = has_burned_pixels(dicom_file)
        self.dicom_file = dicom_file
        return self.results
        

    def clean(self):
        '''
        take a dicom image and a list of pixel coordinates, and return
        a cleaned file (if output file is specified) or simply plot 
        the cleaned result (if no file is specified)
    
        Parameters
        ==========
            add_padding: add N=margin pixels of padding
            margin: pixels of padding to add, if add_padding True
        '''

        if not self.results:
            bot.warning('Use %s.detect() to find coordinates first.' %self)

        elif self.results['flagged'] is False:
            bot.info('Image was not flagged, nothing to clean.' %self)

        else:
            bot.info('Cleaning %s.' %self.dicom_file)

            # Load in dicom file, and image data
            dicom = read_file(self.dicom_file,force=True)

            # We will set original image to image, cleaned to clean
            self.original = dicom._get_pixel_array()
            self.cleaned = self.original.copy()

            # Compile coordinates from result
            coordinates = []
            for item in self.results['results']:
                if len(item['coordinates']) > 0:
                    coordinates.append(item['coordinates']) # [[1,2,3,4],...[1,2,3,4]]

            print("Blanking %s coordinate boxes" %(len(coordinates)))
            for coordinate in coordinates:
                minr, minc, maxr, maxc = coordinate
                self.cleaned[minr:maxr, minc:maxc] = 0  # should fill with black
                                           

    def get_figure(self, show=False, image_type="cleaned", title=None):
        '''get a figure for an original or cleaned image. If the image
           was already clean, it is simply a copy of the original.
           If show is True, plot the image.
        '''
        from matplotlib import pyplot as plt
        
        if hasattr(self, image_type):
            fig, ax = plt.subplots(figsize=(10, 6))      
            ax.imshow(self.cleaned)
            if title is not None:
                plt.title(title, fontdict=self.font)
            if show is True:
                plt.show()
            return plt


    def _get_clean_name(self, extension='dcm'):
        basename = re.sub('[.]dicom|[.]dcm', '', os.path.basename(self.dicom_file))
        return "%s/cleaned-%s.%s" %(output_folder, basename, extension)
        
    def save_png(self, output_folder=None, image_type="cleaned", title=None):
        '''save an original or cleaned dicom as png to disk.
           Default image_format is "cleaned" and can be set 
           to "original." If the image was already clean (not 
           flagged) the cleaned image is just a copy of original
        '''
        from matplotlib import pyplot as plt
        
        if output_folder is None:
            output_folder = self.output_folder

        if hasattr(self,image_type):
            png_file = self._get_clean_name('png')
            plt = self.get_figure(image_type=image_type, title=title)
            plt.savefig(png_file)
            plt.close()


    def save_dicom(self, output_folder=None, image_type="cleaned"):
        '''save a cleaned dicom to disk. We expose an option to save
           an original (change image_type to "original" to be consistent,
           although this is not incredibly useful given it would duplicate
           the original data.
        '''
        if output_folder is None:
            output_folder = self.output_folder

        # Having clean also means has dicom image
        if hasattr(self, image_type):
            dicom_name = self._get_clean_name()
            dicom = read_file(self.dicom_file,force=True)
            dicom.PixelData = self.clean.tostring()
            dicom.save_as(dicom_name)
            return dicom_name
        else:
            bot.warning('use detect() --> clean() before saving clean is possible.')
