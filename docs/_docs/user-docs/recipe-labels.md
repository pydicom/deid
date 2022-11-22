---
title: Recipe Labels
category: User Documentation
order: 3
---

The `%labels` section is a way for the user to supply custom commands to an
application that aren't relevant to the header or pixels. For example, If I
wanted to carry around a version or a maintainer address, I could do that as follows:

```
FORMAT dicom

%header

ADD PatientIdentityRemoved YES
REPLACE PatientID cookie-monster

%labels
ADD MAINTAINER vsochat@stanford.edu
ADD VERSION 1.0
```

As you can see, the labels follow the same action commands as before, in the case
that the application needs them. In case you are interested in what the
application sees when it reads the file above (if you are a developer) it looks like this:

```
{
   "labels":[
      {
         "field":"MAINTAINER",
         "value":"vsochat@stanford.edu",
         "action":"ADD"
      },
      {
         "field":"VERSION",
         "value":"1.0",
         "action":"ADD"
      }
   ],

   "format":"dicom",
   "header":[
      {
         "field":"PatientIdentityRemoved",
         "value":"Yes",
         "action":"ADD"
      },
      {
         "field":"PatientID",
         "value":"cookie-monster",
         "action":"REPLACE"
      }
   ]
}
```

And you are free to map the actions (eg, `ADD`, `REMOVE`) onto whatever functionality
is relevant to your application, or just skip the action entirely and use the
fields and values.
