# Contributor/Developer Docs

This section of the documentation is intended for people who are looking to write code for the `ezcv` codebase. This section is intended for developers who are looking to dive deeper into the technical details of the system, and those who are looking to contribute directly.

## Contribution guidelines

Below are details for submitting your code to the `ezcv` codebase. If you are just looking to modify some of the themes (aside from the `base` theme and `dimension` theme), then review the [theme development](theme-development.md) section instead of this page.

### Code standards

Any submitted code is expected to:
1. Be documented inline, and update user documentation if it's a new feature
   - Inline docs at minimum entails writing docstrings on **ALL** functions/classes using the existing [numpy style docs](https://numpydoc.readthedocs.io/en/latest/format.html#overview) (you can just follow what other methods/classes do)
   - User documentation should be concise but descriptive. People don't need all the technical details, but they do need to know enough to use your code
2. Not break any existing features/syntax

If you are unsure if you're on the right track to submitting code feel free to post in the [discussion board](https://github.com/Descent098/ezcv/discussions) for a second pair of eyes.

## Themes

Details about creating themes and submitting them for development can be found in the [theme development](theme-development.md) section of the docs. All themes (aside from the `base` theme and `dimension` theme) have their code at [https://github.com/QU-UP/ezcv-themes](https://github.com/QU-UP/ezcv-themes).

## Content parsing

In ezcv content parsing is done based on file extension. There is a base class in ```ezcv.content``` that is used to dispatch file parsing to subclasses based on the extensions they support. So for example if a file has a ``.md`` extension the ```Content``` class will have` Content.get_available_extensions()` called which will look into the values of it's child classes ```Content.extension``` attribute to see if they match. The resulting dictionary can then be used to dispatch to the correct class. 

For example this snippet is adapted from ```ezcv.content.get_section_content()```:

```python
import os

from ezcv.content import Content

content = [] # Empty list to be filled with content later
extension_handlers = Content.get_available_extensions()

for file_name in os.listdir("content/education"): # Iterate through /content/education and get the content from each file
    if not examples and file_name.startswith("example"):
        continue
    else:
        extension = "." + file_name.lower().split(".")[-1]      # Get the file extension
        if extension_handlers[extension]:                       # Checking if there exists a Content subclass capable of handling the file
            extension_handler = extension_handlers[extension]() # Instantiate the proper extension

            # Get the content and add it to the list
            metadata, html = extension_handler.get_content(os.path.join(section_folder, file_name))
            content.append([metadata, html])
print(content) # All the content from the files will be here in lists of lists
```

### Content base class

The `Content` class can be found in ```ezcv.content```, and is only really used to subclass content parsers and to get the available extensions with ```Content.get_available_extensions()```. Details on subclassing can be found [here](#creating-parser-for-new-extensions).

### Included extensions

Below are details about the included extensions. This is a broad overview, and it is a good idea to look specifically at the implementations in [content.py](https://github.com/Descent098/ezcv/blob/master/ezcv/content.py).

#### Markdown files

Used to parse markdown files in the `Projects`, `Education`, `Work Experience`, and `Volunteering Experience` sections. Details about implementation can be found in the [content.py](https://github.com/Descent098/ezcv/blob/master/ezcv/content.py).

**Extensions**:  .md, .markdown, .mdown, .mkdn, .mkd, .mdwn

##### Usage

To use this class directly you can use:

```python
metadata, html = Markdown().get_content(file_path: str)
```

The `metadata` return variable is a defaultdict of the [YAML Frontmatter](https://assemble.io/docs/YAML-front-matter.html) of the markdown file and `html` return variable is the raw HTML export of the content from the markdown file.

#### Image

Used in the gallery section. Details about implementation can be found in the [content.py](https://github.com/Descent098/ezcv/blob/master/ezcv/content.py).

**Extensions**: .jpg, .png, .jpeg, .gif, .svg, .webp, .apng, .jfif, .pjpeg, .pjp (Note only .png, .jpg and .jpeg are tested, rest are supported based on [this list of support](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img))

##### Usage

To use this class directly you can use:

```python
tags, html = Image().get_content(file_path:str)
```

The file path is then available at:

```python
tags[0]["file_path"]
```

### Creating parser for new extensions

To create a new parser for a set of extensions you will need to subclass the `Content` class and make sure you have:

  1. A list attribute called extensions, that is a list of strings with the extensions you support (i.e. [".md", ".markdown"])
  2. A function called \_\_metadata\_\_() that returns a defaultdict of the appropriate metadata for a file (can use `lambda:False` to initialize the defauldict)
  3. A function called \_\_html\_\_() that returns a string of the HTML from the parsed content
  4. A function called get_content() that returns the value of `\_\_metadata\_\_(), \_\_html\_\_()` as a tuple

While it is optional to have \_\_metadata\_\_() and \_\_html\_\_() return anything of value (\_\_html\_\_() in the `Image` class does very little), it is important because anyone who tries to call those methods directly will recieve a `NotImplementedError`, since it will invoke the methods from the base `Content` class.

A minimal example of a custom parser to handle files with the ".extension" and ".ext" extensions might look like:

```python
from collections import defaultdict          # Used to give dicts default args
from dataclasses import dataclass            # Used to improve class performance
from typing import DefaultDict, List, Tuple  # Used to provide accurate type hints


from ezcv.content import Content

@dataclass
class ExtensionParser(Content):
    extensions:List[str] = (".extension", ".ext") # Put all the relevent extensions that are handled by your parser

    def __metadata__(self) -> defaultdict:
      metadata:defaultdict = defaultdict(lambda:False)
      ... # Code to scrape relevent metadata and add to defaultdict
      return metadata

    def __html__(self, file_path:str) -> str:
      html = ""
      ... # Append markup to html variable
      return html
    
    # This function is what actually gets called by default in the ezcv code
    def get_content(self, file_path: str) -> Tuple[defaultdict, str]:
      if not os.path.exists(file_path): # If file doesn't exist
          raise FileNotFoundError(f"Could not find file: {file_path}\n")
      html = self.__html__(file_path)
      metadata = self.__metadata__()
      return metadata, html
```

If you would like to submit a parser you developed to be added to the main `ezcv` API please add it into `ezcv.content` and submit a pull request.

## CLI Entrypoints

`ezcv`'s command line interface has several entrypoints the details for which can be found in ```ezcv.cli```. Essentially each entrypoint is it's own function, and after the cli is called [docopt](https://github.com/docopt/docopt) is used to parse the arguments and dispatch to the corresponding functions.

### How exporting sites works

If a user uses ```ezcv build``` then it just calls the ```ezcv.core.generate_site()``` method, and if a ```--dir``` argument is provided it also passes that to the method.

### How generating previews works

Preview generation uses the same methods and calls as site exporting, the only difference is it uses the system defined temporary directory as defined by the [tempfile.TemporaryDirectory()](https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryDirectory) class and passes that to ```ezcv.core.generate_site()```.

## Filters

Filters are used inside templates to do... pretty much anything that python can do. They are injected into the Jinja environments and are used to do everything from capitalizing strings to rendering HTML. They are incredibly useful for times when Jinja doesn't quite do enough for your use case. `ezcv` has [several custom filters built in](theme-development.md#available-custom-filters). 

There are specific sections of the jinja documentation [dedicated to filters](https://jinja.palletsprojects.com/en/3.0.x/templates/#filters), but I will explain the basics of developing them.

### Filter syntax

To write a filter you will need to have at least 1 argument being passed in. When someone uses your filter anything they put left of the pipe (`|`) will be passed as the first variable.

#### Single argument filter

A filter is just a basic python function. So if you wanted to make a filter that takes in an int and then doubles it and returns it's string form you would do something like:

```python
def double_it(n:int) -> str:
  """Takes in an int, doubles it and returns it's string form"""
  return str(2*n)
```

Then make sure to add it to the environment by going into ```ezcv.filters.inject_filters()```, and adding the function object to the `filters` variable.

You can then use the filter like so:

```jinja2
<h2> 2 * 2 = {{ 2 | double_it }}</h2>
```

#### Multi-argument filter

Multi argument filters have very similar syntax to single argument filters, the main place the syntax deviates is in how you call it with jinja. Changing our `double_it()` example from before to taking in 2 integers `n` and `m` and then multiplying them by each other like so:

```python
def multiply(n:int, m:int) -> str:
  """Takes in two numbers and multiplies them by each other"""
  return str(n * m)
```

We then make sure to add it to the environment by going into ```ezcv.filters.inject_filters()```, and adding the function object to the `filters` variable.

Now we can use the filter like so:

```jinja2
<h2> 4 * 6 = {{ 4 | multiply(6) }}</h2>
```

The variable to the left of the pipe is automatically put as the first variable (`n`), and then every subsequent variable is structured like a standard python function call. So with a function like:

```python
def multiply_multiple_numbers(n:int, m:int, z:int) -> str:
  """Takes in three numbers and multiplies them by each other"""
  return str(n * m * z)
```

You would invoke it like this:

```jinja2
<h2> 4 * 6 * 2 = {{ 4 | multiply_multiple_numbers(6, 2) }}</h2>
```

You can also use python standard unpacking to allow arbitrary amounts of arguments, such as:

```python
def multiply_many_numbers(*numbers:int) -> str:
  """Takes in an arbitrary amount of numbers and multiplies them by each other"""
  result = 1

  for number in numbers:
    result *= number

  return str(result)
```

Which would be called after being added to ```ezcv.filters.inject_filters()``` with any number of arugment like this:

```
<h2> 2 * 3 * 4 * 5 * 6 * 7 = {{ 2 | multiply_many_numbers(3, 4, 5, 6, 7) }}</h2>
```

The same goes for using keyword arguments, just keep in mind you still **must** have that first argument passed. So something like:

```python
def string_values(n:int, **kwargs) -> str:
    """Takes in arguments and prints them"""

    return str(kwargs)
```

Could be called like this after being added to ```ezcv.filters.inject_filters()```:

```jinja
<h2> {{ 2 | string_values(arg_1 = "wow", arg_2 = "wowee", arg_3="zooweemama") }}</h2>
```

Notice our first number is just a throwaway value, but it is necessary in this case.

More details about jinja filters can be found [here](https://ttl255.com/jinja2-tutorial-part-4-template-filters/#writingyourownfilters)

### Updating existing filters
To update existing filters head to ```ezcv.filters``` and locate the filter you want to change. Be sure to familiarize yourself with the [syntax](#filter-syntax) first.

### How to add ad-hoc filters (add filters without updating ezcv source code)

To inject a filter into the environment for rendering you can add the method object to the `extra_filters` parameter in ```ezcv.core.generate_site()```. 

For example:

```python
from ezprez.core import generate_site

def multiply(n:int, m:int) -> str:
  """Takes in two numbers and multiplies them by each other"""
  return str(n * m)

generate_site(extra_filters=[multiply])
```

### How to add new custom filters to the core codebase

To add new filters you will need to add the function to ```ezcv.filters```, and then add the function object to the `filters` list local variable inside ```ezcv.filters.inject_filters()```.

## Extra documentation

### Logging

There is logging available for debugging simply use a setup like this:


```python
import logging

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

... # Run whichever function you're testing
```

### Sequence diagram of generating a site

<img src="/en/latest/img/generate_site_sequence.svg" width="100%" height="600px">

<details>
<summary>Mermaid source </summary>
~~~mermaid
sequenceDiagram
    core.generate_site()->>+core.get_site_config(): Getting site_context["config"]
    core.get_site_config()->>+core.generate_site(): 
    core.generate_site()->>+themes.locate_theme_directory(): Get the path for the theme
    themes.locate_theme_directory()->>+core.generate_site(): 
    core.generate_site()->>+filters.inject_filters(): inject custom filters into the jinja environment
    filters.inject_filters()->>+core.generate_site(): 
    core.generate_site()->>+themes.get_theme_section_directories(): Get a list of sections that have templates in the theme i.e. ['education', 'work_experience'] etc.
    themes.get_theme_section_directories()->>+core.generate_site(): 
    core.generate_site()->>+themes.get_content_directories(): Get a list of sections that have content folders in the project path i.e. ['education', 'work_experience'] etc.
    themes.get_content_directories()->>+core.generate_site(): 
    core.generate_site()->>+core.generate_site(): Determine pages to render in the top_level_file list
    core.generate_site()->>+core._render_section(): Render a section provided (i.e. education)
    core._render_section()->>+core._render_page(): Get html and metadata of markdown sections
    core._render_page()->>+core._render_section(): 
    core._render_section()->>+core.generate_site(): 
    core.generate_site()->>+core._export(): Generate output files and folders (also renders gallery and blog sections)
    core._export()->>+core.generate_site(): 
~~~
</details>
<br>

