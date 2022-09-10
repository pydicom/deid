__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

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
    new_value = original

    if original is not None:

        # Create default for new value
        new_value = None
        dcmvr = field.element.VR

        # DICOM Value Representation can be either DA (Date) DT (Timestamp),
        # or something else, which is not supported.
        if dcmvr == "DA":
            # NEMA-compliant format for DICOM date is YYYYMMDD
            new_value = get_timestamp(original, jitter_days=value, format="%Y%m%d")

        elif dcmvr == "DT":
            # NEMA-compliant format for DICOM timestamp is
            # YYYYMMDDHHMMSS.FFFFFF&ZZXX
            try:
                new_value = get_timestamp(
                    original, jitter_days=value, format="%Y%m%d%H%M%S.%f%z"
                )
            except Exception:
                new_value = get_timestamp(
                    original, jitter_days=value, format="%Y%m%d%H%M%S.%f"
                )

        else:

            # If the field type is not supplied, attempt to parse different formats
            for fmtstr in ["%Y%m%d", "%Y%m%d%H%M%S.%f%z", "%Y%m%d%H%M%S.%f"]:
                try:
                    new_value = get_timestamp(
                        original, jitter_days=value, format=fmtstr
                    )
                    break
                except Exception:
                    pass

            # If nothing works, do nothing and issue a warning.
            if not new_value:
                bot.warning("JITTER not supported for %s with VR=%s" % (field, dcmvr))

    return new_value
