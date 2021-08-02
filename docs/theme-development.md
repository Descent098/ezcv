# Theme Development

There are 3 key peices of data you should be aware about when developing your theme's:

1. The config dictionary; Where all the data from ```config.yml``` is stored
2. The sections dictionary; Where all the raw data from your markdown content is stored
3. Sections HTML; If you are doing a component based model this is where the resulting html is stored

Additionally it is assumed you are aware of how to develop using [Jinja Templating.](https://jinja.palletsprojects.com/en/3.0.x/templates/)

It is also highly recommended to include everything found in the [support for standard features](#support-for-standard-features) section.

## Folder Layout

When creating a theme this is the only officially supported file structure layout (others work but are not guarenteed to):

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
└── 📄index.jinja
```


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

### Developing sections templates

In any theme using the typical [file folder layout](#folder-layout) you just simply add your files in the ```/sections``` folder. I recommend using the ```.jinja``` extension, but ```.html``` will also work. 

For example to create a section template for ```projects``` you would have:

```
📁<theme_name>/
├── 📁sections/
└──  └──📄 projects.jinja
```

Then put your section template inside ```projects.jinja```.

### Sections HTML

On top of the actual sections being included in the sections dictionary if you have sections templates for doing component-based rendering you can access them using ```<section>_html```. So for example if you have a theme called ```base``` with a ```projects``` section in ```/base/sections/projects.jinja``` then to access the rendered html in your top-level pages you can use:

```jinja2
{{ projects_html | safe }}
```

### Creating custom sections

ezcv supports adding in custom sections without need to change the codebase. To do so, simply add in the section template to ```/sections``` in your theme, then add a folder with the same name inside ```/content``` in the site's directory. Inside the section template the content will be available under the section name. 

For example if you created a custom section called ```foo``` then in your theme folder you would put:

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

## Submitting a theme to be officially supported

Currently all themes (except the base and dimension themes) are pulled from a remote repository [https://github.com/QU-UP/ezcv-themes](https://github.com/QU-UP/ezcv-themes). If you want to submit a theme, then head there and [submit it](https://github.com/QU-UP/ezcv-themes/issues/new?assignees=&labels=new-theme&template=new_theme.md&title=%5BTheme%5D) and then create a pull request with the ticket submission referenced.
