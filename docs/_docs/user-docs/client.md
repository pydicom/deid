---
title: Deid Client
category: User Documentation
order: 6
---

After you [install deid]({{ site.baseurl }}/install/) you will notice a command line application has been placed in your bin:

```
$ which deid
/home/vanessa/anaconda3/bin/deid
```

**Note** @vsoch thinks this client could be better organized (with regard to
usage and commands) please [provide feedback]
(https://www.github.com/pydicom/deid/issues) as you test these functions!
The primary use of deid by the developers group has
been via functions in Python, so the client might be neglected.

<a id="usage">
## Usage
If you run the executable without any arguments, it will show you it's usage:

```
deid
usage: deid [-h] [--input FOLDER] [--version] [--print] [--format {dicom}]
            [--quiet] [--outfolder OUTFOLDER] [--overwrite] [--deid DEID]
            [--ids IDS] --action {get,put,all,inspect}
deid: error: the following arguments are required: --action/-a
```

It's telling us that it wants an action, which can be one of `{get,put,all}`,
where "get" corresponds to getting identifiers from a dataset, "put" corresponds
to doing the replacement, and "all" means you want to do both at the same time
(meaning you won't intervene between the calls to customize any of the replacement
actions. Let's walk through the simplest use case, giving an action without
any other arguments, which will use the default dataset provided (a subset
of [dicom-cookies](https://pydicom.github.io/dicom-cookies)).

<a id="inspect">
### Inspect

Currently, inspect is simply going to look at header fields and try to guess
if there are burned pixels in the image. I am not convinced this is robust -
the filters I am using are from [MIRC CTP](https://github.com/johnperry/CTP/blob/master/source/files/scripts/BurnedInPixelsFilter.script),
and seem to generally look for:

 - if the field Burned Annotation is set to Yes
 - if there is any indication of a SAVE
 - if a secondary device was involved

To inspect a dataset, call the `--action` (or `-a`) command with `inspect`:

```bash
deid --action inspect
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
DEBUG image4.dcm header filter indicates pixels are clean.
DEBUG image2.dcm header filter indicates pixels are clean.
DEBUG image7.dcm header filter indicates pixels are clean.
DEBUG image6.dcm header filter indicates pixels are clean.
DEBUG image3.dcm header filter indicates pixels are clean.
DEBUG image1.dcm header filter indicates pixels are clean.
DEBUG image5.dcm header filter indicates pixels are clean.
```

or specify your own dataset with `--input/-i`

```
deid --action inspect -input /home/vanessa/Desktop/test/su/
DEBUG Found 62 contender files in
DEBUG Checking 62 dicom files for validation.
WARNING Cannot read input file /home/vanessa/Desktop/test/su/__index.xml, skipping.
Found 61 valid dicom files
DEBUG FO-4893011557773677292.dcm header filter indicates pixels are clean.
WARNING FO-7672974892203473954.dcm header filters indicate burned pixels.
WARNING FO-7344077592634450132.dcm header filters indicate burned pixels.
DEBUG FO-2297306028740147772.dcm header filter indicates pixels are clean.
WARNING FO-6958553590975910128.dcm header filters indicate burned pixels.
DEBUG FO-3801449217794418870.dcm header filter indicates pixels are clean.
DEBUG FO-3156845437646327300.dcm header filter indicates pixels are clean.
DEBUG FO-7969108085464715668.dcm header filter indicates pixels are clean.
DEBUG FO-5786379487348112355.dcm header filter indicates pixels are clean.
DEBUG FO-3565568840462998171.dcm header filter indicates pixels are clean.
...
```

### Get
Let's specify `--action` as get. This means that we will use a demo dataset,
and the ids (a data structure saved in compressed python file called a "pickle")
will be saved to a temporary directory.

```
deid --action get
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
GET and PUT identifiers from dicom-cookies
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG Found 27 defined fields for image4.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Found 27 defined fields for image2.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Found 27 defined fields for image7.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Found 27 defined fields for image6.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Found 27 defined fields for image3.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Found 27 defined fields for image1.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Found 27 defined fields for image5.dcm
Writing ids to /tmp/tmpv3h9b11t/deid-ids.pkl
```

Pickle was chosen because what appear as strings are actually data structures
that write nicely back into dicom (or other) files. It also is likely the case
that to save and tweak these identifiers, you will likely need to load them
programmatically anyway, and we are doing a good deed for the world to
encourage using Python :).

<a id="customize-message-level">
#### Customize Message Level
Also by default, we give you debug output. If you want to silence the output,
then you can add `--quiet`:

```
deid --action get --quiet
 deid --action get --quiet
No input folder specified, will use demo dicom-cookies.
Found 7 valid dicom files
GET and PUT identifiers from dicom-cookies
Writing ids to /tmp/tmp6sywao9a/deid-ids.pkl
```

Note that you are actually receiving the level `INFO`, because otherwise you might
not know where the file was saved. If you really want to tweak your level,
then just export what you like in an environment variable, `MESSAGELEVEL`:

```bash
MESSAGELEVEL="QUIET"
export MESSAGELEVEL
deid --action get
```

And nothing would be printed!

<a id="customize-output">
#### Customize Output
If you just want to check output, it might be useful to print it to the screen.
You can do this by adding the flag `--print`:


```
$ deid --action get --print
```

You will see a WHOLE bunch of output print to the screen! You could pipe this
output into a file, however be careful that this will not be proper json.

```
$ deid --action get --print >> deid-ids.txt
$ cat deid-ids.txt | more
```

### Put
Put works in the same way, except you would also hand it your ids (the pickle)
file, in the case that you don't call get with put (via all). In case you changed
your message level to `QUIET`, change it back!

```bash
$ MESSAGELEVEL="DEBUG"
$ export MESSAGELEVEL
```

Now we give the function the pickle file from above:

```bash
$ ids=/tmp/tmp6sywao9a/deid-ids.pkl
$ deid --action put --ids $ids
```

and we again haven't provided our own top folder with files, so we use the dicom cookies.

```bash
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
PUT identifiers from dicom-cookies
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
Loading /tmp/tmp6sywao9a/deid-ids.pkl
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
Files saved to /tmp/tmpyti6zfiw
```

Did they save?

```bash
$ ls /tmp/tmpyti6zfiw/
image1.dcm  image3.dcm  image5.dcm  image7.dcm
image2.dcm  image4.dcm  image6.dcm

```
<a id="customizing-output-directory">
### Customizing Output Directory
You can change the output directory with the `--outfolder` flag:

```bash
$ ids=/tmp/tmp6sywao9a/deid-ids.pkl
out=/home/vanessa/Desktop

deid --action put --ids $ids --outfolder $out
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
PUT identifiers from dicom-cookies
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
Loading /tmp/tmp6sywao9a/deid-ids.pkl
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
7 dicom files at /home/vanessa/Desktop
```

if you try to do it again, and the files exist, it will get angry at you. I'll change the level to `ERROR` so you don't see the `DEBUG` statements:


```bash
MESSAGELEVEL="ERROR"
export MESSAGELEVEL
deid --action put --ids $ids --outfolder $out
ERROR image4.dcm already exists, overwrite set to False. Not writing.
ERROR image2.dcm already exists, overwrite set to False. Not writing.
ERROR image7.dcm already exists, overwrite set to False. Not writing.
ERROR image6.dcm already exists, overwrite set to False. Not writing.
ERROR image3.dcm already exists, overwrite set to False. Not writing.
ERROR image1.dcm already exists, overwrite set to False. Not writing.
ERROR image5.dcm already exists, overwrite set to False. Not writing.
```

This is mostly to protect you from accidentally over-writing data you didn't know was there. If you **want** to overwrite, you can do that:

```bash
MESSAGELEVEL="DEBUG"
export MESSAGELEVEL
deid --action put --ids $ids --outfolder $out --overwrite
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
PUT identifiers from dicom-cookies
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
Loading /tmp/tmp6sywao9a/deid-ids.pkl
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
7 dicom files at /home/vanessa/Desktop
```

and no error message occurs.

<a id="customize-deid-recipe">
#### Customize Deid Recipe
If you generate a configuration file (deid) that says how you want to deidentify
your data, then you can give that to get. Here is a simple one, discussed in
[config](config.md) and [available here](../examples/deid/deid.dicom) for our dicom cookies:

```bash
$ cat examples/deid/deid.dicom
FORMAT dicom

%header

ADD PatientIdentityRemoved YES
REPLACE PatientID var:id
REPLACE SOPInstanceUID var:source_id
```

The nice thing about using a deid is that (in the future when we don't have only one format, dicom), you will be able to give these files to the application and not have to specify a format. You will be able to have some custom deid file in a directory of folders that will be applied to its folder and directories below it, ip to the next found file (meaning you can identify different formats of data with one call). Right now (with only one format) we don't need that, but the software is ready for it.


```bash
ids=/tmp/tmp6sywao9a/deid-ids.pkl
deid="examples/deid/deid.dicom"
deid --action put --ids $ids --deid $deid
DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved YES
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
PUT identifiers from dicom-cookies
DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved YES
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
Loading /tmp/tmp6sywao9a/deid-ids.pkl
DEBUG Attempting ADDITION of PatientIdentityRemoved to image4.dcm.
WARNING REPLACE PatientID not done for image4.dcm
WARNING REPLACE SOPInstanceUID not done for image4.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Attempting ADDITION of PatientIdentityRemoved to image2.dcm.
WARNING REPLACE PatientID not done for image2.dcm
WARNING REPLACE SOPInstanceUID not done for image2.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Attempting ADDITION of PatientIdentityRemoved to image7.dcm.
WARNING REPLACE PatientID not done for image7.dcm
WARNING REPLACE SOPInstanceUID not done for image7.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Attempting ADDITION of PatientIdentityRemoved to image6.dcm.
WARNING REPLACE PatientID not done for image6.dcm
WARNING REPLACE SOPInstanceUID not done for image6.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Attempting ADDITION of PatientIdentityRemoved to image3.dcm.
WARNING REPLACE PatientID not done for image3.dcm
WARNING REPLACE SOPInstanceUID not done for image3.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Attempting ADDITION of PatientIdentityRemoved to image1.dcm.
WARNING REPLACE PatientID not done for image1.dcm
WARNING REPLACE SOPInstanceUID not done for image1.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Attempting ADDITION of PatientIdentityRemoved to image5.dcm.
WARNING REPLACE PatientID not done for image5.dcm
WARNING REPLACE SOPInstanceUID not done for image5.dcm
7 dicom files at /tmp/tmp5reygueo
```

And we can see the files:

```bash
$ ls /tmp/tmp5reygueo/
image1.dcm  image3.dcm  image5.dcm  image7.dcm
image2.dcm  image4.dcm  image6.dcm

```

The reason because we get a lot of warnings is because I specified to replace
fields in the data with variables in the ids data structure, but I didn't
actually add them. In practice, this would mean they would be removed from the header.
We would have needed to load the pickle, add the identifiers, and then give the
ids datastructure to put.  Let's quickly see what that would look like
(in python). First, load the identifiers we generated:

```python
from deid.identifiers import (
    load_identifiers,
    save_identifiers
)

idspkl = "/tmp/tmp3g0x8ts2/deid-ids.pkl"
ids = load_identifiers(idspkl)

Loading /tmp/tmp3g0x8ts2/deid-ids.pkl
```

Now, we need to define an "id" and "source_id" to substitute, here is a loop
to do that. At this point you would probably want to save whatever you need to
your IRB approved database / protocol.

```python
count=0
for entity, items in ids.items():
    for item in items:
        ids[entity][item]['id'] = "cookiemonster"
        ids[entity][item]['source_id'] = "cookiemonster-image-%s" %(count)
        count+=1
```

and let's save over the old one, why not.

```python
ids = save_identifiers(ids)
exit
```

Now let's try again - since the fields are defined in the data, we shouldn't see
the warning messages.

```python
ids=/tmp/tmp3g0x8ts2/deid-ids.pkl
deid="examples/deid/deid.dicom"
deid --action put --ids $ids --deid $deid

DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved YES
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
PUT identifiers from dicom-cookies
DEBUG FORMAT set to dicom
DEBUG Adding ADD PatientIdentityRemoved YES
DEBUG Adding REPLACE PatientID var:id
DEBUG Adding REPLACE SOPInstanceUID var:source_id
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
Loading /tmp/tmp3g0x8ts2/deid-ids.pkl
DEBUG Attempting ADDITION of PatientIdentityRemoved to image4.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Attempting ADDITION of PatientIdentityRemoved to image2.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Attempting ADDITION of PatientIdentityRemoved to image7.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Attempting ADDITION of PatientIdentityRemoved to image6.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Attempting ADDITION of PatientIdentityRemoved to image3.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Attempting ADDITION of PatientIdentityRemoved to image1.dcm.
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Attempting ADDITION of PatientIdentityRemoved to image5.dcm.
7 dicom files at /tmp/tmpqbols1q9
```

Looks good!

<a id="put-and-get">
### Put and Get (All)
If you just want to de-identify your data, (meaning get and put without intervention in between) you can use `--action all`:

```bash
$ deid --action all
No input folder specified, will use demo dicom-cookies.
DEBUG Found 7 contender files in dicom-cookies
DEBUG Checking 7 dicom files for validation.
Found 7 valid dicom files
GET and PUT identifiers from dicom-cookies
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG Found 27 defined fields for image4.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG Found 27 defined fields for image2.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG Found 27 defined fields for image7.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG Found 27 defined fields for image6.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG Found 27 defined fields for image3.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG Found 27 defined fields for image1.dcm
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
DEBUG Found 27 defined fields for image5.dcm
Writing ids to /tmp/tmp12lwhq7x/deid-ids.pkl
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5323.1495927169.335276
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5354.1495927170.440268
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5335.1495927169.763866
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5348.1495927170.228989
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5360.1495927170.640947
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5342.1495927169.3131
DEBUG entity id: cookie-47
DEBUG item id: 1.2.276.0.7230010.3.1.4.8323329.5329.1495927169.580351
7 dicom files at /tmp/tmp12lwhq7x
```

This will mean that the majority of things will be removed. You can still specify a
deid file to have additions, or blanks, but all variables must be present in the
header already (eg, the fields returned in the ids that we had tweaked above) for it to work.

<a id="your-own-folder">
### Your own folder
This is what you really want to do! Specify your own input folder with --input

```bash
$ deid --action get --input deid/data/dicom-cookies
```

That's it! If you want more robust explanation, or better control of this process,
go back to the [getting started]({{ site.baseurl }}/getting-started/) index and read
the dicom sections that talk about creating a configuration file using get,put, and
the developer notes.
