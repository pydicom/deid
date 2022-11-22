---
title: Github Contribution
category: Contributing
order: 2
---

Generally, for code contribution you should:

1. Open an issue to discuss what you would like to work on
2. Follow all existing docstring, coding styles
3. Make sure to write tests and format your code with black
4. Open a pull request against the master branch.

See the repository `CONTRIBUTING.md` for these same details.

## Contributing a Custom Function

Deid ships (as of version 0.2.3) with deid-provided functions that can be used in
header parsing. To contribute a custom function you should do the following:


1. Add a function to deid/dicom/actions, ideally in the appropriate file (e.g., uid functions in uuid.py, etc)
2. Ensure your function is added to the lookup in `deid/dicom/actions/__init__.py` so it can be found.
3. Add a test to `deid/tests/test_dicom_funcs.py` that ensures your function works, with or without custom variables.


Generally, a custom function should accept the following variables:

 - dicom: the dicom file
 - item: expected to be the dictionary lookup of user provided values
 - field: the dicom field
 - value: the value to replace

You can generally define a catch all `**kwargs` if you don't need a field. Finally,
if you do provide a custom variable, you'll need to also provide a default (or exit on error
if it's absolutely essential). As an example, if your custom function in the lookup is named
`generate_sesame_street_character` the user might provide a custom argument as follows:

```
%header

REPLACE fields:PatientID deid_func:generate_sesame_street_character name=elmo
```

Within the function, you can expect the extra (unparsed) key value pairs to be provided as "extras" and you
can use the deid utils helper to parse these into a dictionary:

```python
from deid.utils import parse_keyvalue_pairs
import random

def generate_sesame_street_character(item, value, field, dicom, **kwargs):
    """
    Add a sesame street character by name, or randomly chosen.
    """
    opts = parse_keyvalue_pairs(kwargs.get("extras"))

    default_names = ["grover", "elmo", "big-bird", "oscar-the-grouch"]
    name = opts.get("name") or random.choice(default_names)

    # The thing we return is the final value to replace the field with.
    return name
```

And that should be it! You are free to use (or not use) the item, value, field, and dicom.
Please open an issue if you have any questions.
