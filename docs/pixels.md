# Cleaning Pixels

At this point, you've possibly obtained identifiers via a [get](get.md) action, and you want to figure out which of your images have pixels burned into the data. For that, we have a [set of pixel functions](../deid/dicom/pixels.py) that mirror the functionality of MIRCTP, specifically the functions to [filter DICOM](http://mircwiki.rsna.org/index.php?title=The_CTP_DICOM_Filter) and then [Anonymize](http://mircwiki.rsna.org/index.php?title=The_CTP_DICOM_Pixel_Anonymizer). The  [DicomPixelAnonymizer.script](https://github.com/johnperry/CTP/blob/master/source/files/scripts/DicomPixelAnonymizer.script) is a rule based list of known machine and modality types, and specific locations in the pixels where annotations are commonly found. The [BurnedInPixels.script](https://github.com/johnperry/CTP/blob/master/source/files/scripts/BurnedInPixelsFilter.script) is a set of filters that, given that an image passes through them, it continues processing. If it fails, then we flag it.

### Flagging Burned Images
If we look at the [BurnedInPixels.script](https://github.com/johnperry/CTP/blob/master/source/files/scripts/BurnedInPixelsFilter.script), we see the following:

```
    # We continue processing given that:
    # ![0008,0008].contains("SAVE") *   ImageType doesn't contain save AND
    # [0018,1012].equals("") *          DateofSecondaryCapture flat not present AND
    # ![0008,103e].contains("SAVE") *   SeriesDescription does not contain save AND
    # [0018,1016].equals("") *          SecondaryDeviceCaptureManufacturer flag not present AND
    # [0018,1018].equals("") *          SecondaryDeviceCaptureManufacturerModelName flag not present AND
    # [0018,1019].equals("") *          SecondaryDeviceCaptureDeviceSoftwareVersion flag not present AND
    # ![0028,0301].contains("YES")      BurnedInAnnotation is not YES
```

and I've provided a "human friendly" translation of the rules. The `!` operator indicates a `not`, and the `*` indicates `and`. You can imagine an image passing through those tests, and if it makes it all the way through, it's considered ok. If any of the tests fail, then it gets flagged for PHI (Burned Annotations) and is quarantined. Thus, we can read through the dicom fields and summarize the above as:

We continue processing given that:
 - Image was not saved with some secondary software or device
 - Image is not flagged to have burned pixels

If we look at the [DicomPixelAnonymizer.script](https://github.com/johnperry/CTP/blob/master/source/files/scripts/DicomPixelAnonymizer.script), it also contains criteria (and additionally, locations) for pixel areas that are known/likely to have annotations. The general format looks like this:

```
{ signature }
(region) (region) ... (region)
```
and the signature looks similar to an expression used in the `BurnedInPixels.script`, but the difference is that groups of logic are then paired with one or more regions:

```
{ Modality.equals("CT") 
    * Manufacturer.containsIgnoreCase("manufacturer1") 
        * ManufacturerModelName.containsIgnoreCase("modelA") }
(0,0,100,20) (480,200,32,250)
```

The expression above would say: 

The pixels with bounding boxes (0,0,100,20) and (480,200,32,250) should be removed if:
   - the modality is CT AND
   - the Manufacterer contains text "manufacturer1" (and ignore the case) AND
   - the Manufacturer model name text contains "modelA" (and ignore the case)


I'm not entirely sure why these two are separate (as both seem to indicate a flag for an image having PHI) but likely it's because the first group (`BurnedInPixels.script`) indicates header fields that are likely to indicate annotation, but don't carry any obvious mapping to a location. We can think of both as a set of filters, some with a clear location, and others not. TLDR: the second file (`DicomPixelAnonymizer.script`) has both header fields and locations.


### Deid Representation
For our purposes, since we just want to flag images with PHI, we don't need to distinguish fields as the MIRCTP does. Also, given that these criteria are universal (it would be unlikely that we would want to give users control to re-define what is considered PHI) we represent these criteria in the [config.json](../deid/dicom/config.json) provided in the dicom module. The filters look like this:

```
   "filter":{

          "contains":[
 
              {"action":"FLAG","field":"ImageType","value": "SAVE"},
              {"action":"FLAG","field":"DateOfSecondaryCapture", "value":""},
              {"action":"FLAG","field":"SeriesDescription", "value":"SAVE"},
              {"action":"FLAG","field":"SecondaryCaptureDeviceManufacturer", "value":""},
              {"action":"FLAG","field":"SecondaryCaptureDeviceManufacturerModelName", "value":""},
              {"action":"FLAG","field":"SecondaryCaptureDeviceSoftwareVersions", "value":""},
              {"action":"FLAG","field":"BurnedInAnnotation", "value":"YES"}


      ]
   }
```
     
The user can call a function to go through a list of images, and determine which are likely to have PHI.



