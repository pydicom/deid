"""

clean.py: functions for pixel scrubbing

Copyright (c) 2017-2020 Vanessa Sochat

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

"""

from pydicom.pixel_data_handlers.util import get_expected_length
from deid.config import DeidRecipe
from deid.logger import bot
from deid.utils import get_temporary_name
from pydicom import read_file
import matplotlib
import numpy
import os
import re

matplotlib.use("pdf")

from matplotlib import pyplot as plt

bot.level = 3


class DicomCleaner:
    """take an input dicom file, check for burned pixels, and then clean,
       with option to save / output in multiple formats. This object should
       map to one dicom file, and the usage flow is the following:
       cleaner = DicomCleaner()
       summary = cleaner.detect(dicom_file)
      
       cleaner.clean()
    """

    def __init__(
        self,
        output_folder=None,
        add_padding=False,
        margin=3,
        deid=None,
        font=None,
        force=True,
    ):

        if output_folder is None:
            output_folder = get_temporary_name(prefix="clean")

        if font is None:
            font = self.default_font()
        self.font = font
        self.cmap = "gray"
        self.output_folder = output_folder
        self.recipe = DeidRecipe(deid)
        self.results = None
        self.force = force

    def default_font(self):
        """define the font style for saving png figures
           if a title is provided
        """
        return {"family": "serif", "color": "darkred", "weight": "normal", "size": 16}

    def detect(self, dicom_file):
        """detect will initiate the cleaner for a new dicom file.
        """
        from deid.dicom.pixels.detect import has_burned_pixels

        self.results = has_burned_pixels(
            dicom_file, deid=self.recipe.deid, force=self.force
        )
        self.dicom_file = dicom_file
        return self.results

    def clean(self, fix_interpretation=True, pixel_data_attribute="PixelData"):
        """
        take a dicom image and a list of pixel coordinates, and return
        a cleaned file (if output file is specified) or simply plot 
        the cleaned result (if no file is specified)
    
        Parameters
        ==========
            add_padding: add N=margin pixels of padding
            margin: pixels of padding to add, if add_padding True
            fix_interpretation: fix the photometric interpretation if found off
        """

        if not self.results:
            bot.warning("Use %s.detect() to find coordinates first." % self)

        else:
            bot.info("Scrubbing %s." % self.dicom_file)

            # Load in dicom file, and image data
            dicom = read_file(self.dicom_file, force=True)
            pixel_data = getattr(dicom, pixel_data_attribute)

            # Get expected and actual length of the pixel data (bytes, expected does not include trailing null byte)
            expected_length = get_expected_length(dicom)
            actual_length = len(pixel_data)
            padded_expected_length = expected_length + expected_length % 2
            full_length = expected_length / 2 * 3  # upsampled data is a third larger
            full_length += (
                1 if full_length % 2 else 0
            )  # trailing padding byte if even length

            # If we have YBR_FULL_2, must be RGB to obtain pixel data
            if (
                not dicom.file_meta.TransferSyntaxUID.is_compressed
                and dicom.PhotometricInterpretation == "YBR_FULL_422"
                and fix_interpretation
                and actual_length >= full_length
            ):
                bot.warning(
                    "Updating dicom.PhotometricInterpretation to RGB, set fix_interpretation to False to skip."
                )
                photometric_original = dicom.PhotometricInterpretation
                dicom.PhotometricInterpretation = "RGB"
                self.original = dicom.pixel_array
                dicom.PhotometricInterpretation = photometric_original
            else:
                self.original = dicom.pixel_array

            # Compile coordinates from result
            coordinates = []
            for item in self.results["results"]:
                if len(item["coordinates"]) > 0:
                    for coordinate_set in item["coordinates"]:
                        # Coordinates expected to be list separated by commas
                        new_coordinates = [int(x) for x in coordinate_set.split(",")]
                        coordinates.append(new_coordinates)  # [[1,2,3,4],...[1,2,3,4]]

            # Instead of writing directly to data, create a mask
            # For 4D, (frames, X, Y, channel)
            if len(self.original.shape) == 4:
                mask = numpy.zeros(self.original.shape[1:3], dtype=numpy.uint8)

            # For 3D, (X, Y, channel)
            else:
                mask = numpy.zeros(self.original.shape[0:2], dtype=numpy.uint8)

            for coordinate in coordinates:
                minr, minc, maxr, maxc = coordinate

                # Update the mask: values set to 0 to be black
                mask[minc:maxc, minr:maxr] = 1

            # Now apply finished mask to the data
            if len(self.original.shape) == 4:

                # np.tile does the copying and stacking of masks into the channel dim to produce 3D masks
                # transposition to convert tile output (channel, X, Y)  into (X, Y, channel)
                # see: https://github.com/nquach/anonymize/blob/master/anonymize.py#L154
                channel3mask = numpy.transpose(numpy.tile(mask, (3, 1, 1)), (1, 2, 0))

                # use numpy.tile to copy and stack the 3D masks into 4D array to apply to 4D pixel data
                # tile converts (X, Y, channels) -> (frames, X, Y, channels), presumed ordering for 4D pixel data
                final_mask = numpy.tile(channel3mask, (self.original.shape[0], 1, 1, 1))

                # apply final 4D mask to 4D pixel data
                self.cleaned = final_mask * self.original

            # greyscale: no need to stack into the channel dim since it doesnt exist
            elif len(self.original.shape) == 3:

                # numpy.tile converts (X, Y) -> (frames, X, Y)
                final_mask = numpy.tile(mask, (self.original.shape[0], 1, 1))
                self.cleaned = final_mask * self.original

            else:
                bot.warning(
                    "Pixel array dimension %s is not recognized."
                    % (self.original.shape)
                )

    def get_figure(self, show=False, image_type="cleaned", title=None):
        """get a figure for an original or cleaned image. If the image
           was already clean, it is simply a copy of the original.
           If show is True, plot the image.
        """
        if hasattr(self, image_type):
            _, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(self.cleaned, cmap=self.cmap)
            if title is not None:
                plt.title(title, fontdict=self.font)
            if show is True:
                plt.show()
            return plt

    def _get_clean_name(self, output_folder, extension="dcm"):
        """return a full path to an output file, with custom folder and
           extension. If the output folder isn't yet created, make it.
 
           Parameters
           ==========
           output_folder: the output folder to create, will be created if doesn't
           exist.
           extension: the extension of the file to create a name for, should
           not start with "."
        """
        if output_folder is None:
            output_folder = self.output_folder

        if not os.path.exists(output_folder):
            bot.debug("Creating output folder %s" % output_folder)
            os.mkdir(output_folder)

        basename = re.sub("[.]dicom|[.]dcm", "", os.path.basename(self.dicom_file))
        return "%s/cleaned-%s.%s" % (output_folder, basename, extension)

    def save_png(self, output_folder=None, image_type="cleaned", title=None):
        """save an original or cleaned dicom as png to disk.
           Default image_format is "cleaned" and can be set 
           to "original." If the image was already clean (not 
           flagged) the cleaned image is just a copy of original
        """
        if hasattr(self, image_type):
            png_file = self._get_clean_name(output_folder, "png")
            plt = self.get_figure(image_type=image_type, title=title)
            plt.savefig(png_file)
            plt.close()
            return png_file
        else:
            bot.warning("use detect() --> clean() before saving is possible.")

    def save_dicom(self, output_folder=None, image_type="cleaned"):
        """save a cleaned dicom to disk. We expose an option to save
           an original (change image_type to "original" to be consistent,
           although this is not incredibly useful given it would duplicate
           the original data.
        """
        # Having clean also means has dicom image
        if hasattr(self, image_type):
            dicom_name = self._get_clean_name(output_folder)
            dicom = read_file(self.dicom_file, force=True)
            # If going from compressed, change TransferSyntax
            if dicom.file_meta.TransferSyntaxUID.is_compressed is True:
                dicom.decompress()
            dicom.PixelData = self.cleaned.tostring()
            dicom.save_as(dicom_name)
            return dicom_name
        else:
            bot.warning("use detect() --> clean() before saving is possible.")
