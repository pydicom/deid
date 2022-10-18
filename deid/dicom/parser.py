__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

import os
import re
from copy import deepcopy

from pydicom import read_file
from pydicom.dataelem import DataElement
from pydicom.dataset import Dataset
from pydicom.tag import Tag

from deid.config import DeidRecipe
from deid.config.standards import actions as valid_actions
from deid.dicom.actions import deid_funcs, jitter_timestamp
from deid.dicom.fields import DicomField, expand_field_expression, get_fields
from deid.dicom.groups import extract_fields_list, extract_values_list
from deid.dicom.tags import add_tag, get_private, get_tag, remove_sequences
from deid.dicom.utils import save_dicom
from deid.logger import bot
from deid.utils import parse_value, read_json

here = os.path.dirname(os.path.abspath(__file__))


class DicomParser:
    """
    Parse a dicom, performing one or more actions on fields.

    A dicom parser serves as a cache to read in all fields from a dicom
    file. For each, we store the element and child elements
    """

    def __init__(
        self, dicom_file, recipe=None, config=None, force=True, disable_skip=False
    ):
        """
        Create new instance of DicomParser

        :param dicom_file: Path to a dicom file or instance of a pydicom.Dataset
        :param recipe: a deid recipe, defaults to None
        :param config: deid config, defaults to None
        :param force: ignore errors when reading a dicom file, defaults to True
        :param disable_skip: _description_, defaults to False
        """

        # Lookup for the dicom
        self.lookup = {}

        # Will be a list of DicomField
        self.fields = {}

        # Disable skip will load ALL fields, even those protected
        self.disable_skip = disable_skip

        # Load default configuration, or a custom one
        config = config or os.path.join(here, "config.json")
        if not os.path.exists(config):
            bot.error("Cannot find config %s, exiting" % (config))
        self.config = read_json(config, ordered_dict=True)

        # Keep a lookup of deid provided functions
        self.deid_funcs = deid_funcs

        # Deid can be a recipe or filename
        if not isinstance(recipe, DeidRecipe):
            recipe = DeidRecipe(recipe)

        self.load(dicom_file, force=force)
        self.recipe = recipe

    def __str__(self):
        return "[dicom-parser:%s]" % self.dicom_name

    def __repr__(self):
        return self.__str__()

    def load(self, dicom_file, force=True):
        """
        Load the dicom file.

        Ensure that the dicom file exists, and use full path. Here
        we load the file, and save the dicom, dicom_file, and dicom_name.
        """
        # Reset seen, which is generated when we parse
        self.seen = []

        # The user might already have provided a dataset
        if isinstance(dicom_file, Dataset):
            self.dicom = dicom_file
        else:
            # If we must read the file, the path must exist
            if not os.path.exists(dicom_file):
                bot.exit("%s does not exist." % dicom_file)
            self.dicom = read_file(dicom_file, force=force)

        # Set class variables that might be helpful later
        df = self.dicom.get("filename")
        self.dicom_file = None if not df else os.path.abspath(df)
        self.dicom_name = None if not df else os.path.basename(self.dicom_file)

    def define(self, name, value):
        """
        Add a function or variable to the lookup for later usage.

        This can be used for functions, lists, or variables.
        """
        self.lookup[name] = value

    def reset_preamble(self):
        """reset the preamble"""
        # We aren't including preamble, we will reset to be empty 128 bytes
        self.dicom.preamble = b"\0" * 128

    def get_nested_field(self, field, return_parent=False):
        """
        Retrieve a nested field.

        Based on a DicomField, return the one referenced in self.dicom.
        If a delete is needed, then the parent should be returned as well.
        """
        # The field provided will be last in the list, the one we want
        # It is not be nested because fields are stored flat
        uids = field.uid.split("__")

        # Keep a reference to where we are in dicom (can nest)
        if field.is_filemeta:
            parent = self.dicom.file_meta
        else:
            parent = self.dicom  # dicom is of type Dataset
        desired = field.element.tag

        while uids:
            uid = uids.pop(0)

            # If if's a uid for a tag, has parens
            if re.search("[(]|[)]", uid):
                group, element = [
                    x.strip() for x in re.sub("[(]|[)]", "", uid).split(",")
                ]
                group = int(group, 16)
                element = int(element, 16)
                tag = Tag(group, element)

                # We keep going until we find the desired tag
                if tag != desired:

                    # If the parent has been removed, we can't continue
                    if tag not in parent:
                        return None, desired

                    parent = parent[tag]

            # Otherwise it's an index into a sequence
            else:

                # If the parent has been removed, we can't continue
                if not int(uid) in parent:
                    return None, desired
                parent = parent[int(uid)]

        if return_parent:
            return parent, desired
        return desired

    def delete_field(self, field):
        """
        Delete a field from the dicom.

        We do this by way of parsing all nested levels of a tag into actual tags,
        and deleting the child node.
        """
        # Returns the parent, and a DataElement (indexes into parent by tag)
        parent, desired = self.get_nested_field(field, return_parent=True)
        if parent and desired in parent:
            del parent[desired]
            del self.fields[field.uid]

    def blank_field(self, field):
        """
        Blank a field
        """
        element = self.get_nested_field(field)

        # Assert we have a data element, and can blank a string
        if element:
            if not isinstance(element, DataElement):
                bot.warning("Issue parsing %s as a DataElement, not blanked." % field)
            elif element.VR in ["US", "SS"]:
                element.value = ""
            else:
                bot.warning("Unrecognized VR for %s, skipping blank." % field)

    def replace_field(self, field, value):
        """
        Replace a value in a field.

        This uses the same function as ADD, but likely the dicom has the value.
        """
        self.add_field(field, value)

    def parse(self, strip_sequences=False, remove_private=False):
        """
        Parse the dicom.

        The parse action corresponds to iterating through fields, and
        for each one, saving a data structure with the full element,
        the string (with nested representation of the keywords)
        and the tag. We want to save all three in a flat list that is
        easy to search over, and also build up actions for the lookup
        on the first parsing.
        """
        # Remove sequences first, maintained in DataStore
        if strip_sequences is True:
            remove_sequences(self.dicom)

        # Remove private tags at the onset, if requested
        if remove_private:
            self.remove_private()

        # In the parsing, we generate a list of DicomField objects.
        fields = self.get_fields(expand_sequences=True)

        # if we loaded a deid recipe
        if self.recipe.deid is not None:

            # Prepare additional lists of values and lookup fields (index by nested uid)
            if self.recipe.has_values_lists():
                for group, actions in self.recipe.get_values_lists().items():
                    self.lookup[group] = extract_values_list(
                        dicom=self.dicom, actions=actions, fields=fields
                    )

            if self.recipe.has_fields_lists():
                for group, actions in self.recipe.get_fields_lists().items():
                    self.lookup[group] = extract_fields_list(
                        dicom=self.dicom, actions=actions, fields=fields
                    )

            # actions on the header
            for action in self.recipe.get_actions():
                self.perform_action(
                    field=action.get("field"),
                    value=action.get("value"),
                    action=action.get("action"),
                )

        # Next perform actions in default config, only if not done
        for action in self.config["put"]["actions"]:
            self.perform_action(
                field=action.get("field"),
                value=action.get("value"),
                action=action.get("action"),
            )

        # At this point the self.dicom should be updated fully
        # The user can save, or take other action

    def save(self, filename, overwrite=False):
        """
        Save a dicom to file.
        """
        filename = filename or self.dicom_file
        ds = save_dicom(
            dicom=self.dicom,
            dicom_file=os.path.basename(filename),
            output_folder=os.path.dirname(filename),
            overwrite=overwrite,
        )
        return ds

    @property
    def skip(self):
        """
        Return a list of fields to skip, as defined in the self.config
        """
        skips = []
        if self.config and not self.disable_skip:
            skips = self.config.get("get", {}).get("skip", {})
        return skips

    def get_fields(self, expand_sequences=True):
        """expand all dicom fields into a list, where each entry is
        a DicomField. If we find a sequence, we unwrap it and
        represent the location with the name (e.g., Sequence__Child)
        """
        if not self.fields:
            self.fields = get_fields(
                dicom=self.dicom,
                expand_sequences=expand_sequences,
                seen=self.seen,
                skip=self.skip,
            )
        return self.fields

    def find_by_values(self, values):
        """
        Find fields by values.

        Given a list of values, find fields in the dicom that contain any
        of those values, as determined by a regular expression search.
        """
        # Values must be strings
        values = [str(x) for x in values]

        fields = {}

        if values:
            # Create single regular expression to search by
            regexp = "(%s)" % "|".join(values)
            for uid, field in self.fields.items():
                if field.value_contains(regexp):
                    fields[uid] = field
        else:
            bot.warning("Empty values list encountered.  No fields will be identified.")

        return fields

    def find_by_name(self, name):
        """
        Find fields by name.

        Given a string, find all field objects that contain the name.
        Name can correspond to:
         - a string of the tag, with or without the parens and comma/space
         - a keyword
         - a field name
        """
        fields = {}

        # Create single regular expression to search by
        for uid, field in self.fields.items():
            if field.name_contains(name):
                fields[uid] = field

        return fields

    # Actions

    def perform_action(self, field, value, action, filemeta=False):
        """
        Perform an action on a field.

        perform action takes an action (dictionary with field, action, value)
        and performs the action on the loaded dicom.

        Parameters
        ==========
        fields: if provided, a filtered list of fields for expand
        action: the action from the parsed deid to take
           "field" (eg, PatientID) the header field to process
           "action" (eg, REPLACE) what to do with the field
           "value": if needed, the field from the response to replace with
        filemeta (bool) perform on filemeta
        """
        # Validate the action
        if action not in valid_actions:
            bot.warning("%s in not a valid choice. Defaulting to blanked." % action)
            action = "BLANK"

        # A values list returns fields with the value (can be private tags if not removed)
        if re.search("^values", field):
            values = self.lookup.get(re.sub("^values:", "", field), [])
            fields = self.find_by_values(values=values)

        # A fields list is used vertbatim
        # In expand_field_expression below, the stripped_tag is being passed in to field.  At this point,
        # expanders for %fields lists have already been processed and each of the contenders is an
        # identified, unique field.  It is important to use stripped_tag at this point instead of
        # element.keyword as private tags will not have a keyword and can only be identified by tag number.
        elif re.search("^fields", field):
            listing = {}
            for uid, contender in self.lookup.get(
                re.sub("^fields:", "", field), {}
            ).items():
                listing.update(
                    expand_field_expression(
                        field=contender.stripped_tag,
                        dicom=self.dicom,
                        contenders=self.fields,
                    )
                )
            fields = listing

        else:
            # If there is an expander applied to field, we iterate over
            fields = expand_field_expression(
                field=field, dicom=self.dicom, contenders=self.fields
            )

        # If it's an addition, we might not have fields
        if action == "ADD":
            self.add_field(field, value)

        # Otherwise, these are operations on existing fields
        else:
            # without deepcopy - "dictionary changed size during iterations"
            temp_fields = deepcopy(fields)
            for uid, field in temp_fields.items():
                self._run_action(field=field, action=action, value=value)

    def add_field(self, field, value):
        """
        Add a field to the dicom.

        If it's already present, update the value.
        """
        value = parse_value(
            item=self.lookup,
            value=value,
            field=field,
            dicom=self.dicom,
            funcs=self.deid_funcs,
        )

        # The addition will be different depending on if we have filemeta
        is_filemeta = False

        # Helper function to update dicom
        def update_dicom(element, is_filemeta):
            if is_filemeta:
                self.dicom.file_meta.add(element)
            else:
                self.dicom.add(element)

        # Assume we don't want to add an empty value
        if value is not None:

            # If provided a field object, create based on keyword or tag identifier
            name = field
            if isinstance(field, DicomField):
                name = field.element.keyword or field.stripped_tag

            # Generate a tag item, add if it's a name found in the dicom dictionary
            tag = get_tag(name)

            # Second try, it might be a private (or other numerical) string identifier
            if not tag:
                tag = add_tag(name)

            if tag:
                uid = getattr(field, "uid", None) or str(tag["tag"])

                # For a replacement, this is likely
                if uid in self.fields:
                    element = self.fields[uid]

                    if element.is_filemeta:
                        is_filemeta = True

                    # Nested fields
                    while not hasattr(element, "value"):
                        element = element.element
                    element.value = value

                    # Add either to file meta or dicom directly
                    update_dicom(element, is_filemeta)
                else:
                    element = DataElement(tag["tag"], tag["VR"], value)
                    is_filemeta = str(element.tag).startswith("(0002")
                    update_dicom(element, is_filemeta)
                    self.fields[uid] = DicomField(element, name, uid, is_filemeta)
            else:
                bot.warning("Cannot find tag for field %s, skipping." % name)

    def _run_action(self, field, action, value=None):
        """
        Underlying function to run an action.

        perform_action (above) typically is called using a loaded deid,
        and _run_addition is typically done via an addition in a config
        Both result in a call to this function. If an action fails or is not
        done, None is returned, and the calling function should handle this.
        """
        # Blank the value
        if action == "BLANK":
            self.blank_field(field)

        # Unlikely to be called from perform_action
        elif action == "ADD":
            self.add_field(field, value)

        # Code the value with something in the response
        elif action == "REPLACE":
            self.replace_field(field, value)

        # Code the value with something in the response
        elif action == "JITTER":
            value = parse_value(
                item=self.lookup,
                dicom=self.dicom,
                value=value,
                field=field,
                funcs=self.deid_funcs,
            )
            if value is not None:
                # Jitter the field by the supplied value
                new_val = jitter_timestamp(field=field, value=value)
                if new_val not in [None, ""]:
                    self.replace_field(field, new_val)
            else:
                bot.warning("JITTER %s unsuccessful" % field)

        # elif "KEEP" --> Do nothing. Keep the original

        # Remove the field entirely
        elif action == "REMOVE":

            # If a value is defined, parse it (could be filter)
            do_removal = True
            if value != None:
                do_removal = parse_value(
                    item=self.lookup,
                    dicom=self.dicom,
                    value=value,
                    field=field,
                    funcs=self.deid_funcs,
                )

            if do_removal is True:
                self.delete_field(field)

    def remove_private(self):
        """
        Remove private tags from the loaded dicom
        """
        try:
            self.dicom.remove_private_tags()
        except Exception:
            bot.error(
                """Private tags for %s could not be completely removed, usually
                         this is due to invalid data type. Removing others."""
                % self.dicom_name
            )
            for ptag in get_private(self.dicom):
                del self.dicom[ptag.tag]
