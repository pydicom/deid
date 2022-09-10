---
title: The Deid Recipe
category: Examples
order: 2
---

As we've discussed, the basic actions of using header filters to flag images, 
and performing actions on headers (for replacement), are controlled by a text file called 
a deid recipe. If you want a reminder about how to write this text file, 
[read here]({{ site.baseurl }}/getting-started/dicom-config), and we hope to at some 
point have an interactive way as well (let us know your feedback!). 
The basic gist of the file is that we have different sections. 

 - In the `%header` section we have a list of actions to take on header fields
 - We can define groups, either field names `%fields` or values from fields `%values` to reference in header actions
 - In the `%filter` section we have lists of criteria to check image headers against, and given a match, we flag the image as belonging to the group.

In this small tutorial, we will walk through the basic steps of loading a recipe, 
interacting with it, and then using it to replace identifiers. If you want to 
jump in, then go straight to the [script](https://github.com/pydicom/deid/blob/master/examples/dicom/recipe/deid-dicom-example.py) 
that describes this example.

<a id="recipe-management">
## Recipe Management

The following sections will describe creating and combining recipes.

<a id="create-a-deidrecipe">
### Create a DeidRecipe

We will start with how to work with a `DeidRecipe` object. If you aren't interested 
in this use case or just want to use a provided deid recipe file, continue to the 
next section.

We start by importing the class, and instantiating it.

```python
from deid.config import DeidRecipe
recipe = DeidRecipe()
WARNING No specification, loading default base deid.dicom
```

Since we didn't load a custom deid recipe text file, we get a default warning message that
a default is being use. That default is a [dicom base](https://github.com/pydicom/deid/blob/master/deid/data/deid.dicom) 
provided by the library. If you want to see the raw data structure that is loaded, look here:

```
recipe.deid
```

You can also double check the recipe format. We currently only support dicom, 
but this could in the future be other image formats (seriously, open an issue)!


```python
recipe.get_format()
# dicom
```

Note that validation of this structure happens at load time. If something is 
incorrectly labeled or formatted, you will get an error message and it will 
fail to load. You can also provide your own deid recipe file, and in 
doing so, you won't load the default. Here is one from our examples folder


```
wget https://raw.githubusercontent.com/pydicom/deid/master/examples/deid/deid.dicom
```

and in Python...

```
deid_file = os.path.abspath('deid.dicom')
recipe = DeidRecipe(deid=deid_file)
```

I would strongly recommended starting with an example, and building your custom
recipe from it. If you have an example that you think others would find useful, 
please contribute it to the repository in the examples folder.

<a id="combine-recipes">
### Combine Recipes

You can also choose to load the default base with your own recipe. In this action, 
the two recipes are combined, with any conflict (an overlap in the second) being 
given preference. For example, if the first deid you load removes a field and 
the second adds the same field, the final result will have it added. 
Keep this in mind and take care when combining recipes for this reason. 
Here is how it would look to load the default base *and* provide you custom file:

```
recipe = DeidRecipe(deid=deid_file, base=True)
```

You can also specify a different base entirely, and this would be equivalent to 
just providing a list of deid files:

```
recipe = DeidRecipe(deid=[deid_file1, deid_file2])
recipe = DeidRecipe(deid=deid_file1, base=True, default_base=deid_file2)
```

When we load bases, we are looking in the [data folder](https://github.com/pydicom/deid/tree/master/deid/data) 
provided by the module. The base is the deid.<tag> in this folder. 
So for example, if we wanted to use `deid/data/deid.dicom.chest.xray` we would specify:

```
# Use dicom.xray.chest as a base
recipe = DeidRecipe(deid=path, base=True, default_base='dicom.xray.chest')

# Use dicom.xray.chest as the only one
recipe = DeidRecipe(deid='dicom.xray.chest')

# On top of the default base, deid.dicom
recipe = DeidRecipe(deid='dicom.xray.chest', base=True)
```

This data folder is to encourage sharing! It often is a lot of work to develop 
a criteria specific for your group or interest. If you have a general recipe 
that others might use, please [contribute it](https://github.com/pydicom/deid/blob/master/CONTRIBUTING.md#pull-request-process).

<a id="sections">
## Sections

Now let's discuss the sections that a recipe can include, including a header, labels, filters, and
groups for lists of values or fields.


## Filters

The process of flagging images comes down to writing a set of filters to
check if each image meets some criteria of interest. For example, I might
create a filter called "xray" that is triggered when the Modality is CT or XR.
The filters are found in the `%filter` sections of the deid recipe. 

First, to get a complete dict of all filters (a dictionary with keys corresponding 
to filter group names and values the filters themselves) we can do the following actions:

```python
recipe.get_filters()

# To get the group names
recipe.ls_filters()
# ['whitelist', 'blacklist']

# To get a list of specific filters under a group
recipe.get_filters('blacklist')
```
<a id="header-actions">
## Header Actions

A header action is a step (e.g., replace, remove, blank) to be applied to
a dicom image header. The headers are also part of the deid recipe. You
don't need to necessarily use header actions and filters at the same time, but since
it's nice to keep things tidy for a single dataset using a shared file, we support 
having them both represented in the same file. You could just as easily keep 
them in separate files to load separately - a DeidRecipe is not
required to have header actions and/or filters.

First, let's load the default deid recipe file (deid.dicom in the data folder) 
that we know has a `%header` section.

```
recipe = DeidRecipe()
```

Here is how to get and interact with actions defined by the recipe.

```
# We can get a complete list of actions
recipe.get_actions()

# We can filter to an action type
recipe.get_actions(action='ADD')

#[{'action': 'ADD',
#  'field': 'IssuerOfPatientID',
#  'value': 'STARR. In an effort to remove PHI all dates are offset from their original values.'},
# {'action': 'ADD',
#  'field': 'PatientBirthDate',
#  'value': 'var:entity_timestamp'},
# {'action': 'ADD', 'field': 'StudyDate', 'value': 'var:item_timestamp'},
# {'action': 'ADD', 'field': 'PatientID', 'value': 'var:entity_id'},
# {'action': 'ADD', 'field': 'AccessionNumber', 'value': 'var:item_id'},
# {'action': 'ADD', 'field': 'PatientIdentityRemoved', 'value': 'Yes'}]

# or we can filter to a field
recipe.get_actions(field='PatientID')

#[{'action': 'REMOVE', 'field': 'PatientID'},
# {'action': 'ADD', 'field': 'PatientID', 'value': 'var:entity_id'}]

# and logically, both
recipe.get_actions(field='PatientID', action="REMOVE")
#  [{'action': 'REMOVE', 'field': 'PatientID'}]

# If you have lists of fields or values defined, you can retrieve them too
recipe.get_fields_lists()                                                                                                              
# OrderedDict([('instance_fields',
#              [{'action': 'FIELD', 'field': 'contains:Instance'}])])

recipe.get_values_lists()                                                                                                              
# OrderedDict([('cookie_names',
#              [{'action': 'SPLIT',
#                'field': 'PatientID',
#                'value': 'by="^";minlength=4'}]),
#             ('operator_names',
#              [{'action': 'FIELD', 'field': 'startswith:Operator'}])])

recipe.get_values_lists("cookie_names")                                                                                                
# [{'action': 'SPLIT', 'field': 'PatientID', 'value': 'by="^";minlength=4'}]
```

If you have need for more advanced functions, please [file an issue](https://www.github.com/pydicom/deid/issues).

<a id="replace-identifiers">
## Replace Identifiers

The `%header` section of a deid recipe defines a set of actions and associated
fields to perform them on. As we saw in the examples above, we could easily
view and filter the actions based on the header field or action type.
For this next section, we will pretend that we've just extracted ids from
our data files (in a dictionary called ids) and we will prepare a second
dictionary of updated fields.

In this first step, let's import needed functions and load a set of cookie dicoms!

```python
from deid.dicom import get_files, replace_identifiers
from deid.utils import get_installdir
from deid.data import get_dataset
import os

# This will get a set of example cookie dicoms
base = get_dataset('dicom-cookies')
dicom_files = list(get_files(base))
```

Here is the function to get identifiers

```python
from deid.dicom import get_identifiers
ids = get_identifiers(dicom_files)
```

Remember, the data above probably has PHI in it (e.g., a real `PatientID` and at this point
you might save them in your special (IRB approvied) places, and then do some action to
provide replacement anonymous ids to put back in the data. We provide a cookie tumor example
of doing this below.

```python
# Load the dummy / example deid
path = os.path.abspath("%s/../examples/deid/" %get_installdir())
recipe = DeidRecipe(deid=path)
```

We can quickly double check the actions that are defined

```python
recipe.get_actions()

[{'action': 'ADD', 'field': 'PatientIdentityRemoved', 'value': 'Yes'},
 {'action': 'REPLACE', 'field': 'PatientID', 'value': 'var:id'},
 {'action': 'REPLACE', 'field': 'SOPInstanceUID', 'value': 'var:source_id'}]
```

The above says that we are going to:

 -  `ADD` a field `PatientIdentityRemoved` with value `Yes`
 -  `REPLACE` `PatientID` with whatever value is under "id" in our updated lookup
 -  `REPLACE` `SOPInstanceUID` with whatever value is under "source_id"

We have 7 dicom cookie images we loaded above, so we have two options. We can
either loop through the dictionary of ids and update values (in this case,
adding values to be used as new variables) or we can make a new datastructure. 
Let's be lazy and just update the extracted ones

```python
updated_ids = dict(); count=0
for image, fields in ids.items():    
    fields['id'] = 'cookiemonster'
    fields['source_id'] = "cookiemonster-image-%s" %(count)
    updated_ids[image] = fields
    count+=1
```

You can look at each of the updated_ids entries and see the added variables

```python
updated_ids

...

  'id': 'cookiemonster',
  'source_id': 'cookiemonster-image-2'}}
```

And then use the deid recipe and updated to create new files

```python
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    deid=recipe,
                                    ids=updated_ids)

```

To check your work, you can load in a cleaned file to see what was done

```python
from pydicom import read_file
test_file = read_file(cleaned_files[0])

# test_file
# (0008, 0018) SOP Instance UID                    UI: cookiemonster-image-1
# (0010, 0020) Patient ID                          LO: 'cookiemonster'
# (0012, 0062) Patient Identity Removed            CS: 'Yes'
# (0028, 0002) Samples per Pixel                   US: 3
# (0028, 0010) Rows                                US: 1536
# (0028, 0011) Columns                             US: 2048
# (7fe0, 0010) Pixel Data                          OB: Array of 738444 bytes
```

And finally, a few extra customizations for different output folders and settings.

```python
# Different output folder
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    ids=updated_ids,
                                    output_folder='/home/vanessa/Desktop')

# Force overwrite (be careful!)
cleaned_files = replace_identifiers(dicom_files=dicom_files,
                                    ids=updated_ids,
                                    output_folder='/home/vanessa/Desktop',
                                    overwrite=True)
```

<a id="groups">
## Groups

More advanced usage of header actions would be to define a group of values (the content of the 
header fields) or field names (the names themselves) to use in an action. This corresponds
to `%fields` (a list of fields) and `%values` (a list of values from fields) to parse
at the onset of the dicom load, and use later in a recipe. Here is how that might look
in a recipe:

```
FORMAT dicom

%values cookie_names
SPLIT PatientID by=" ";minlength=3

%values operator_names
FIELD startswith:Operator

%fields instance_fields
FIELD contains:Instance

%header

ADD PatientIdentityRemoved Yes
REPLACE values:cookie_names var:id
REPLACE values:operator_names var:source_id
REMOVE fields:instance_fields
```

In the above, we define two lists of values (operator_names and cookie_names)
and a list of fields (instance_fields). The sections read as follows:

 - create a list of values called `cookie_names` that are from the PatientID field that is split by a space with a minimum length of 3
 - create a list of values called `operator_names` that includes any values from fields that start with "Operator"
 - create a list of field names, `instance_fields` that includes any field that contains "Instance"

And then in our `%header` section we take the following actions:

 - replace all fields that have any of the cookie names as a value with the variable defined by "id"
 - replace all fields that have any of the operator_names as a value with the variable defined by source_id
 - remove all fields defined in the list of instance_fields

Let's give this a try with an example. We'll load a recipe, and then look
at the loaded deid (recipe.deid).

```python
from deid.config import DeidRecipe
recipe = DeidRecipe("examples/deid/deid.dicom-group")
recipe.deid
OrderedDict([('format', 'dicom'),
             ('values',
              OrderedDict([('cookie_names',
                            [{'action': 'SPLIT',
                              'field': 'PatientID',
                              'value': 'by="^";minlength=4'}]),
                           ('operator_names',
                            [{'action': 'FIELD',
                              'field': 'startswith:Operator'}])])),
             ('fields',
              OrderedDict([('instance_fields',
                            [{'action': 'FIELD',
                              'field': 'contains:Instance'}])])),
             ('header',
              [{'action': 'ADD',
                'field': 'PatientIdentityRemoved',
                'value': 'Yes'},
               {'action': 'REPLACE',
                'field': 'values:cookie_names',
                'value': 'var:id'},
               {'action': 'REPLACE',
                'field': 'values:operator_names',
                'value': 'var:source_id'}])])
```
