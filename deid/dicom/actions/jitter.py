__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2025, Vanessa Sochat"
__license__ = "MIT"

from pydicom.multival import MultiValue

from deid.logger import bot
from deid.utils import get_timestamp, parse_keyvalue_pairs

# Timestamps


def jitter_timestamp_func(item, value, field, **kwargs):
    """
    A wrapper to jitter_timestamp so it works as a custom function.
    """
    opts = parse_keyvalue_pairs(kwargs.get("extras"))

    # Default to jitter by one day
    value = int(opts.get("days", 1))

    # The user can optionally provide years
    if "years" in opts:
        value = (int(opts["years"]) * 365) + value
    return jitter_timestamp(field, value)


def jitter_timestamp(field, value):
    """
    Jitter a timestamp "field" by number of days specified by "value"

    The value can be positive or negative. This function is grandfathered
    into deid custom funcs, as it existed before they did. Since a custom
    func requires an item, we have a wrapper above to support this use case.

    Parameters
    ==========
    field: the field with the timestamp
    value: number of days to jitter by. Jitter bug!
    """
    if not isinstance(value, int):
        value = int(value)

    original = field.element.value

    # Early exit for empty values
    if not original:
        return None

    # Normalize to list for uniform processing of multi-value fields
    is_multi_values = isinstance(original, (list, tuple, MultiValue))
    values = list(original) if is_multi_values else [original]
    dcmvr = field.element.VR

    jittered = []
    for val in values:
        # Create default for new value
        single_value = None

        # DICOM Value Representation can be either DA (Date) DT (Timestamp),
        # or something else, which is not supported.
        if dcmvr == "DA":
            # NEMA-compliant format for DICOM date is YYYYMMDD
            single_value = get_timestamp(val, jitter_days=value, format="%Y%m%d")

        elif dcmvr == "DT":
            # NEMA-compliant format for DICOM timestamp is
            # YYYYMMDDHHMMSS.FFFFFF&ZZXX
            try:
                single_value = get_timestamp(
                    val, jitter_days=value, format="%Y%m%d%H%M%S.%f%z"
                )
            except Exception:
                single_value = get_timestamp(
                    val, jitter_days=value, format="%Y%m%d%H%M%S.%f"
                )

        else:
            # If the field type is not supplied, attempt to parse different formats
            for fmtstr in ["%Y%m%d", "%Y%m%d%H%M%S.%f%z", "%Y%m%d%H%M%S.%f"]:
                try:
                    single_value = get_timestamp(val, jitter_days=value, format=fmtstr)
                    break
                except Exception:
                    pass

            # If nothing works, do nothing and issue a warning.
            if not single_value:
                bot.warning(
                    f"JITTER not supported for tag={field.element.tag}, name={field.name}, VR={dcmvr}"
                )

        # If jittering failed (single_value is None), keep the original value
        jittered.append(single_value if single_value else val)

    # Return in same format as input
    if is_multi_values:
        # For multi-value DICOM fields, return as backslash-separated string
        return "\\".join(str(v) for v in jittered)
    else:
        return jittered[0]
