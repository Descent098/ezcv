# Theme Development

There are 3 key peices of data you should be aware about when developing your theme's:

1. The config dictionary; Where all the data from ```config.yml``` is stored
2. The sections dictionary; Where all the raw data from your markdown content is stored
3. Sections HTML; If you are doing a component based model this is where the resulting html is stored


## Base Theme

...

## Modifying Existing themes

...

## Config Variable

...

## Sections

### Sections Dictionary

For each section you can access a defaultdictionary inside any templates and use the section name as a key to get a list of that sections content.

For example here is what an example section dictionary would look like with only the work_experience section:

**Note that because this is a defaultdictionary any keys that are not filled in will be False**

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

...

### Sections HTML

On top of the actual sections being included in the sections dictionary if you have sections templates for doing component-based rendering you can access them using ```<section>_html```. So for example if you have a theme called ```base``` with a ```projects``` section in ```/base/sections/projects.jinja``` then to access the rendered html in your top-level pages you can use:

```jinja

```
