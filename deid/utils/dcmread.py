__author__ = "Andrew Brooks"
__copyright__ = "Copyright 2025, Andrew Brooks"
__license__ = "MIT"

import pydicom

################################################################################
# Abstraction layer over pydicom
################################################################################


def dcmread(filename, **kwargs):
    """Just call the native pydicom dcmread function.
    This function exists so that if dcmread is renamed in future we can change
    it here and the rest of deid will continue to work unchanged."""
    return pydicom.dcmread(filename, **kwargs)
