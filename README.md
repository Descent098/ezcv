![ezcv logo](https://raw.githubusercontent.com/Descent098/ezcv/master/.github/logo.png)

[![Downloads](https://pepy.tech/badge/ezcv)](https://pepy.tech/project/ezcv) [![DeepSource](https://deepsource.io/gh/Descent098/ezcv.svg/?label=active+issues&show_trend=true&token=Yg9KssXSgrClbYRYM3OMJhbI)](https://deepsource.io/gh/Descent098/ezcv/?ref=repository-badge)

# ezcv

*A python-based static site generator for setting up a CV/Resume site*

## Table of Contents

- [What does ezcv do?](#what-does-ezcv-do)
- [Features & Roadmap](#features--roadmap)
- [Why should I use ezcv?](#why-should-i-use-ezcv)
- [Who is ezcv for?](#who-is-ezcv-for)
- [Quick-start](#quick-start)
  - [No-code setup](#no-code-setup)
  - [Installation](#installation)
    - [From PyPi](#from-pypi)
    - [From source](#from-source)
    - [Getting started](#getting-started)
      - [Default File structure](#file-structure)
- [CLI](#cli)
- [Additional Documentation](#additional-documentation)
- [Examples and resources](#examples-and-resources)

## What does ezcv do?

ezcv is a purpose built static site generator for creating personal resume/portfolio/cv sites

## Features & Roadmap

- A large collection of [built in themes](https://ezcv.readthedocs.io/en/latest/included-themes/)
- Flexible templating with Jinja2
- Fully customizable configuration files and sections
- Simple markdown syntax for content building

## Why should I use ezcv?

ezcv is a great choice if:

- You are fond of one of the [built in themes](https://ezcv.readthedocs.io/en/latest/included-themes/)
- You want a free and open source static site generator
- If you want a simple to use static site generator based on Jinja
- If you are familiar with markdown and yaml, and want a system that can be extended
- You are not familiar with static site generators and want a simple one to try out
- You want a static site generator with a built in github pages deploy pipeline

ezcv is not a great choice if:

- You want a widely used industry solution (something like [hugo](https://gohugo.io/) or [jekyl](https://jekyllrb.com/) would be better for this)
- You need low level access to the API for complicated extensions that are not possible within jinja
- You are not familiar with markdown, yaml and jinja and want a frontend to edit your site with ( [netlify](https://www.netlify.com/), [squarespace](https://www.squarespace.com/) or [wix](https://www.wix.com/) would be better for this)

## Who is ezcv for?

- People who are not necessarily familiar with coding, let alone web development
- People who are familiar with web development and want a very simple to use static site generator
- People who are familiar with web development but don't want to bother writing pure html for their site

## Quick-start

Here's everything you need to know to get started with ezcv. 

### No-code/remote setup

Note that there is an option to develop a site completely on your browser without needing to install anything or know how to use git. For details on setting this up, please visit [https://ezcv.readthedocs.io/en/latest/quick-start/#remote-editing](https://ezcv.readthedocs.io/en/latest/quick-start/#remote-editing).

### Installation

To use ezcv you will need python 3.6+ (earlier versions wont work) and pip for python 3.

#### From PyPi

1. Run ```pip install ezcv```

#### From source

1. Clone this repo: [https://github.com/Descent098/ezcv](https://github.com/Descent098/ezcv)
2. Run ```pip install .``` or ```sudo pip3 install .```in the root directory

#### Getting started

The easiest way to get started is by running:

```ezcv init <name>```

Replacing the ```<name>``` argument with your name (use "" if you want to use your full name i.e. ```ezcv init "Kieran Wood"```). 

##### File structure

When you run the command a new folder will be created with your name, and some starter files like this:

**Legend**

| Icon | Meaning |
|------|---------|
|📁| File Folder |
|📷| Image file |
|📝| File you should edit/delete |
|📄| File you don't need to edit/shouldn't delete |

```
📁<name>/
├── 📁.github/
│   └── 📁workflows/
│       └── 📄ezcv-publish.yml
├── 📁content/
│   ├── 📁education/
│   |   ├── 📝example-current.md
│   |   └── 📝example-old.md
│   ├── 📁projects/
│   |   └── 📝example.md
│   ├── 📁volunteering_experience/
│   |   ├── 📝example-current.md
│   |   └── 📝example-old.md
│   └── 📁volunteering_experience/
│       ├── 📝example-current.md
│       └── 📝example-old.md
├── 📁images/
│   ├── 📷 abstract-landscape.jpg
│   └── 📷 ice-caps.jpg
├── 📄.gitignore
└── 📝config.yml
```

From here you can go into your ```config.yml``` file and [pick a theme](https://ezcv.readthedocs.io/en/latest/included-themes/), then start filling out your content according to what's available for the theme.

To preview your content use:

```ezcv -p```

If you're on github then pushing the contents to master/main will activate the publish workflow and automatically publish the site to ```<username>.github.io```.

## CLI

```shell
Usage:
    ezcv [-h] [-v] [-p]
    ezcv build [-d OUTPUT_DIR] [-o]
    ezcv init [<name>] [<theme>] [-f]
    ezcv theme [-l] [-c] [-m] [<theme>]
    ezcv section <SECTION_NAME> [-t=<type>]


Options:
-h, --help            show this help message and exit
-v, --version         show program's version number and exit
-l, --list            list the possible themes
-c, --copy            copy the provided theme, or defined site theme
-p, --preview         preview the current state of the site
-o, --optimize        Optimize output files (takes longer to run)
-f, --flask           Generate Flask routes and requirements.txt
-d OUTPUT_DIR, --dir OUTPUT_DIR The folder name to export the site to
-m, --metadata        Generate metadata for the theme
-t=<type>, --type=<type> The type of section to generate [default: markdown]
```

See the [CLI Documentation](https://ezcv.readthedocs.io/en/latest/cli/) for additional details

## Additional Documentation

[User Docs](https://ezcv.readthedocs.io)

[API Docs](https://kieranwood.ca/ezcv)

## Examples and resources

[Template repository for bootstrapping projects](https://github.com/qu-up/ezcv)

[Template repository for ezcv integrated with flask](https://github.com/QU-UP/flask-ezcv)

See documentation for [included themes](https://ezcv.readthedocs.io/en/latest/included-themes/) for examples of each of the included themes
