# Theme Development

There are 3 key peices of data you should be aware about when developing your theme's:

1. The config dictionary; Where all the data from ```config.yml``` is stored
2. The sections dictionary; Where all the raw data from your markdown content is stored
3. Sections HTML; If you are doing a component based model this is where the resulting html is stored


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

To make things easier to understand there is a base theme that has every feature supported in plain unstyled html. To use this base theme I would recommend copying it to your working directory and then changing your ```config.yml``` to use it. so you would do:

```shell
ezcv theme -c base
```

and then in your ```config.yml``` set:

```yml
theme: base
```

This will let you see in plain html **just** what ezcv is doing.


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

## Adding Google Analytics

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

## Customizing Favicons

To use a custom favicon in your theme overwrite the ```images/favicon.png``` file. In the documentation it is assumed this line exists, and users are told to place a file at this path if they want to override the included favicon. As such if you are starting from scratch be sure to include this line in the head tag:

```html
<head>
... <!-- Other code -->
<link rel="icon" type="image/png" href="images/favicon.png"/>
... <!-- Other code -->
</head>
```

## Customizing Resume Generation

Inside all themes they are packaged with a ```resume.jinja``` file. This file is what generates the html resume at `sitename/resume`. Any changes you want to make to the resume should be done to this file. Everything is self contained (stylesheets are CDN linked, or done inline in the `<style>` tag), so any changes you make to global stylesheets **will not** show up unless you import the stylesheet into ```resume.jinja``` with a link tag.
