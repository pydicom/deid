# Deid Documentation

![assets/img/logo.png](assets/img/logo.png)

This is a documentation site for [deid](https://www.github.com/pydicom/deid).
It is part of the [pydicom](https://www.github.com/pydicom) family of tools.

## Setup

 1. Install [Jekyll](https://jekyllrb.com/docs/installation/) locally. For Ruby, I recommend [rbenv](https://github.com/rbenv/rbenv).
 2. Install Jekyll dependencies with `bundle install`
 3. To serve the development server run `bundle exec jekyll serve`

## Folders Included
If you aren't familiar with the structure of a Jekyll site, here is a quick overview:

 - [_config.yml](_config.yml) is the primary configuration file for the site. Variables in this file render as `{{ site.var }}` in the various html includes and templates.
 - [_layouts](_layouts) are base html templates for pages
 - [_includes](_includes) are snippets of html added to layouts
 - [pages](pages) are generic pages (e.g., changelog) that aren't considered docs
 - [_docs](_docs) is a collection of folders that get rendered into the docs sidebar and pages
 - [assets](assets) includes all static assets
 - [_data](_data) has different data files (they can be in `.yml` or `.csv` to render into the site.
