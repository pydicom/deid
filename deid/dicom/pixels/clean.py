"""

clean.py: functions for pixel scrubbing

Copyright (c) 2017-2021 Vanessa Sochat

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
import math
import numpy
import os
import random
import re
import sys

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
        """detect will initiate the cleaner for a new dicom file."""
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

            # Compile coordinates from result, generate list of tuples with coordinate and value
            # keepcoordinates == 1 (included in mask) and coordinates == 0 (remove).
            coordinates = []

            for item in self.results["results"]:

                # We iterate through coordinates in order specified in file
                for coordinate_set in item.get("coordinates", []):

                    # Each is a list with [value, coordinate]
                    mask_value, new_coordinates = coordinate_set

                    if not isinstance(new_coordinates, list):
                        new_coordinates = [new_coordinates]

                    for new_coordinate in new_coordinates:

                        # Case 1: an "all" indicates applying to entire image
                        if new_coordinate.lower() == "all":

                            # 2D - Greyscale Image - Shape = (X, Y) OR 3D - RGB Image - Shape = (X, Y, Channel)
                            if len(self.original.shape) == 2 or (
                                len(self.original.shape) == 3
                                and dicom.SamplesPerPixel == 3
                            ):
                                # minr, minc, maxr, maxc = [0, 0, Y, X]
                                new_coordinate = [
                                    0,
                                    0,
                                    self.original.shape[1],
                                    self.original.shape[0],
                                ]

                            # 4D - RGB Cine Clip - Shape = (frames, X, Y, channel) OR 3D - Greyscale Cine Clip - Shape = (frames, X, Y)
                            if len(self.original.shape) == 4 or (
                                len(self.original.shape) == 3
                                and dicom.SamplesPerPixel == 1
                            ):
                                new_coordinate = [
                                    0,
                                    0,
                                    self.original.shape[2],
                                    self.original.shape[1],
                                ]
                        else:
                            new_coordinate = [int(x) for x in new_coordinate.split(",")]
                        coordinates.append(
                            (mask_value, new_coordinate)
                        )  # [(1, [1,2,3,4]),...(0, [1,2,3,4])]

            # Instead of writing directly to data, create a mask of 1s (start keeping all)
            # For 4D RGB Cine - (frames, X, Y, channel) or 3D Greyscale Cine - (frames, X, Y)
            if len(self.original.shape) == 4 or (
                len(self.original.shape) == 3 and dicom.SamplesPerPixel == 1
            ):
                mask = numpy.ones(self.original.shape[1:3], dtype=numpy.uint8)
            # For 2D Greyscale image (X, Y) or 3D RGB Image (X, Y channel)
            else:
                mask = numpy.ones(self.original.shape[0:2], dtype=numpy.uint8)

            # Here we apply the coordinates to the mask, 1==keep, 0==clean
            for coordinate_value, coordinate in coordinates:
                minr, minc, maxr, maxc = coordinate

                # Update the mask: values set to 0 to be black
                mask[minc:maxc, minr:maxr] = coordinate_value

            # Now apply finished mask to the data
            # RGB cine clip
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

            # RGB image or Greyscale cine clip
            elif len(self.original.shape) == 3:

                # This condition is ambiguous.  If the image shape is 3, we may have a single frame RGB image: size (X, Y, channel)
                # or a multiframe greyscale image: size (frames, X, Y).  Interrogate the SamplesPerPixel field.
                if dicom.SamplesPerPixel == 3:
                    # RGB Image
                    # Convert (X, Y) -> (X, Y, channel)
                    final_mask = numpy.transpose(
                        numpy.tile(mask, (self.original.shape[2], 1, 1)), (1, 2, 0)
                    )
                else:
                    # Greyscale cine clip
                    # Convert (X, Y) -> (frames, X, Y)
                    final_mask = numpy.tile(mask, (self.original.shape[0], 1, 1))

                # apply final 3D mask to 3D pixel data
                self.cleaned = final_mask * self.original

            # greyscale image: no need to stack into the channel dim since it doesn't exist
            elif len(self.original.shape) == 2:
                self.cleaned = mask * self.original

            else:
                bot.warning(
                    "Pixel array dimension %s is not recognized."
                    % (str(self.original.shape))
                )

    def get_figure(self, show=False, image_type="cleaned", title=None):
        """get a figure for an original or cleaned image. If the image
        was already clean, it is simply a copy of the original.
        If show is True, plot the image. If a 4d image is discovered, we use
        randomly choose a slice.
        """
        if hasattr(self, image_type):
            _, ax = plt.subplots(figsize=(10, 6))

            # Retrieve full image
            image = getattr(self, image_type)

            # Handle 4d data by choosing one dimension
            if len(image.shape) == 4:
                channel = random.choice(range(image.shape[3]))
                bot.warning(
                    "Image detected as 4d, will sample channel %s and middle slice"
                    % channel
                )
                image = image[math.floor(image.shape[0] / 2), :, :, channel]

            ax.imshow(image, cmap=self.cmap)
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
            os.makedirs(output_folder)

        basename = re.sub("[.]dicom|[.]dcm", "", os.path.basename(self.dicom_file))
        return "%s/cleaned-%s.%s" % (output_folder, basename, extension)

    def save_png(self, output_folder=None, image_type="cleaned", title=None):
        """save an original or cleaned dicom as png to disk. Default
        image_format is "cleaned" and can be set to "original." If the image
        was already clean (not flagged) the cleaned image is just a
        copy of original. If a 4d image is provided, we save the dimension
        specified (or if not provided, a randomly chosen dimension).
        """
        if hasattr(self, image_type):
            png_file = self._get_clean_name(output_folder, "png")
            plt = self.get_figure(image_type=image_type, title=title)
            plt.savefig(png_file)
            plt.close()
            return png_file
        else:
            bot.warning("use detect() --> clean() before saving is possible.")

    def save_animation(self, output_folder=None, image_type="cleaned", title=None):
        """save an original or cleaned animation of a dicom. If there are not
        enough frames, then save_png should be used instead.
        """
        if hasattr(self, image_type):
            from matplotlib import animation, rc

            animation.rcParams["animation.writer"] = "ffmpeg"

            image = getattr(self, image_type)

            # If we have rgb, choose a channel

            if len(image.shape) == 4:
                channel = random.choice(range(image.shape[3]))
                bot.warning("Selecting channel %s for rendering" % channel)
                image = image[:, :, :, channel]

            # Now we expect 3D, we can animate one dimension over time
            if len(image.shape) == 3:
                movie_file = self._get_clean_name(output_folder, "mp4")

                # First set up the figure, the axis, and the plot element we want to animate
                fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))
                plt.close()
                ax.xlim = (0, image.shape[1])
                ax.ylim = (0, image.shape[2])
                ax.set_xticks([])
                ax.set_yticks([])
                img = ax.imshow(image[0, :, :].T, cmap="gray")
                img.set_interpolation("nearest")

                # The animation function should take an index i
                def animate(i):
                    img.set_data(image[i, :, :].T)
                    sys.stdout.flush()
                    return (img,)

                bot.info("Generating animation...")
                anim = animation.FuncAnimation(
                    fig, animate, frames=image.shape[0], interval=50, blit=True
                )
                anim.save(
                    movie_file,
                    writer="ffmpeg",
                    fps=10,
                    dpi=100,
                    metadata={"title": title or "deid-animation"},
                )
                return movie_file
            else:
                bot.warning(
                    "save_animation() is only for 4D data. Use save_png instead."
                )
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
