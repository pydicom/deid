---
title: Recipe Functions
category: User Documentation
order: 5
---

The [recipe headers]({{ site.baseurl }}/user-docs/recipe-headers/) page taught you
how to write a recipe that has one or more commands to parse a dicom image header.
For example, we might have defined a custom function [per the example here](https://pydicom.github.io/deid/examples/func-replace/)
to replace patient info with a result from our custom function:

```
%header

REPLACE fields:patient_info func:generate_uid
```

As of version 0.2.3 of deid, we have packaged functions along with deid that you can use without needing
to write your own! Current functions are provided for:

 - generating unique identifiers
 - jittering
 - *let us know if you want to contribute or request a new function!*

The current offerings include the following:

| Name          | Description | Extra Params |
|---------------|-------------|--------------|
| `simple_uuid` | Modify with a simple `uuid.uuid4()` string | None |
| `dicom_uuid` | A more formal dicom uid that requires an org root | org_root |
| `suffix_uuid` | Make the value the field name with a `uuid.uuid4()` suffix.  | None |
| `jitter`  | The same as JITTER (grandfathered in) | days |


## A Simple UUID

For a simple example, let's replace the recipe above with the deid provided "simple_uuid" function,
which is simply going to replace the field of our choice with a `uuid.uuid4()` string in Python.
That would look like this:

```
%header

REPLACE fields:patient_info deid_func:simple_uuid
```

The only change is that we replaced `func` with `deid_func`. Deid will see this function
is provided in its library, and grab it for use.


## A Pydicom UUID

Pydicom provides [a function to generate a UUID](https://pydicom.github.io/pydicom/dev/reference/generated/pydicom.uid.generate_uid.html)
and for most this is likely a good approach to take. The most basic usage (for one run) is to generate a random valid
unique identifier:

```
%header

REPLACE ReferringPhysicianName deid_func:pydicom_uuid
```

The default uses `stable_remapping=true`, which means we use the original UUID as entropy
to be able to consistently return the same value between runs. You can disable it, however
we do not recommended it (but maybe could be appropriate for your use case).

You can also optionally define a custom prefix. Note that it needs to match the
regular expression `^(0|[1-9][0-9]*)(\\.(0|[1-9][0-9]*))*\\.$` which (in spoken terms)
is a number followed by a period, another number, and ending also in a period (e.g, `1.55.`).


```
%header

REPLACE ReferringPhysicianName deid_func:pydicom_uuid prefix=1.55.
```

## A Dicom UUID

A more "formal" uuid function was added that requires an organization root. Your
organization should have it's own - for example the `PYMEDPHYS_ROOT_UID` is
"1.2.826.0.1.3680043.10.188" so we might do:

```
%header

REPLACE fields:patient_info deid_func:dicom_uuid org_root=1.2.826.0.1.3680043.10.188
```
Notice how we've provided an extra argument, `org_root` to be parsed. If you don't
provide one an `anonymous-organization` will be used, which isn't technically an organization root.


## A UUID Suffix

If you simply want to take the current field and add a suffix to it as the value:

```
%header

REPLACE fields:patient_info deid_func:suffix_uuid
```
This would make a final value that looks something like `patient_into-5897bd32-b4f3-4bda-9dc5-2d29e5688ea1`


## Jitter

Jitter is intended for datetime fields, and technically you can just use the `JITTER` function provided
natively in the recipe. We decided to include it here to add further customization. For example, you can provide
variables for both days and years for a more fine-tuned jitter. We also wanted to add it here because
technically it is a custom action. A jitter (as a custom deid function) might look like this:

```
%header

REPLACE fields:AcquisitionDate deid_func:jitter days=1
```

or some number of years and days:

```
%header

REPLACE fields:AcquisitionDate deid_func:jitter days=1 years=1
```

And that's it! If you want to request or contribute a custom (deid provided) function, please
[open an issue](https://github.com/pydicom/deid/issues).
