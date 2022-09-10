__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2016-2022, Vanessa Sochat"
__license__ = "MIT"

# Supported formats
formats = ["dicom"]

# Supported Sections
sections = ["header", "labels", "filter", "values", "fields"]

# Supported Header Actions
actions = ("ADD", "BLANK", "JITTER", "KEEP", "REPLACE", "REMOVE", "LABEL")

# Supported Group actions (SPLIT only supported for values)
groups = ["values", "fields"]
group_actions = ("FIELD", "SPLIT")

# Valid actions for a field filter action
filters = (
    "contains",
    "notcontains",
    "equals",
    "notequals",
    "missing",
    "present",
    "empty",
)

# valid actions for a value filter
value_filters = (
    "contains",
    "notcontains",
    "equals",
    "notequals",
)
