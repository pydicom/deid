# Ideas

These are general ideas/thinking for future development, mostly notes not implemented / planned in any way.

We might want to be able to specify multiple sections in one file, for more complex tasks like converting from dicom to nifti, and then scrubbing the nifti data:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved Yes

%function

RUN dicom2nifti

FORMAT nifti

%pixels

RUN pydeface
```

In the above example, the user will start with a set of dicom files, and do manipulation of the header. When the dicom data is deidentified, it will be converted from dicom to nifti with some function (`from dicom import dicom2nifti`) and then the nifti data will be defaced. If the user needs variable replacement of header values, this is where the pipeline might hit a snag, because it has to stop to let the user manipulate the data. It might make sense to not support this for now, or encourage doing one (then) the other. It is generally recommended to deal with most header information before conversion to nifti, as nifti scrapes away most of these header fields. This part has not yet been implemented, and is subject to change.

