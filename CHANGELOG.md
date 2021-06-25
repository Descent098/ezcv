# Changelog

## V0.2.0; tbd

The focus for this release is to add new features and themes

### Features

- Added Resume Generator
- Setup remote theme support
- Added new sections
  - Blog
  - Gallery
- Google analytics config option
- Custom Favicon 
- Added new section creation CLI
- Added support for all standard markdown file extensions (.md, .markdown, .mdown, .mkdn, .mkd, .mdwn)
- Added many new markdown extensions
  - [footnotes](https://python-markdown.github.io/extensions/footnotes/)
  - [tables](https://python-markdown.github.io/extensions/tables/)
  - [toc (Table of contents)](https://python-markdown.github.io/extensions/toc/)
  - [abbr(abbreviations)](https://python-markdown.github.io/extensions/abbreviations/)
  - [def_list(Definition lists)](https://python-markdown.github.io/extensions/definition_lists/)
  - [sane_lists(Sane lists)](https://python-markdown.github.io/extensions/sane_lists/)
  - [mdx_math(Latex/formulas)](https://github.com/mitya57/python-markdown-math)

### Themes

- Moved existing themes to new repo https://github.com/QU-UP/ezcv-themes

### Bug fixes

- Fixed markdown files with .markdown not being recognized
- Fixed markdown files with capitalized extensions not being recognized

### Documentation Improvements

- Added documentation for new features
- Added additional onboarding videos/tutorials
- Added section for finding help/support

## V0.1.1; January 10th 2020

Fixes following initial launch

### Bug fixes

- Added additional warnings for if necessary config value is not provided

### Documentation improvements

- Updated necessary docstrings

## V0.1.0; January 10th 2020

Initial release of ezcv

### Features

- Themes Added:
  - [aerial](https://html5up.net/aerial)
  - base
  - [creative](https://startbootstrap.com/theme/creative)
  - [dimension](https://html5up.net/dimension)
  - [ethereal](https://html5up.net/ethereal)
  - [freelancer](https://startbootstrap.com/theme/freelancer)
  - [Identity](https://html5up.net/identity)
  - [Read only](https://html5up.net/read-only)
  - [Solid State](https://html5up.net/solid-state)
  - [strata](https://html5up.net/strata)
- Added initial [example site](https://github.com/Descent098/ezcv/tree/master/ezcv/example_site)
- Added initial [CLI](https://ezcv.readthedocs.io/en/latest/cli/)
- Added initial [core files](https://github.com/Descent098/ezcv/blob/master/ezcv/core.py#L289-L402)
- Added to [pypi](https://pypi.org/project/ezcv/)

### Documentation improvements

- Added initial [api docs](https://kieranwood.ca/ezcv)
- Added initial [user docs](https://ezcv.readthedocs.io)
