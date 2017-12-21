# CHANGELOG

This is a manually generated log to track changes to the repository for each release. 
Each section should include general headers such as **Implemented enhancements** 
and **Merged pull requests**. All closed issued and bug fixes should be 
represented by the pull requests that fixed them. This log originated with Singularity 2.4
and changes prior to that are (unfortunately) done retrospectively. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)

## [vxx](https://github.com/pydicom/deid/tree/development) (development)

## [0.1.1](https://pypi.python.org/packages/28/26/ee80e7f1c3f65fae1c901497bb2388701158f0c96e0d633ab301abeaa478/deid-0.1.1.tar.gz#md5=39df7efb03e5d3b63308016742062a43) (0.1.1)

**additions**
 - addition of this CHANGELOG and an AUTHORS and CONTRIBUTING file to properly open source the project.
**bug fix**
 - when the user specifies a deid recipe, instead of adding it to a base template we honor the choice and don't append a base.
**creation**
 - this is the initial creation of deid, including recipes for cleaning of image headers and flagging of potential phi in pixels.
