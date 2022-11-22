---
title: Linting and Formatting
category: Development
order: 3
---

After installing deid to a local environment, you can use [pre-commit](https://pre-commit.com/) to help
with linting and formatting. To do that:


```bash
$ pip install -r .github/dev-requirements.txt
```

Then to run:

```bash
$ pre-commit run --all-files
```

You can also install as a hook:

```bash
$ pre-commit install
```

And it will run always before you commit. This is the same linting
we use in our testing as well.
