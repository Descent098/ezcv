# Theme Development

There are 3 key peices of data you should be aware about when developing your theme's:

1. The config dictionary; Where all the data from ```config.yml``` is stored
2. The sections dictionary; Where all the raw data from your markdown content is stored
3. Sections HTML; If you are doing a component based model this is where the resulting html is stored

Additionally it is assumed you are aware of how to develop using [Jinja Templating.](https://jinja.palletsprojects.com/en/3.0.x/templates/)

It is also highly recommended to include everything found in the [support for standard features](#support-for-standard-features) section.

## Folder Layout

When creating a theme this is the only officially supported file structure layout:

**Note: I highly recommend snake casing on folder and file names to avoid path escaping bugs**

```
📁<theme_name>/
├── 📁css/
|   └──📄 <file_name>.css
├── 📁js/
|   └──📄 <file_name>.js
├── 📁images/
|   └──📄 <file_name>.<extension>
├── 📁sections/
|   └──📄 <section_name>.jinja
|   └──📁<blog section>
|       ├──📄 overview.jinja
|       ├──📄 feed.jinja
|       └──📄 single.jinja
├── 📝metadata.yml
└── 📄index.jinja
```

Using other formats have these side effects:

1. Cannot use optimize flag when building (will do nothing since it's expecting this layout)
2. Not be guarenteed to work, and if there are issues we **will not** be patching to support your file layout
3. Sections with highly coupled rendering, and special folder structure are likely to not work (i.e. Gallery and Blog)


## Base Theme

To make things easier to understand there is a base theme that has every feature supported in plain unstyled html. To use this base theme I would recommend copying it to your working directory and then changing your ```config.yml``` to use it. So you would do:

```shell
ezcv theme -c base
```

and then in your ```config.yml``` set:

```yml
theme: base
```

This will let you see in plain html **just** what ezcv is doing, and what data is available and how it's structured. I would recommend doing this to learn, but it is likely easier to modify an existing theme for most projects.


## Modifying Existing themes

If you want to modify an existing theme, set it in your ```config.yml``` file and then just run:

```shell
ezcv -c
```

You will now have a folder in your working directory with a copy of the theme you are using that you can begin modifying.


## Config Variable

Any settings defined in the ```config.yml``` file will be available in the templates under the ```config``` variable. For example if you wanted to access the defined name in the ```config.yml``` file you would do:

```jinja2
{{ config["name"] }}
```

### Adding new config values

Since the ```config``` variable is a [defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict), this means you can include any key-value pairs you want without needing to update the ezcv code base. Any unspecified values will simply return `False` instead of just crashing. 

So for example if you wanted to include a new variable in your theme called ```sign``` you could do it without needing to update ezcv in any way.

### Optional values

 Just keep in mind that if you want a variable to be optional you should do an explicit check within the **theme** for the variable, for example:

```jinja2
{% if config["sign"] %}
  <p> your sign is {{ config["sign"] }} </p>

{{% else %}}
<p> You have no sign </p>

{{% endif %}}
```

Because if you just do:

```jinja2
<p> your sign is {{ config["sign"] }} </p>
```

Then if no sign value is specified you will get:

```html
<p> your sign is False </p>
```

## Sections

### Sections Dictionary

For each section you can access a [defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict) inside any templates and use the section name as a key to get a list of that sections content.

For example here is what an example section dictionary would look like with only the work_experience section:

**Note that because this is a [defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict) any keys that are not filled in will be False**

```python
{'work_experience': 
  [
    [
      { 
        'company': 'Canadian Coding',
        'current': 'true', 
        'month_ended': False, 
        'month_started': 'October', 
        'role': 'CEO', 'year_ended': False, 
        'year_started': '2019'
      },

      '<p>This is my current job</p>' # This is the markdown content of the page as rendered html
    ],

    [
      {
        'company': 'Canadian Coding', 
        'current': False, 
        'month_ended': 'October', 
        'month_started': 'October', 
        'role': 'CTO', 
        'year_ended': '2020', 
        'year_started': '2017'
      },

      '<p>I do all the technical things</p>' # This is the markdown content of the page as rendered html
    ]
  ]
}
```

So to iterate through each of the peices of content you could do:

```jinja
{% for experience in sections["work_experience"] %}

    {{ project[0] }} {# This is the metadata dictionary #}

    {{ project[0][key] }} {# This is the syntax for accessing a specific key from the metadata, i.e. project[0]["company"] #}

    {{ project[1] | safe }} {# This is the actual content of the page after the metadata, the "| safe" will make it just render the markdown as HTML #}

{% endif %}
```

### Developing Sections templates

In any theme using the typical [file folder layout](#folder-layout) there are 3 types of sections:

1. [Markdown sections](#markdown-sections-theme-development); Standard markdown content that doesn't need to have each file rendered to a new page
2. [Gallery sections](#custom-styling-for-gallerys); Image galleries
3. [Blog sections](#blog-sections-theme-development); Sections that need access to a feed, and for each markdown file to be rendered in a template

#### Creating custom sections

ezcv supports adding in custom sections without need to change the codebase. To do so, simply add in the section template to ```/sections``` in your theme, then add a folder with the same name inside ```/content``` in the site's directory. Inside the section template the content will be available under the section name. 

For example if you created a custom markdown section called ```foo``` then in your theme folder you would put:

```
📁<theme_name>/
├── 📁sections/
└──  └──📄 foo.jinja
```

and in your site you would put

```
📁<site_name>/
├── 📁content/
|    └── 📁foo/
|         └──📄 example.md
```

and you can access the content of all the files in ```/content/foo``` in ```foo.jinja``` via:

```jinja2
<p> This is all the section foo content </p>
{{ foo }}

<p> This is how to iterate over each peice of content indvidually </p>

{% for bar in foo %}
<p> This is the metadata </p>
{{ bar[0] }}

<p> This is the content </p>
{{ bar[1] | safe }}

{% endfor %}
```

#### Markdown sections theme development

For markdown sections you just simply add your files in the ```/sections``` folder. I recommend using the ```.jinja``` extension, but ```.html``` will also work.

For example to create a section template for ```projects``` you would have:

```
📁<theme_name>/
├── 📁sections/
└──  └──📄 projects.jinja
```

Then put your section template inside ```projects.jinja```.

#### Blog sections theme development

Blog sections do have a different folder layout, for blog sections there are 3 files:

- `overview.jinja`; This file will end up rendering out as `<section name>.html` and is meant to be a landing page
- `feed.jinja`; This file is what gets rendered to `<section name>_html`, see [Sections HTML](#sections-html) for details
- `single.jinja`; This file is what will be rendered for **each peice of content**, so for example each blog post would be rendered as a page with the `title` or filename without the extension used (i.e. a file with `title: example` would be rendered to `example.html` and a file with no title called `lorem.md` would be rendered to `lorem.html`)

*The only required file is `feed.jinja`*

For example the layout for a blog section called `blog`, with a content file called `example.md` would be:

```
📁<theme_name>/
├── 📁sections/
|   └──📁blog
|       ├──📄 overview.jinja
|       ├──📄 feed.jinja
|       └──📄 single.jinja
```

and would result in:

- `blog_html` being available in all templates rendered from `feed.jinja`
- a page called `blog.html` rendered from `overview.jinja`
- a page called `example.html` rendered from `example.md` using `single.jinja`

Within `single.jinja` (if used) there is a seperate context passed with the following info:

```yml

{'config': 
  {... # This is where the config variables will be
  }, 
  'content': [
     {
       'title': 'Post Title', 
       'created': '2022-04-26', 
       'updated': '2022-04-26'
      }, 
     '<p>This is the post content</p>'
     ]}
```

So you will **only have access to the current post**, and variables can be accessed using:

```jinja
{{ content[0]["title"] }} <!-- content[0] is the metadata -->
{{ content[1] | safe }} <!-- This is the content of the post -->

```


#### Gallery sections theme development

Currently there is only support for 1 gallery section, and it must be created using a `gallery.jinja` file in the `sections/` folder:

```
📁<theme_name>/
├── 📁sections/
|   └──📄 gallery.jinja
```

The most basic setup for iterating through those images would be:

```jinja
{% for image in gallery %}
  <img src="{{ image[0]['file_path'] }}" alt="{{ image[0]['file_path'].split()[-1] }}" loading="lazy">
{% endfor %}
```

For details on adding EXIF data see [here](#custom-styling-for-gallerys)


### Sections HTML

On top of the actual sections being included in the sections dictionary if you have sections templates for doing component-based rendering you can access them using ```<section>_html```. So for example if you have a theme called ```base``` with a ```projects``` section in ```/base/sections/projects.jinja``` then to access the rendered html in your top-level pages you can use:

```jinja2
{{ projects_html | safe }}
```

### Accessing configuration variables in section templates

Additionally you can access the configuration details using

```jinja2
{{ config["name"] }}
```

where name is the configuration variable (i.e. biography, phone etc.)

## Support for standard features

This section contains details for implementing "standard" features that are used in all first-party themes, and are highly recommended to be included in custom themes.

### Adding support for Google Analytics

To add support for google analytics to your theme you can use the snippet below to the head tag of the template.


```jinja2
{% if config["ua_code"] %}
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{config['ua_code']}}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '{{config["ua_code"]}}');
</script>
{% endif %}
```

### Adding support for LaTex

In order for a theme to support latex you will need to add the following script import

```html
<script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>
```

### Adding support for customizing Favicons

To use a custom favicon in your theme overwrite the ```images/favicon.png``` file. In the documentation it is assumed this line exists, and users are told to place a file at this path if they want to override the included favicon. As such if you are starting from scratch be sure to include this line in the head tag:

```html
<head>
... <!-- Other code -->
<link rel="icon" type="image/png" href="images/favicon.png"/>
... <!-- Other code -->
</head>
```

### Adding suport for Resume Generation

Inside all themes they are packaged with a ```resume.jinja``` file. This file is what generates the html resume at `sitename/resume`. Any changes you want to make to the resume should be done to this file. Everything is self contained (stylesheets are CDN linked, or done inline in the `<style>` tag), so any changes you make to global stylesheets **will not** show up unless you import the stylesheet into ```resume.jinja``` with a link tag.


## Adding support for optional features

Below are the recommended methods to add support for optional configuration options, and optional features.

### Adding support for avatars

When people enter a value for avatar it is just an image path. Since this can be referenced in multiple ways it's recommended to use the `get_image_path` filter as shown below. Additionally it is recommended to have a fallback of some kind, because the config value could be `False`. It's also recommended to put somewhere in your documentation what the image dimensions should be for the avatar image since it's used in different ways by different themes.

```
{% if config['avatar'] %}
  <img src="{{ config['avatar'] | get_image_path }}" alt="{{config['name']}}" />
{% else %}
  <img src="/images/avatar.png" alt="{{config['name']}}" />
{% endif %}
```

## Custom styling for resume

To customize the styling for resumes you need to modify `resume.jinja`. Keep in mind that `resume.jinja` also has an inline custom stylesheet for print styling so keep that in mind when making changes (since many people will just print the generated resume if they need a hardcopy).

## Custom Styling for gallery's

*Note that using the optimized flag clears the exif data from images*

Gallery images have classes for each peice of information

```html
<p class='lens'>LEICA DG 100-400/F4.0-6.3</p>
<p class='focal-length'>256mm (full frame equivalent)</p>
<p class='iso'>ISO 400</p>
<p class='shutter-speed'>1/160 Second(s)</p>
<p class='aperture'>f6.3</p>
<p class='camera-type'>Panasonic DC-G95</p>
```

**As much as I would like to say I can guarentee this works for every type of exif data I only have 1 camera body to test with, so if something seems off please report it.**

### Notes
A few notes and idiocyncracies when using the HTML that gets exported

- The focal length will have the additional "(full frame equivalent)" added for lenses that are on non-standard sensor sizes (micro 4/3, APSC etc.)
- The camera type can include just the manufacturer, just the model name, or both based on how the exif data is burned in

### Overriding the default display completely
Let's say you want to do completely custom HTML like this:

```html


<div class="image">
    <img src="images/foo"> {# This is the image path #}
    <div class="camera-metadata">
      <p class='camera-type'>Panasonic DC-G95</p>
    </div>
    <div class="lens-metadata">
      <p class='focal-length'>256mm (full frame equivalent)</p>
      <p class='lens'>LEICA DG 100-400/F4.0-6.3</p>
    </div>
    <div class="exposure-details">
      <p class='iso'>ISO 400</p>
      <p class='shutter-speed'>1/160 Second(s)</p>
      <p class='aperture'>f6.3</p>
    </div>
</div>
```

To do so you would need to hook into the content and use the dictionary keys provided by the API **not the classes from above**. So the list of keys would be:

``
"EXIF LensModel" == Lens Model
"EXIF FocalLengthIn35mmFilm" == Focal length (converted to full frame equivalent) 
"EXIF FocalLength" == Focal length (raw and unconverted) 
"EXIF ISOSpeedRatings" == ISO
"EXIF ExposureTime" == Shutter Speed
"EXIF FNumber" == aperture \*(see note at bottom)
"Image Make" == The camera brand name (i.e. Panasonic)
"Image Model" == The camera model name (i.e. DC-G95)
``

\* The aperture is in rational form. So for example f6.3 would be 63/10


So to complete the example above you would do:
```jinja2
{% for image in sections["gallery"] %}

<div class="image">
    <img src="images/gallery/{{ image[0]['file_path'] }}"> {# This is the image path #}

    <div class="camera-metadata">
      <p class='camera-type'>{{ image[0]['Image Make'] }} {{ image[0]['Image Model'] }}</p>
    </div>
    <div class="lens-metadata">
      <p class='focal-length'>{{ image[0]['EXIF FocalLengthIn35mmFilm'] }}</p>
      <p class='lens'>{{ image[0]['EXIF LensModel'] }}</p>
    </div>
    <div class="exposure-details">
      <p class='iso'>ISO {{ image[0]['EXIF ISOSpeedRatings'] }}</p>
      <p class='shutter-speed'>{{ image[0]['EXIF ExposureTime'] }} Second(s)</p>
      <p class='aperture'>f {{ image[0]['EXIF FNumber'] }}</p>
    </div>
</div>
{% endif %}
```

## Available custom filters

There are several additional filters on top of the [jinja defaults](https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-filters) that have been added to ezcv to make it easier to develop themes

### split_to_sublists

Takes a list and splits it into sublists of size n.

#### Basic usage

```jinja2
{{ list|split_to_sublists(n, strict) }}
```

**Parameters**

```
initial_list : list
    The initial list to split into sublists

n : int
    The size of each sublist

strict: bool
    Whether to force an error if the length of the initial list is not divisible by n (split into even groups), default True
```


The list is passed in automatically via the pipe `|` operator as first argument, but you need to explicitly define n (the size of each sublist) and optionally provide strict.

#### Notes
**The list must be divisible by n if strict is True**. So for example if you set `n` to `3` and then give a list with `4` elements an error will be raised since `4 % 3 != 0`. You can avoid this by doing an explicit modulus check like:

```jinja2
{% if list|length % n == 0 %}
  {% for sublist in list|split_to_sublists(n) %}
  {% endfor %}
{% endif %}
```

or alternatively you can explicitly set `strict` to false which will just allow the last list to be less than `n`, like so:
```jinja2
{% for sublist in list|split_to_sublists(n, False) %}
  {# sublist| length can now be anywhere from 1 to n#}
{% endfor %}
```


#### Example

Let's say you want unique styling that takes images from a gallery and splits the list into sublists of 3 to individually process you could do:

```jinja2
{% if gallery|length % 3 == 0 %}
  {% for sublist in gallery|split_to_sublists(3) %}
    <div class="row">

      <div class="col-md-4">
        <img src="{{ sublist.0[0]['file_path'] }}" alt="{{ sublist.0[0]['file_path'].split()[-1] }}">
      </div>

      <div class="col-md-4">
        <img src="{{ sublist.1[0]['file_path'] }}" alt="{{ sublist.1[0]['file_path'].split()[-1]}}">
      </div>

      <div class="col-md-4">
        <img src="{{ sublist.2[0]['file_path'] }}" alt="{{ sublist.2[0]['file_path'].split()[-1] }}">
      </div>

    </div>
  {% endfor %}
{% endif }
```

The above jinja is roughly equivalent to something like this in pure python:


```python
gallery = ["image 1" , "image 2", "image 3", "image 4" , "image 5", "image 6"]

if len(images) % 3 == 0:
    for sublist in split_to_sublists(gallery, 3): # Returns [["image 1" , "image 2", "image 3"], ["image 4" , "image 5", "image 6"]]
      ... # Do stuff with each sublist
```



### get_image_path

Takes in the path to an image and returns it in usable format to use in img tags as src attribute

#### Basic usage

```jinja2
{{ path | get_image_path  }}
```

**Parameters**

```
path : str
    The raw image path from metadata
```

#### Example

Passing in an image path from a project in the projects section:

```jinja2
{% for project in projects %}
  {% if project[0]["image"] %}
  <img src="{{ project[0]['image'] | get_image_path }}" alt="{{ project[0]['image'] | get_filename_without_extension }}" />
  {% endif %}
{% endfor %}
```

The above jinja is roughly equivalent to something like this in pure python:

```python
project = [{"image": "image.jpg"}, ["other stuff"]]

if project[0]["image"]:
  print(get_image_path(project[0]['image'])) # Prints /images/image.jpg which is a usable path

project = [{"image": "https://example.com/img/image.jpg"}, ["other stuff"]]

if project[0]["image"]:
  print(get_image_path(project[0]['image'])) # Prints https://example.com/img/image.jpg which is a usable path
```



### get_filename_without_extension

Takes in path to filename and returns filename without extension

#### Basic usage

```jinja2
{{ path | get_filename_without_extension  }}
```

**Parameters**

```
path : str
    The original path to file
```

#### Example

Taking in an image path and returning just the file name to use in `alt` attribute:

```jinja2
{% for project in projects %}
  {% if project[0]["image"] %}
  <img src="{{ project[0]['image'] | get_image_path }}" alt="{{ project[0]['image'] | get_filename_without_extension }}" />
  {% endif %}
{% endfor %}
```

The above jinja is roughly equivalent to something like this in pure python:

```python
project = [{"image": "/path/to/John Doe.jpg"}, ["other stuff"]]

if project[0]["image"]:
  print(get_filename_without_extension(project[0]['image'])) # Prints "John Doe"

```



### pretty_datetime

A utility function for pretty printing dates provided for jobs/getting a degree/volunteering etc


#### Basic usage

```jinja
{{ month_started | pretty_datetime(year_started, month_ended, year_ended, current) }}
```

**Parameters**

```
month_started : str
    The month started i.e. October

year_started : str
    The year started i.e. 2013

month_ended : str
    The month ended i.e. December

year_ended : str
    The year ended i.e. 2017

current : bool
    A boolean describing if this is somewhere you are currently working/studying/volunteering at
```

#### Example

Printing the date details of a degree in the `education` section:

```jinja2
{% for experience in education %}
  {{ experience[0]["month_started"] | pretty_datetime(experience[0]["year_started"], experience[0]["month_ended"], experience[0]["year_ended"], experience[0]["current"]) }}
{%endfor%}
```

The above jinja is roughly equivalent to something like this in pure python:

```python

month_started = "October"
year_started = "2013"

month_ended = "December"
year_ended = "2017 

current = False

print(pretty_datetime(month_started, year_started, month_ended, year_ended, current)) # October 2013 - December 2017
```

### pretty_defaultdict

Returns a prettyprinted form of a defaultdict


#### Basic usage

```jinja
{{ ugly_dict | pretty_defaultdict | safe }}
```

**Notes**

Must be used with the safe filter since there is HTML included inline

**Parameters**

```
ugly_dict : defaultdict
    A defaultdictionary to pretty print
```

#### Example

Pretty printing the `config` defaultdictionary:

```jinja2
{{ config | pretty_defaultdict | safe }}
```

The above jinja is roughly equivalent to something like this in pure python:

```python
from ezcv.core import get_site_config

config = get_site_config()

print(pretty_defaultdict(config)) # Prints config dict in pretty form
```

## Metadata file

As of ezcv version 0.3.0 there is a specification for theme metadata. This specification is meant to provide information about a theme at a glance including details about the theme such as which version of ezcv it's designed for and when it was created to specific usage information like which sections and fields within those sections are available. Below is an example of a truncated version of the `metadata.yml` file in the dimension theme:

```yml
name: dimension
ezcv_version: "0.3.3"
created: 2022-05-18
updated: 2022-05-18
folder: dimension # Optional, only needed if folder is different than name field
required_config: # Optional, used to specify values for config.yml that are required to build site
  biography:
    type: str
    default: "A description of yourself"
    description: "This field is for writing about yourself you can add a > to span multiple lines"
sections: # Optional, only if sections are available
  education:
    type: markdown
    fields: # Optional, only if fields exist
      title: str
      institution:
        required: true
        type: str
      month_started: str
      year_started: str
      month_ended: str
      year_ended: str
      current: bool
  gallery:
    type: gallery
  blog:
    type: blog
    overview: true
    single: true
    feed: true
  projects:
    type: markdown
    fields:
      title:
        required: true
        type: str
      image: image
      link: str
  ... # More info below
```

By default a `metadata.yml` file like this will be generated if a theme is missing one automatically. Additionally all first party themes will ship with these files present.

### Generating theme metadata

The easiest way to generate theme metadata is to use the tool built into the cli. Inside a project folder that has the theme set in the `config.yml` you can run `ezcv theme -m`, this will bring the theme into the project folder (if not already there) and generate a `metadata.yml` file for you.

#### Fields key generation

Please note that the `fields` key will generate based on the metadata of the first **alphabetical** file in a content folder. So for example if this was the metadata for the first file alphabetically in `/content/education` and the theme had a file in `/sections/education.jinja`:

```markdown
---
institution: UBC
title: MSc Science Computer Science
year_started: 2014
year_ended: 2016
month_started: october
month_ended: october
current: true
---
```

then the resulting `metadata.yml` file would have:

```yml
sections:
  education:
    type: markdown
    fields:
      title: str
      institution: str
      month_started: str
      year_started: int
      month_ended: str
      year_ended: int
      current: bool
```

**Note that no fields are set to required when automatically generated**

### Required Config Key

You can optionally specify a `required_config` key, which is either a list or a YAML object specifying the required values a user must have in `config.yml` in order for a site to build. For example with the `dimension` theme:

```yml
required_config:
  name:
    type: str
    default: name
    description: "Your full name"
  biography:
    type: str
    default: "A description of yourself"
    description: "This field is for writing about yourself you can add a > to span multiple lines"
```

This means two things:

1) if someone uses the theme when using `ezcv init` these two configuration values will be added to `config.yml` (`name` and `theme` will be ignored if specified) in the form `<config_value>: <default> # <description>` so for example with the `dimension` `required_config` above you would get:


```yml
# See https://ezcv.readthedocs.io for documentation
name: John Doe
theme: dimension
resume: false
biography: A description of yourself # This field is for writing about yourself you can add a > to span multiple lines
```
2) If someone tries to build the site with these values missing they will get an error message
<img src="/en/latest/img/required_config_error.png" width="100%" height="500px">

The 3 attributes (type, default, description) are also optional, so you can include 1-3 of them, or you can also use the following format for brevity if you don't care about usability (which you should):

```yml
required_config:
  - name
  - biography
```

This will be interpreted as all values being strings with no description or default value.

### Top-level theme metadata

- Theme Name: str
- Date Created: Datetime string
- Date Updated: Datetime string
- Sections (see below)

*See [type indicators](#type-indicators-for-field) for any types you are unsure of.*

#### Sections metadata

You can include metadata for the themes included sections. If a theme has no sections you can omit this key completely. There are currently 3 defined section types.

##### Gallery Sections metadata

For image galleries you only need to specify the `type` parameter as `gallery`

```yml
sections:
  gallery:
    type: gallery
```

*only currently available for sections called `gallery.jinja`*

##### Markdown Sections metadata

For standard markdown sections that only have a feed you only need to specify the `type` parameter as `markdown`

```yml
sections:
  projects:
    type: markdown
    ... # more info
```

##### Blog Sections metadata

For blog markdown sections there are a few bits of configuration. First set the type to `blog`:

```yml
sections:
  blog:
    type: blog
    ... # more info
```

From there you can set variables for each type of template file that's available (i.e. `overview.jinja`, `single.jinja`, `feed.jinja`):

```yml
sections:
  blog:
    type: blog
    overview: true
    single: true
    feed: true
  ... # more info
```


##### Fields

Within each section you can include fields to denote which metadata can be provided for each markdown file.

###### Type indicators for field

- bool: Boolean values (True or False)
- str: string values (plain text)
- datetime: datetime string (string in the format of YYYY-MM-DD)
- literal: literal (a set of strings see below for details)
- int: an integer (number)
- float: a floating point number (decimal number)

You can define literals to state strings that must be one of a set number of options, for example if a field **only** be the strings "literal1" or "literal2" you can use a list format to denote this:

```python
sections:
  section:
    field:
      field_name: 
        - literal1
        - literal2
```

So for example if you have the choice between the literals ["sophomore", "junior", "senior"] for the field `level` in the `education` section it would be:

```yml
... # More stuff
sections:
    education:
        ... # More stuff
       fields
            level:
              - sophmore
              - junior
              - senior
... # More stuff
```

*Note that currently literals are not enforced, but down the road a flag will be added to make them enforceable*

###### Required Fields

If a field is required you can denote it by adding a `required: true` key-value pair to the field, otherwise it is assumed to be optional. For example:

```yml
... # More stuff
sections:
    section_name:
       folder_name: str
       fields:
          field_name: 
            type: str
            required: true
    section_name2:
       folder_name: str
       fields:
          field_name: type
... # More stuff
```


## Submitting a theme to be officially supported

Currently all themes (except the base and dimension themes) are pulled from a remote repository [https://github.com/QU-UP/ezcv-themes](https://github.com/QU-UP/ezcv-themes). If you want to submit a theme, then head there and [submit it](https://github.com/QU-UP/ezcv-themes/issues/new?assignees=&labels=new-theme&template=new_theme.md&title=%5BTheme%5D) and then create a pull request with the ticket submission referenced.

## Acknowledgements & Licenses

A big thank you to the providers for themes that are used heavily throughout the project. Keep in mind any attributions made in the code are **required to keep in the code**.

[Start Bootstrap](https://startbootstrap.com/)

[HTML5UP](https://html5up.net/)

If you want to use an attribution free version of HTML5UP themes checkout [pixelarity](https://pixelarity.com/)
