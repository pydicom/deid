---
title: Local Installation
category: Installation
order: 3
---


Let's walk through how to install {{ site.title }} locally.

<a id="install-from-github">
## Install from Github

First, clone the Github repository to your present working directory. If you
are a developer, you might want to fork it first, and then clone your fork.

```bash
git clone https://www.github.com/{{ site.repo }}
cd {{ site.reponame }}
```

If you are updating, it's helpful to issue this command until you see it's no
longer installed:

```bash
pip uninstall deid
```

Then install with python!

```bash
python setup.py install
```

<a id="install-from-pypi">
## Install from Pypi

If you want to install a particular version, the package is [available on pypi](https://pypi.org/project/deid/).

```bash
pip install deid
```

Install a particular version

```bash
pip install deid==0.1.19
```
