---
title: Contributing to Documentation
category: Contributing
order: 1
---

It's so great that you want to contribute! The documentation here includes information
about using and developing {{ site.title }}, and they are hosted on Github, meaning that you
can easily contribute via a [pull request](https://help.github.com/articles/about-pull-requests/).

<a id="getting-started">
## Getting Started

<a id="installing-dependencies">
### Installing Dependencies
Initially (on OS X), you will need to setup [Brew](http://brew.sh/) which is a
package manager for OS X and [Git](https://git-scm.com/). To install Brew and Git,
run the following commands:

```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install git
```

If you are on Debian/Ubuntu, then you can easily install git with `apt-get`

```bash
apt-get update && apt-get install -y git
```

<a id="fork-the-repo">
### Fork the repo
To contribute to the web based documentation, you should obtain a GitHub account and *fork* the <a href="https://www.github.com/{{ site.repo }}" target="_blank">{{ site.title }} Documentation</a> repository by clicking the *fork* button on the top right of the page. Once forked, you will want to clone the fork of the repo to your computer. Let's say my GitHub username is *meatball*:

```bash
git clone https://github.com/meatball/{{ site.reponame }}
cd {{ site.reponame }}/
```

<a id="install-a-local-jekyll-server">
### Install a local Jekyll server
This step is required if you want to render your work locally before committing the changes. This is highly recommended to ensure that your changes will render properly and will be accepted.

Jekyll requires Ruby. This project uses an older version of Jekyll, and thus requires an older version of Ruby (v2.7.8 seems to work). <a href="https://github.com/rbenv/rbenv">rbenv</a> is suggested to manage Ruby versions. On OS X, this looks like:

```bash
brew install rbenv
rbenv init
rbenv install 2.7.8
cd docs
rbenv local 2.7.8
``` 
This requires a new shell after installing rbenv (it modifies your shell profile). The last line sets Ruby 2.7.8 to be the Ruby version used within the docs directory. A second shell restart may be needed again, after that line. Test your active Ruby version with `ruby -v`. Once working, you install the needed plugins with (from the deid/docs directory):

```bash
bundle install
```

Now you can see the site locally by running the server with Jekyll:

```bash
bundle exec jekyll serve
```

This will make the site viewable at <a href="http://localhost:4000/{{ site.title }}/" target="_blank">http://localhost:4000/{{ site.title }}/</a>.
