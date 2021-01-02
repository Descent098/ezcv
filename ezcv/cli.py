"""The module containing all cli functionality of ezcv including:
    - Initializing sites
    - Generating temporary preview
    - Getting lists of themes and/or copying themes

Functions
---------
init:
    Initializes an ezcv site

preview:
    Creates a temporary folder of the site's files and then previews it in browser

theme:
    Used to get information about the available themes and/or copy a theme folder

main:
    The primary entrypoint for the ezcv cli

Examples
--------
Create a new site
```
from ezcv.cli import init

theme = "freelancer"
name = "John Doe"

init(theme, name)
```

Preview a site that is in the cwd
```
from ezcv.cli import preview

preview()
```

Copy the aerial theme
```
from ezcv.cli import theme

theme(copy_theme = True, theme = "aerial")
```

Print a list of available themes
```
from ezcv.cli import theme

theme(list_themes = True)
```
"""

# Standard Lib Dependencies
import os                   # Used for path validation
import shutil               # Used for file/folder copying and removal
import tempfile             # Used to generate temporary folders for previews
from sys import argv, exit  # Used to get length of CLI args and exit cleanly

## internal dependencies
from ezcv.core import generate_site, _get_site_config

# Third party dependencies
from docopt import docopt  # Used to complete argument parsing

usage = """Usage:
    ezcv [-h] [-v] [-p]
    ezcv init [<name>] [<theme>]
    ezcv build [-d OUTPUT_DIR] [-p]
    ezcv theme [-l] [-c] [<theme>]


Options:
-h, --help            show this help message and exit
-v, --version         show program's version number and exit
-l, --list            list the possible themes
-c, --copy            copy the provided theme, or defined site theme
-p, --preview         preview the current state of the site
-d OUTPUT_DIR, --dir OUTPUT_DIR The folder name to export the site to
"""

def init(theme="freelancer", name="John Doe"):
    """Initializes an ezcv site

    Parameters
    ----------
    theme : (str, optional)
        The theme to use in the config, by default "freelancer"

    name : (str, optional)
        The name to use in the config, by default "John Doe"
    """
    print(f"Generating site at {os.path.abspath(name)}")

    shutil.copytree(os.path.join(os.path.dirname(__file__), "example_site"), os.path.abspath(name))

    # Generate initial config.yml file
    with open(os.path.join(name, "config.yml"), "w+") as config_file:
        config_file.write(f"# See https://ezcv.readthedocs.io for documentation\nname: {name}\ntheme: {theme}")

    print(f"Site generated and is available at {os.path.abspath(name)}")


def preview():
    """Creates a temporary folder of the site's files and then previews it in browser"""
    with tempfile.TemporaryDirectory() as temp_dir:
        print(temp_dir)
        generate_site(temp_dir, preview=True)
        input("Press enter when done previewing")


def theme(list_themes: bool = False, copy_theme:bool = False, theme:str = ""):
    """Used to get information about the available themes and/or copy a theme folder

    Parameters
    ----------
    list_themes : bool, optional
        Whether or not to list the available themes, by default False

    copy_theme : bool, optional
        Whether or not to copy provided theme, by default False

    theme : str, optional
        The theme to copy, by default "" (which will copy the freelancer)
    """
    if not theme:
        theme = "freelancer"

    themes_folder =  os.path.join(os.path.dirname(__file__), "themes")

    if copy_theme:
        if os.path.exists(os.path.join(themes_folder, theme)): # If the theme exists in the themes folder
            try: # Try to copy the theme to ./<theme>
                shutil.copytree(os.path.join(themes_folder, theme), theme)
            except FileExistsError: # If a folder exists at ./<theme> remove and then re-copy
                shutil.rmtree(theme)
                shutil.copytree(os.path.join(themes_folder, theme), theme)
            print(f"Copied {os.path.join(themes_folder, theme)} to .{os.sep}{theme}")
        else: # Theme could not be found
            print(f"Theme {theme} not found and was unable to be copied")

    if list_themes:
        print(f"\nAvailable themes\n{'='*16}")
        for theme in os.listdir(themes_folder):
            print(f"  - {theme}")
        print() # empty newline after list


def main():
    """The primary entrypoint for the ezcv cli"""
    args = docopt(usage, version="0.1.0")

    if len(argv) == 1: # Print usage if no arguments are given
        print("\n", usage)
        exit()

    if args["--preview"] and not args["build"]:
        preview()

    elif args["init"]:
        if args["<theme>"] and args["<name>"]: # Both a theme and name are specified
            init(args["<theme>"], args["<name>"])
        elif args["<name>"]: # Only a name is specified
            init(name = args["<name>"])
        elif args["<theme>"]: # Only a theme is specified
            init(args["<theme>"])
        else: # No values are specified
            init()

    elif args["build"]:
        if not args["--dir"]:
            generate_site()
        else:
            generate_site(args["--dir"])

        if args["--preview"]: # If preview flag is specified
            preview()

        if not args["--dir"] and not args["--preview"]: # No flags provided
            print("\n", usage)
            exit()

    elif args["theme"]:
        if args["<theme>"]:
            theme(args["--list"], args["--copy"], args["<theme>"])
        elif args["--copy"]: # If copy is flagged, but no theme is provided
            if os.path.exists("config.yml"):
                theme(args["--list"], args["--copy"], _get_site_config()["theme"])
            else: # If no theme, or config.yml file is present
                theme(args["--list"], args["--copy"], "freelancer")
        elif args["--list"]:
            theme(args["--list"])
        else: # If theme argument is called with no other flags
            print("\n", usage)
            exit()

    elif args["--preview"]: # If preview flag is specified with no other flags
        preview()

    else: # No top level argument is provided
        print("\n", usage)
        exit()

if __name__ == "__main__": # For testing
    main()
