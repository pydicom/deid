---
title: Welcome
permalink: /
---

**Anonymization toward De-identification (deid)**

This Python module is intended for basic coding of medical images, which means
"cleaning" image headers and pixel data, and integrating with your own functions
to replace with anonymous identifiers. Per HIPAA, this process is technically
called "anonymization," meaning we did our _best effort_.

> What does this module do?

 - Anonymize header data based on a specific logic of replacing, blanking, removing, or some custom function (e.g., "replace field X with item Y,")
 - Pass images through a filter for quarantine based on header logic, and if pixel coordinates are available, can black them out.
 - For each of the above, you can use defaults (blacklist, whitelist, graylist), or create your own customized logic.
 - provides functions for developers, and executables and containers for users.

> What does this module *not* do?

 - does *not* provide a workflow manager to perform these actions.
 - does *not* implement custom API calls to retrieve identifiers from some specific database.
 - does *not* guarantee IRB validated outputs and is not liable for however you might use it.

For dicom data, we use [pydicom](https://www.github.com/pydicom/pydicom) and for nifti we (will) use [nibabel](http://nipy.org/nibabel/).

> Where do I go from here?

If you are new to deid or pydicom, we recommend you start with
the [getting started]({{ site.baseurl }}/getting-started/) pages.
