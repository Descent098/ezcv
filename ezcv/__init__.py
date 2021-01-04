"""A python-based static site generator for setting up a CV/Resume site

Note
----
If this is your first time using ezcv I would recommend looking at the user docs at https://ezcv.readthedocs.io

Installation
------------
#### From pypi
```pip install ezcv``` or ```sudo pip3 install ezcv```

#### From source
1. ```git clone https://github.com/Descent098/ezcv```
2. ```pip install .``` or ```sudo pip3 install .```

Modules
-------
#### core
The module containing all primary functionality of ezcv including:

- Section parsing
- HTML generation
- Site exporting

#### cli
The module containing all cli functionality of ezcv including:

- Initializing sites
- Generating temporary preview
- Getting lists of themes and/or copying themes

Quickstart
----------
#### Generating a site using all settings defined in "config.yml"
```
from ezcv.core import generate_site

generate_site()
```

#### Generating a site overriding the theme in "config.yml", output directory and specifying to show a preview of the site
```
from ezcv.core import generate_site

generate_site(output_folder="my_site", theme = "aerial", preview = True)
```
"""