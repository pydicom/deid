# Put Identifiers Back
At this point, we want to perform a `put` action, which is generally associated with the `replace_identifiers` function. 


## Default: Blank Everything
If we do absolutely nothing, and provide no input to the function. all fields will be blanked in the data.



## Customize Replacement
As we mentioned earlier, if you have a [deid settings](config.md) file, you can specify how you want the replacement to work, and in this case, you would want to provide the result `ids` variable from the [previous step](get.md)

For this example, we will use an example file provided with this package. Likely this will be put into a function with easier use, but this will work for now.

```
from deid.utils import get_installdir
from deid.config import load_deid
import os

deid = os.path.abspath("%s/../examples/deid/" %get_installdir())
```

The above `deid` is just a path to a folder that we have a `deid` file in. The function will find it for us. This function will happen internally, but here is an example of what your loaded `deid` file might look like.

```
load_deid(path)
DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved Yes
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE InstanceSOPUID var:source_id
Out[76]: 
{'format': 'dicom',
 'header': [{'action': 'ADD',
   'field': 'PatientIdentityRemoved',
   'value': 'Yes'},
  {'action': 'REPLACE', 'field': 'PatientID', 'value': 'var:id'},
  {'action': 'REPLACE', 'field': 'InstanceSOPUID', 'value': 'var:source_id'}]}
```

And this data structure will be used to specify your preferences in the replace_identifiers function (not yet updated!)

**currently being written**
