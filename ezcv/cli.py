"""The module containing all cli functionality of ezcv including:
    - Initializing sites
    - Generating temporary preview
    - Getting lists of themes and/or copying themes

Functions
---------
init():
    Initializes an ezcv site

preview():
    Creates a temporary folder of the site's files and then previews it in browser

theme():
    Used to get information about the available themes and/or copy a theme folder

main():
    The primary entrypoint for the ezcv cli

Examples
--------
#### Create a new site
```
from ezcv.cli import init

theme = "freelancer"
name = "John Doe"

init(theme, name)
```

#### Preview a site that is in the cwd
```
from ezcv.cli import preview

preview()
```

#### Copy the aerial theme
```
from ezcv.cli import theme

theme(copy_theme = True, theme = "aerial")
```

#### Print a list of available themes
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
from ezcv.core import generate_site, get_site_config
from ezcv.themes import THEMES_FOLDER, get_remote_themes, locate_theme_directory, setup_remote_theme

# Third party dependencies
from colored import fg     # Used to highlight output with colors
from docopt import docopt  # Used to complete argument parsing for the cli

usage = """Usage:
    ezcv [-h] [-v] [-p]
    ezcv init [<name>] [<theme>]
    ezcv build [-d OUTPUT_DIR] [-p]
    ezcv theme [-l] [-c] [-s SECTION_NAME] [<theme>]


Options:
-h, --help            show this help message and exit
-v, --version         show program's version number and exit
-l, --list            list the possible themes
-c, --copy            copy the provided theme, or defined site theme
-p, --preview         preview the current state of the site
-d OUTPUT_DIR, --dir OUTPUT_DIR The folder name to export the site to
-s SECTION_NAME, --section SECTION_NAME The section name to initialize
"""

def init(theme="dimension", name="John Doe"):
    """Initializes an ezcv site

    Parameters
    ----------
    theme : (str, optional)
        The theme to use in the config, by default "dimension"

    name : (str, optional)
        The name to use in the config, by default "John Doe"
    """
    print(f"Generating site at {os.path.abspath(name)}")

    shutil.copytree(os.path.join(os.path.dirname(__file__), "example_site"), os.path.abspath(name))

    # Generate initial config.yml file
    with open(os.path.join(name, "config.yml"), "w+") as config_file:
        config_file.write(f"# See https://ezcv.readthedocs.io for documentation\nname: {name}\ntheme: {theme}\nresume: false")

    if theme != "dimension":
        # Check if theme is remote theme, and download it if it is
        
        remote_themes = get_remote_themes()
        if remote_themes.get(theme, False):
            original_directory = os.path.abspath(os.getcwd()) # Store CWD
            os.chdir(os.path.abspath(name))                   # Go into new site folder
            setup_remote_theme(theme, remote_themes[theme])   # Download theme 
            os.chdir(original_directory)                      # Navigate back to original cwd

    print(f"Site generated and is available at {os.path.abspath(name)}")


def preview():
    """Creates a temporary folder of the site's files and then previews it in browser"""
    with tempfile.TemporaryDirectory() as temp_dir:
        generate_site(temp_dir, preview=True)
        try:
            input("Press enter when done previewing")
        except EOFError:
            print(f"\nKeyboard interupt detected, ending preview and removing {temp_dir}")
            return
        except KeyboardInterrupt:
            print(f"\nKeyboard interupt detected, ending preview and removing {temp_dir}")
            return

        print(f"Ending preview and removing {temp_dir}")


def theme(list_themes: bool = False, copy_theme:bool = False, theme:str = ""):
    """Used to get information about the available themes and/or copy a theme folder

    Parameters
    ----------
    list_themes : bool, optional
        Whether or not to list the available themes, by default False

    copy_theme : bool, optional
        Whether or not to copy provided theme, by default False

    theme : str, optional
        The theme to copy, by default "" (which will copy the dimension theme)
    """
    if not theme:
        theme = "dimension"

    if copy_theme:
        if os.path.exists(os.path.join(THEMES_FOLDER, theme)): # If the theme exists in the themes folder
            try: # Try to copy the theme to ./<theme>
                shutil.copytree(os.path.join(THEMES_FOLDER, theme), theme)
            except FileExistsError: # If a folder exists at ./<theme> remove and then re-copy
                shutil.rmtree(theme)
                shutil.copytree(os.path.join(THEMES_FOLDER, theme), theme)
            print(f"Copied {os.path.join(THEMES_FOLDER, theme)} to .{os.sep}{theme}")
        else: # Theme could not be found
            print(f"Theme {theme} not found and was unable to be copied")

    if list_themes:
        # Get local themes
        print(f"\nAvailable local themes\n{'='*22}")
        for theme in os.listdir(THEMES_FOLDER):
            if not theme == "remotes.yml":
                print(f"  - {theme}")

        # Get remote themes
        print(f"\nAvailable remote themes\n{'='*23}")
        import yaml
        with open(os.path.join(THEMES_FOLDER, "remotes.yml")) as remote_themes:
            for theme in yaml.safe_load(remote_themes):
                print(f"  - {theme}")
        print() # empty newline after list



def new_section(section_name:str) -> bool:
    """Creates a new section (content folder, and section template in the theme)

    Parameters
    ----------
    section_name : str
        The name you want to give to the section, used to generate folder and template filename

    Notes
    -----
    - Needs to be run from the main folder of a site, or at most one folder deep (i.e. the content or Images folder)

    Returns
    -------
    bool
        True if the creation was successful and False if it failed early
    """    
    if os.path.exists("config.yml"):
        config_path = "config.yml"
    elif os.path.exists("../config.yml") :
        config_path = "../config.yml"
    else:
        print(f"{fg(1)}You are not in a project root folder, please run from folder with config.yml{fg(15)}\n")
        return False

    config = get_site_config(config_file_path=config_path)
    if not config["theme"]: # Set to default theme if no theme is set
        config["theme"] = "dimension"


    theme_path = locate_theme_directory(config["theme"], {"config": config})
    if os.path.exists(config["theme"]): # Theme is at cwd i.e. ./aerial
        theme_path = config["theme"]
    elif os.path.exists(os.path.join("..", config["theme"])): # Theme is one level up i.e. ../aerial
        theme_path = os.path.join("..", config["theme"])
    elif os.path.exists(os.path.join(THEMES_FOLDER, config["theme"])): # Theme is in package theme folder i.e. THEME_FOLDER/aerial
        theme_path = os.path.join(THEMES_FOLDER, config["theme"])
    else:
        print(f"{fg(1)}Could not find theme at any of the possible locations\n\t{config['theme']}\n\t{os.path.join('..', config['theme'])}\n\t{os.path.join(THEMES_FOLDER, config['theme'])} {fg(15)}\n")
        return False

    if os.path.exists("content"):
        content_path = "content"
    elif os.getcwd().split(os.sep)[-1] == "content": # Inside the current content folder
        content_path = os.getcwd()
    else:
        return False

    # The content for the template in the generated section
    default_section_page_templte = f"""\n{{% for page in {section_name} %}} <!--Lets you iterate through each page -->
            {{{{ page[0] }}}} <!--Metadata access -->
            {{{{ page[1] | safe }}}} <!--content access -->
{{% endfor %}}
\n"""

    # Begin creating content folder and theme file
    if not os.path.exists(os.path.join(content_path, section_name)): # If the content folder doesn't already exist
        if not os.path.exists(os.path.join(theme_path, "sections", f"{section_name}.jinja")) and not os.path.exists(os.path.join(theme_path, "sections", f"{section_name}.html")): # If jinja theme doesn't already exist
            os.mkdir(os.path.join(content_path, section_name))
            with open(os.path.join(theme_path, "sections", f"{section_name}.jinja"), 'w+') as section_file:
                section_file.write(default_section_page_templte)
        else: # Theme file already existed
            print(f"{fg(1)}Could not create path, path already exists at either: \n\t{os.path.join(theme_path, 'sections', f'{section_name}.jinja')}\n\tor\n\t{os.path.join(theme_path, 'sections', f'{section_name}.jinja')}\n{fg(15)}")
            return False
    else: # Content folder already existed
        print(f"{fg(1)}Could not create path, path already exists at {os.path.join(content_path, section_name)}\n{fg(15)}")
        return False

    print(f"Section successfully created\n\nTheme file created at:\n\t{os.path.join(theme_path, 'sections', f'{section_name}.jinja')}\nContent folder created at:\n\t{os.path.join(content_path, section_name)}")
    return True


def main():
    """The primary entrypoint for the ezcv cli"""
    args = docopt(usage, version="0.2.1")

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
        if args["--section"]:
            created = new_section(args["--section"])
            if not created:
                print(f"{fg(1)}Failed to create section {args['--section']} {fg(15)}")
        elif args["<theme>"]:
            theme(args["--list"], args["--copy"], args["<theme>"])
        elif args["--copy"]: # If copy is flagged, but no theme is provided
            if os.path.exists("config.yml"):
                theme(args["--list"], args["--copy"], get_site_config()["theme"])
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
