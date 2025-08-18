#!/usr/bin/env python3

"""
Simple example demonstrating private tag handling with the private creator syntax in deid.

This script shows how to implement a "retain safe private tags" approach that removes
all private tags except the ones specifically allowed by the user in the recipe,
using the GROUP,"PRIVATE_CREATOR",ELEMENT_OFFSET syntax for precise targeting.
"""

from pydicom import dcmread

from deid.data import get_dataset
from deid.dicom import get_identifiers, replace_identifiers
from deid.tests.common import create_recipe, get_file


def is_tag_private(dicom, value, field, item):
    """Check if a DICOM tag is private."""
    return field.element.is_private and (field.element.private_creator is not None)


def main():
    """
    Demonstrate private tag operations with the private creator syntax.
    """
    print("DEID Private Creator Syntax Example")
    print("=" * 40)

    # Get a sample DICOM file
    dataset = get_dataset("humans")
    dicom_file = get_file(dataset)
    print(f"Using DICOM file: {dicom_file}")

    # Create actions using the private creator syntax
    actions = [
        # Keep safe private tags using private creator syntax
        # This will ONLY match if the private creator exactly matches
        {"action": "KEEP", "field": '(0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)'},
        # Remove all private tags except the ones specified above
        # This will use a custom function to check if a tag is private
        # and remove it if it is not in the KEEP list
        {"action": "REMOVE", "field": "ALL", "value": "func:is_tag_private"},
    ]

    # Create the recipe
    recipe = create_recipe(actions)
    # The recipe would look like this:
    # KEEP (0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)
    # REMOVE ALL func:is_tag_private

    # Get identifiers to add our custom function
    items = get_identifiers([dicom_file])

    # Add our custom function to check private tags
    for item in items:
        items[item]["is_tag_private"] = is_tag_private

    # Process the DICOM file
    print("\nProcessing DICOM file with private tag recipe...")

    result = replace_identifiers(
        dicom_files=dicom_file,
        deid=recipe,
        ids=items,
        save=True,
        remove_private=False,  # Keep private tags so we can manipulate them
        strip_sequences=False,
    )

    processed = dcmread(result[0])
    print(f"Successfully processed file: {result[0]}")

    # Check if our target private tag was kept
    target_tag = "0033101E"  # This would be the hex tag format in DICOM
    print(
        "Retained Private Tag:",
        processed[target_tag],
        "with private creator:",
        processed[target_tag].private_creator,
    )


if __name__ == "__main__":
    main()
