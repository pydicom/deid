from .jitter import jitter_timestamp, jitter_timestamp_func
from .uids import basic_uuid, dicom_uuid, pydicom_uuid, suffix_uuid

# Function lookup
# Functions here must take an item, field, and value

deid_funcs = {
    "jitter": jitter_timestamp_func,
    "dicom_uuid": dicom_uuid,
    "suffix_uuid": suffix_uuid,
    "basic_uuid": basic_uuid,
    "pydicom_uuid": pydicom_uuid,
}
