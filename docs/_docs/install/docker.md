---
title: Deid via Docker
category: Installation
order: 2
---

To use the Docker container, you should first ensure that you have
 [installed Docker](https://www.docker.com/get-started) on your computer.

For the container we will use, we currently provide a container hosted
at [pydicom/deid](http://hub.docker.com/r/pydicom/deid) that you can use to
quickly run deid without any installation of other dependencies
or compiling on your host.

When you are ready, try running {{ site.title }} using it. This first command will
access the deid executable:

```bash
$ docker run {{ site.docker }}
$ deid
usage: deid [-h] [--quiet] [--debug] [--version] [--outfolder OUTFOLDER]
            [--format {dicom}] [--overwrite]
            {version,inspect,identifiers} ...
deid: error: too few arguments
```

It might also be desired to shell into the container and interact with deid
via python:

```bash
$ docker run -it --entrypoint bash {{ site.docker }}
(base) root@488f5e7f53a1:/code#
```
