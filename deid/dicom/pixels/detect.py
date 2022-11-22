__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"


from typing import List, Optional, Union

from pydicom import FileDataset, read_file
from pydicom.sequence import Sequence

from deid.config import DeidRecipe
from deid.dicom.filter import apply_filter
from deid.logger import bot


def has_burned_pixels(
    dicom_files, force: bool = True, deid: Optional[DeidRecipe] = None
):
    """
    Determine if a dicom file has burned pixels.

    has_burned_pixels is an entrypoint for has_burned_pixels_multi (for
    multiple images) or has_burned_pixels_single (for one detailed repor)
    We will use the MIRCTP criteria (see ref folder with the
    original scripts used by CTP) to determine if an image is likely to have
    PHI, based on fields in the header alone. This script does NOT perform
    pixel cleaning, but returns a dictionary of results (for multi) or one
    detailed result (for single)
    """
    # if the user has provided a custom deid, load it
    if not isinstance(deid, DeidRecipe):
        if deid is None:
            deid = "dicom"
        deid = DeidRecipe(deid)

    if isinstance(dicom_files, list):
        return _has_burned_pixels_multi(dicom_files, force, deid)
    return _has_burned_pixels_single(dicom_files, force, deid)


def _has_burned_pixels_multi(dicom_files: List[Union[str, FileDataset]], force, deid):
    """
    Determine if one or more dicom files have burned pixels.

    return a summary dictionary with lists of clean, and then lookups
    for flagged images with reasons. The deid should be a deid recipe
    instantiated from deid.config.DeidRecipe. This function should not
    be called directly, but should be called from has_burned_pixels
    """

    # Store decisions in lookup based on filter groups
    decision = {"clean": [], "flagged": {}}

    for dicom_file in dicom_files:
        result = _has_burned_pixels_single(
            dicom_file=dicom_file, force=force, deid=deid
        )

        if result["flagged"] is False:
            # In this case, group is None
            decision["clean"].append(dicom_file)
        else:
            decision["flagged"][dicom_file] = result

    return decision


def _has_burned_pixels_single(dicom_file, force: bool, deid):

    """
    Determine if a single dicom has burned pixels.

    has burned pixels single will evaluate one dicom file for burned in
    pixels based on 'filter' criteria in a deid. If deid is not provided,
    will use application default. The method proceeds as follows:

    1. deid is loaded, with criteria groups ordered from specific --> general
    2. image is run down the criteria, stops when hits and reports FLAG
    3. passing through the entire list gives status of pass

    The default deid has a greylist, whitelist, then blacklist

    Parameters
    =========
    dicom_file: the fullpath to the file to evaluate
    force: force reading of a potentially erroneous file
    deid: the full path to a deid specification. if not defined, only default used

    deid['filter']['dangerouscookie'] <-- filter list "dangerouscookie"

    --> This is what an item in the criteria looks like
         [{'coordinates': ['0,0,512,110'],
           'filters': [{'InnerOperators': [],
           'action': ['notequals'],
           'field': ['OperatorsName'],
           'operator': 'and',
           'value': ['bold bread']}],
         'name': 'criteria for dangerous cookie'}]


    Returns
    =======
    --> This is what a clean image looks like:
        {'flagged': False, 'results': []}

    --> This is what a flagged image looks like:
       {'flagged': True,
        'results': [
               {'reason': ' ImageType missing  or ImageType empty ',
                'group': 'blacklist',
                'coordinates': []}
            ]
        }
    """
    if isinstance(dicom_file, FileDataset):
        dicom = dicom_file
    else:
        dicom = read_file(dicom_file, force=force)

    # Return list with lookup as dicom_file
    results = []
    global_flagged = False

    # Load criteria (actions) for flagging
    filters = deid.get_filters()
    if not filters:
        bot.warning("Deid provided does not have %filter.")
        return {"flagged": global_flagged, "results": results}

    for name, items in filters.items():
        for item in items:
            flags = []

            descriptions = []  # description for each group across items

            # If there aren't any filters but we have coordinates, assume True
            if not item.get("filters") and item.get("coordinates"):
                group_flags = [True]
                group_descriptions = [item.get("name", "")]

            else:
                group_flags = []  # evaluation for a single line
                group_descriptions = []
                for group in item["filters"]:

                    # You cannot pop from the list
                    for a in range(len(group["action"])):

                        action = group["action"][a]
                        field = group["field"][a]
                        value = ""

                        if len(group["value"]) > a:
                            value = group["value"][a]

                        flag = apply_filter(
                            dicom=dicom,
                            field=field,
                            filter_name=action,
                            value=value or None,
                        )
                        group_flags.append(flag)
                        description = "%s %s %s" % (field, action, value)

                        if len(group["InnerOperators"]) > a:
                            inner_operator = group["InnerOperators"][a]
                            group_flags.append(inner_operator)
                            description = "%s %s" % (description, inner_operator)

                        group_descriptions.append(description)

            # At the end of a group, evaluate the inner group
            flag = evaluate_group(group_flags)

            # "Operator" is relevant for the outcome of the list of actions
            operator = ""
            if "operator" in group:
                if group["operator"] is not None:
                    operator = group["operator"]
                    flags.append(operator)

            flags.append(flag)
            reason = ("%s %s" % (operator, " ".join(group_descriptions))).replace(
                "\n", " "
            )
            descriptions.append(reason)

            # When we parse through a group, we evaluate based on all flags
            flagged = evaluate_group(flags=flags)

            if flagged is True:
                global_flagged = True
                reason = " ".join(descriptions)

                # Each coordinate is a list with [value, [coordinate]]
                # and if from: in the coordinate value, it indicates we get
                # the coordinate from some field (done here)
                for coordset in item["coordinates"]:
                    if "from:" in coordset[1]:
                        coordset[1] = extract_coordinates(dicom, coordset[1])

                result = {
                    "reason": reason,
                    "group": name,
                    "coordinates": item["coordinates"],
                }

                results.append(result)

    results = {"flagged": global_flagged, "results": results}
    return results


def evaluate_group(flags):
    """
    Evaluate group will take a list of flags (e.g.,

     [True, and, False, or, True]

    And read through the logic to determine if the image result
    is to be flagged. This is how we combine a set of criteria in
    a group to come to a final decision.
    """
    flagged = False
    first_entry = True

    # If it starts with and and/or, remove it
    if flags and flags[0] in ["and", "or"]:
        flags.pop(0)

    while len(flags) > 0:
        flag = flags.pop(0)
        if flag == "and":
            flag = flags.pop(0)
            flagged = flag and flagged
        elif flag == "or":
            flag = flags.pop(0)
            flagged = flag or flagged
        else:
            # If it's the first entry
            if first_entry is True:
                flagged = flag
            else:
                flagged = flagged and flag
        first_entry = False

    return flagged


def extract_coordinates(dicom, field):
    """
    Given a field that is provided for a dicom, extract coordinates
    """
    field = field.replace("from:", "", 1)
    coordinates = []
    if field not in dicom:
        return coordinates

    regions = []
    region = dicom.get(field)

    # First put list of attributes together
    if isinstance(region, Sequence):
        for entry in region:
            regions.append(entry)
    else:
        regions.append(region)

    # Now extract coordinates
    for region in regions:

        if (
            "RegionLocationMinX0" in region
            and "RegionLocationMinY0" in region
            and "RegionLocationMaxX1" in region
            and "RegionLocationMaxY1" in region
        ):

            # https://gist.github.com/vsoch/df6957be12c34e62b21000603f1687e5
            # minr, minc, maxr, maxc = coordinate
            # self.cleaned[minc:maxc, minr:maxr] = 0  # should fill with black
            # self.cleaned[A:B, C:D]
            # image[A:B,C:D]
            # A: refers to ymin
            # B: refers to ymax
            # C: refers xmin
            # D: refers to xmax
            # self.cleaned[ymin:ymax, xmin:xmax]
            # coordinate must be [xmin, ymin, xmax, ymax]
            # x0,y0,x1,y1.
            coordinates.append(
                "%s,%s,%s,%s"
                % (
                    region.RegionLocationMinX0,
                    region.RegionLocationMinY0,
                    region.RegionLocationMaxX1,
                    region.RegionLocationMaxY1,
                )
            )
    return coordinates
