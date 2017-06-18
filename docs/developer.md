# Developers Notes

This readme is intended to explain how the functions work (on the back end) for those wishing to create a module for a new image type. The basic idea is that each folder (module, eg `dicom`) contains a base processing template that tells the functions to `get_identifiers` how to process different header values for the datatype (e.g, DICOM). This folder, and others like it, should contain should contain the following files:


 - **config.json** this is the default specification for how a dicom header is parsed, which primarily means additions, and a set of custom actions. 
 - **__init__.py**: has the purpose of exposing module functions to the higher up folder for import. For example, the function `get_identifiers` in [header.py](header.py) is programatically accessible via `from deid.dicom import get_identifiers` thanks to this file. If you create a new module with the equivalent functions, you should be fine to just copy this file, or import the functions directly from tasks.py in the module folder.
 - **header.py**: should contain functions for `get_identifiers`, which should return a dictionary with top level indexes by entity, and the value of each entity another dictionary indexed by the item ids. This data structure, if provided by the client, must be understood by the function `remove_identifiers`.

Note that, since we are working in Python, we will be using dicom headers that are mapped from the standard to pydicom, the entire mapping which is provided [here](https://github.com/pydicom/pydicom/blob/master/pydicom/_dicom_dict.py), and programatically accessible via:

```
from pydicom._dicom_dict import DicomDictionary

field_names = []

for key,entry in DicomDictionary.items():
   if entry[3] != "Retired":
       field_names.append(entry[4])
```

Since there are so many, we enforce (at least for dicom) the most conservative approach of removing header fields that the client has not asked anything special to be done for. Let's now talk about the [config.json](config.json).

## Config.json
The base of the json has two classes, and they correspond with the actions of `get` and `put`, where a "get" is broadly the step of getting identifiers from the data, and the "put" is putting things back (and realistically, removing a lot). Here they are, completely empty:

```
{
 "get": {},
 "put": {}
}
```

The entire data structure isn't very large, and can be shown to you:

```
{
   "get": { 

         
         "skip": ["PixelData"],
         "ids":{
            "entity":"PatientID",
            "item":"SOPInstanceUID"
         }

   },

   "put":{

          "actions":[
 
              {"action":"ADD","field":"PatientIdentityRemoved","value": "Yes"},

      ]
   }
}
```

Note that we don't need to specify the datatypes like "PixelData" or "Columns", or other fields related to the data. These fields are by default kept, as they are specific to the pixel data. For details see [this issue](https://github.com/pydicom/pydicom/issues/372).


### Get
If you read the details about get (usage for the client) see [get](get.md), you probably see some commonality. We have identified default fields in the header for entity and item under `['get']['ids']` (both which can be altered by the user via a function call) and then we skip over PixelData, because we don't want to return that for inspection, or have it in the list to include. If there are others you don't want returned, then add them to the skip list. Have caution that the user won't see the field returned, and likely won't ask for any action to be taken, meaning it will by default be blanked.


### Put
Put is primarily concerned with actions, which as they are for the user, can be `ADD`, `KEEP`, `REMOVE`, or `BLANK`. For the default, we keep the useful pixel data, and specify that we have removed the patient identity.
