#!/usr/bin/env python3

"""
Simple example demonstrating private tag handling with the new syntax in deid.

This script shows how to use REMOVE and REPLACE actions with private tags
using the enhanced syntax for precise targeting.
"""

from pydicom import dcmread

from deid.data import get_dataset
from deid.dicom import replace_identifiers
from deid.tests.common import create_recipe, get_file


def main():
    """
    Demonstrate private tag operations with the new syntax.
    """
    print("DEID Private Tag Syntax Example")
    print("=" * 40)

    # Get a sample DICOM file
    try:
        dataset = get_dataset("humans")
        dicom_file = get_file(dataset)
        print(f"Using DICOM file: {dicom_file}")
    except Exception:
        print("Sample DICOM data not available. This example shows the concept.")
        return

    # Read the original file to show what we're working with
    original = dcmread(dicom_file)
    print(f"\nOriginal PatientName: {original.get('PatientName', 'Not present')}")

    # Create actions using the new private tag syntax
    actions = [
        # Private creator syntax for precise targeting
        # This will ONLY match if the private creator exactly matches
        {"action": "REMOVE", "field": '(0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)'},
        {
            "action": "REPLACE",
            "field": '(0029,"SIEMENS CSA HEADER",21)',
            "value": "Example",
        },
    ]

    # Create the recipe
    recipe = create_recipe(actions)
    # The recipe would look like this:
    # REMOVE (0033,"MITRA OBJECT UTF8 ATTRIBUTES 1.0",1E)
    # REPLACE (0029,"SIEMENS CSA HEADER",21) Example

    # Process the DICOM file
    print("\nProcessing DICOM file with private tag recipe...")

    result = replace_identifiers(
        dicom_files=dicom_file,
        deid=recipe,
        save=True,
        remove_private=False,  # Keep private tags so we can manipulate them
        strip_sequences=False,
    )

    if result:
        dcmread(result[0])
        print(f"Successfully processed file: {result[0]}")
        print("Private tag operations completed!")
    else:
        print("No output file generated")


if __name__ == "__main__":
    main()
