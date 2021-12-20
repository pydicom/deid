# CHANGELOG

This is a manually generated log to track changes to the repository for each release. 
Each section should include general headers such as **Implemented enhancements** 
and **Merged pull requests**. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)

Referenced versions in headers are tagged on Github, in parentheses are for pypi.

## [vxx](https://github.com/pydicom/deid/tree/master) (master)
 - `ADD/KEEP` actions have now higher priority than `KEEP`, allowing to whitelist fields from `REMOVE ALL` [#197](https://github.com/pydicom/deid/issues/197)
 - updated pydicom dependency from 2.1.1 to 2.2.2 [#194](https://github.com/pydicom/deid/issues/194)
 - various LGTM alert fixes [#186](https://github.com/pydicom/deid/pull/186)
 - bug fix for exception when attempting to jitter DA/DT which cannot be jittered (space) [#189] (https://github.com/pydicom/deid/issues/189) (0.2.27)
 - adding support to manipulate file meta [#183](https://github.com/pydicom/deid/issues/183) (0.2.26)
 - updated pydicom dependency from 1.3.0 to 2.1.1 [#171](https://github.com/pydicom/deid/issues/171) (0.2.25)
 - bug fix for multivalued fields in %values lists [#174](https://github.com/pydicom/deid/issues/174)
 - allowing other VR types for jitter [#175](https://github.com/pydicom/deid/issues/175)
 - ensuring that an add/replace of an existing value is also updated in fields [#173](https://github.com/pydicom/deid/issues/173)
 - change to correct issue with deidentifying RGB images [#165](https://github.com/pydicom/deid/issues/165) (0.2.24)
 - removing verbosity of debug logger (0.2.23)
 - changing iteration technique through fields to properly add nested uids [#153](https://github.com/pydicom/deid/issues/153) (0.2.22)
 - change to return results from detect when recipe does not contain filters [#155](https://github.com/pydicom/deid/issues/155)
 - fix to correct bug in detect [#142](https://github.com/pydicom/deid/issues/142)  (0.2.21)
 - fixes to detect and clean to better represent keep/coordinates (0.2.20)
 - modify default VR for added tags [#146](https://github.com/pydicom/deid/issues/146), bug with private tags in %fields section [#147](https://github.com/pydicom/deid/issues/147) (0.2.19)
 - adding keepcoordinates to allow for reverse specified coordinates (0.2.18)
 - bug with empty values within %values sections [#144](https://github.com/pydicom/deid/issues/144) (0.2.17)
 - ability to save 4d dicom series as animation (0.2.16)
 - bug with multiple actions on the same header field [#140](https://github.com/pydicom/deid/issues/140) (0.2.15)
 - nested sequence in replace_identifiers/strip_sequences bug [#137](https://github.com/pydicom/deid/issues/137) (0.2.14)
 - adding custom cleaner to specify region fields (0.2.13)
 - bug with replace for tested fields (0.2.12)
 - fixing func args to be kwargs (0.2.11)
 - DicomCleaner empty method does not handle list (0.2.1)
 - refactor to use iterall for all fields (0.2.0)
 - including private tags in parsing (0.1.42)
 - adding filters (contains through missing) for REMOVE (0.1.41)
 - adding support for tag groups (values, fields) (0.1.4)
 - Adding option to provide function to remove (must return boolean) (0.1.38)
 - removing matplotlib version requirement (0.1.37)
 - Matplotlib dependency >= 2.1.2 (0.1.36)
 - Adding black formatting, tests run in GitHub actions (0.1.35)
 - Adding option to recursively replace sequences (0.1.34)
 - adding pylint to clean up code (0.1.33)
 - removing dependency that isn't used (simplejson) (0.1.31)
 - updating cleaner to use pixel array (0.1.30)
 - validation function should use debug verbository, bumping license year [#92](https://github.com/pydicom/deid/issues/92) (0.1.29)
 - bumping pydicom to 1.2.0 [#91](https://github.com/pydicom/deid/issues/91) (0.1.28)
 - header expansions starts with and ends with should support regular expression OR (|) [#89](https://github.com/pydicom/deid/issues/89) (0.1.27)
 - added all, allexcept, contains to field filters [#87](https://github.com/pydicom/deid/pull/87) (0.1.26)
 - fixing bug in jitter timestamp function [#85](https://github.com/pydicom/deid/pull/85) (0.1.25)
 - installation order of pydicom / matplotlib changes default python [#81](https://www.github.com/pydicom/deid/issues/81) (0.1.23)
 - updating deid.dicom with contribution from @fimafurman [#63](https://github.com/pydicom/deid/issues/63) (0.1.22)
 - adding "func" option for recipe to pass function (0.1.21)
 - fixing client bug, redoing docs to be better organized (0.1.20)
 - Removing MediaStorageSOPInstanceUID from file_meta, issue #72 (0.1.19)
 - need to clean up temporary directory (mkdtemp), issue #68 (0.1.18)
 - fixing issue #65, save for compressed data (0.1.17)
 - matplotlib must be less than or equal to 2.1.2 for install (0.1.16)
 - fixing bug with clean coordinate flipping rectangle
 - Fixing bug with saving self.cleaned (0.1.15)
 - Allowing for datasets to be passed in functions (not necessary for files) (0.1.14)
 - index should be full path in header.py (0.1.13)
 - pydicom bumped to install latest (1.0.2) (0.1.12)
 - ensuring that ids for images are full paths (0.1.11)
 - addition of the DeidRecipe class to better interact with and combine deid recipe files.
 - the get_files function now returns a generator instead of a list.

## [0.1.1](https://pypi.python.org/packages/28/26/ee80e7f1c3f65fae1c901497bb2388701158f0c96e0d633ab301abeaa478/deid-0.1.1.tar.gz#md5=39df7efb03e5d3b63308016742062a43) (0.1.1)

**additions**
 - addition of this CHANGELOG and an AUTHORS and CONTRIBUTING file to properly open source the project.
**bug fix**
 - when the user specifies a deid recipe, instead of adding it to a base template we honor the choice and don't append a base.
**creation**
 - this is the initial creation of deid, including recipes for cleaning of image headers and flagging of potential phi in pixels.
