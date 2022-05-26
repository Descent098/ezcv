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

section():
    Creates a new section, or prints details about a section if it already exists

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
from collections import defaultdict
import os                   # Used for path validation
import string               # Used for data validation
import shutil               # Used for file/folder copying and removal
import logging              # Used to log information for internal testing
import datetime             # Used for date formatting and date validation
from glob import glob       # Used to glob filepaths (patternmatch filepaths)
from sys import argv, exit  # Used to get length of CLI args and exit cleanly

## internal dependencies
from ezcv import __version__ as version
from ezcv.core import generate_site, get_site_config
from ezcv.themes import THEMES_FOLDER, generate_theme_metadata, get_remote_themes, get_theme_metadata, locate_theme_directory, setup_remote_theme
from ezcv.autoreload import start_server

# Third party dependencies
import yaml                      # Used to read and write yaml files
from colored import fg           # Used to highlight output with colors
from docopt import docopt        # Used to complete argument parsing for the cli
from PIL import Image            # Used to optimize and minify image files
from css_html_js_minify import * # Used to optimize and minify html/css/js files

usage = """Usage:
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
"""

def init(theme_name="dimension", name="John Doe", flask:bool = False):
    """Initializes an ezcv site

    Parameters
    ----------
    theme_name : (str, optional)
        The theme_name to use in the config, by default "dimension"

    name : (str, optional)
        The name to use in the config, by default "John Doe"
    """
    if os.path.exists(os.path.abspath(name)): # If folder already exists at ./<name>
        logging.error("[ezcv cli.init()] The provided name already exists")
        print(f"[ezcv cli.init()] The provided name {name} already exists at {os.path.abspath(name)}")
        return
    logging.debug(f"[ezcv cli.init()] Initializing site with theme {theme_name} and name {name}")
    print(f"Generating site at {os.path.abspath(name)}")

    logging.debug(f"[ezcv cli.init()] Copying example site from {os.path.join(os.path.dirname(__file__), 'example_site')} to {os.path.abspath(name)}")
    shutil.copytree(os.path.join(os.path.dirname(__file__), "example_site"), os.path.abspath(name))

    # Generate initial config.yml file
    logging.debug("[ezcv cli.init()] generating config file")

    ## Get theme info 
    site_context= {"config": {"name": name, "theme": theme_name, "remotes": get_remote_themes()}}
    theme_folder = locate_theme_directory(theme_name, site_context)
    theme_metadata = get_theme_metadata(theme_folder)
    with open(os.path.join(name, "config.yml"), "w+") as config_file:
        config_file_contents = f"# See https://ezcv.readthedocs.io for documentation\nname: {name}\ntheme: {theme_name}\nresume: false\n"
        if theme_metadata["required_config"]: # Parse required config from theme if available
            if type(theme_metadata["required_config"]) == dict:
                for value in theme_metadata["required_config"]:
                    if value in ("name", "theme"):
                        continue
                    if not theme_metadata["required_config"][value].get("type", False):
                        theme_metadata["required_config"][value]["type"] = "str"
                    if not theme_metadata["required_config"][value].get("description", False):
                        theme_metadata["required_config"][value]["description"] = ""
                    else: # If description exists
                        theme_metadata["required_config"][value]["description"] = "# " + str(theme_metadata["required_config"][value]["description"])
                    if not theme_metadata["required_config"][value].get("default", False):
                        if theme_metadata["required_config"][value]["type"] == "str":
                            theme_metadata["required_config"][value]["default"] = f'"{str(value)}"'
                        elif theme_metadata["required_config"][value]["type"] == "bool":
                            theme_metadata["required_config"][value]["default"] = False
                        elif theme_metadata["required_config"][value]["type"] == "int":
                            theme_metadata["required_config"][value]["default"] = 0
                        elif theme_metadata["required_config"][value]["type"] == "datetime":
                            theme_metadata["required_config"][value]["default"] = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
                    config_file_contents += f"{value}: {theme_metadata['required_config'][value]['default']} {theme_metadata['required_config'][value]['description']}\n"
            elif type(theme_metadata["required_config"]) == list:
                for value in theme_metadata["required_config"]:
                    if value in ("name", "theme"):
                        continue
                    config_file_contents += f"{value}: \"{str(value)}\"\n"
        config_file.write(config_file_contents)

    if theme_name != "dimension":
        logging.debug(f"[ezcv cli.init()] Not using dimension theme, copying theme {theme_name}")

        # Check if theme is remote theme, and download it if it is
        remote_themes = get_remote_themes()
        if remote_themes.get(theme_name, False):
            original_directory = os.path.abspath(os.getcwd()) # Store CWD
            os.chdir(os.path.abspath(name))                   # Go into new site folder
            setup_remote_theme(theme_name, remote_themes[theme_name])   # Download theme 
            os.chdir(original_directory)                      # Navigate back to original cwd

    if flask:
        logging.debug("[ezcv cli.init()] Finalizing Flask setup")
        os.remove(os.path.join(name, "standard-README.md"))
        os.rename(os.path.join(name, "flask-README.md"), os.path.join(name, "README.md"))
    else:
        logging.debug("[ezcv cli.init()] Finalizing Standard setup")
        os.remove(os.path.join(name, "routes.py"))
        os.remove(os.path.join(name, "requirements.txt"))
        os.remove(os.path.join(name, "flask-README.md"))
        os.rename(os.path.join(name, "standard-README.md"), os.path.join(name, "README.md"))

    print(f"Site generated and is available at {os.path.abspath(name)}")


def preview():
    """Creates a temporary folder of the site's files and then previews it in browser"""
    logging.debug("[ezcv cli.preview()] Generating temporary site preview")
    start_server()


def theme(list_themes: bool = False, copy_theme:bool = False, theme_name:str = "", metadata:bool = False):
    """Used to get information about the available themes and/or copy a theme folder

    Parameters
    ----------
    list_themes : bool, optional
        Whether or not to list the available themes, by default False

    copy_theme : bool, optional
        Whether or not to copy provided theme, by default False

    theme_name : str, optional
        The theme to copy, by default "" (which will copy the dimension theme)
    
    metadata : bool, optional
        Whether or not to generate metadata for the theme, by default False
    """
    logging.debug(f"[ezcv cli.theme({list_themes=}, {copy_theme=}, {theme_name=}, {metadata=})] Calling theme command")
    if not theme_name:
        logging.debug("[ezcv cli.theme()] No theme provided, using dimension theme")
        theme_name = "dimension"

    if metadata:
        if os.path.exists(os.path.join(THEMES_FOLDER, theme_name)): # If the theme exists in the themes folder
            try: # Try to copy the theme to ./<theme>
                logging.debug(f"[ezcv cli.theme()] Copying theme {theme_name} to ./{theme_name}")
                shutil.copytree(os.path.join(THEMES_FOLDER, theme_name), theme_name)
            except FileExistsError: # If a folder exists at ./<theme> remove and then re-copy
                shutil.rmtree(theme_name)
                shutil.copytree(os.path.join(THEMES_FOLDER, theme_name), theme_name)
            print(f"Copied {os.path.join(THEMES_FOLDER, theme_name)} to .{os.sep}{theme_name}")
            print(f"Generating/updating theme metadata for {theme_name}")
            logging.debug("[ezcv cli.theme()] Metadata specified, generating metadata file")
            metadata_path = os.path.abspath(f".{os.sep}{theme_name}{os.sep}metadata.yml")
            data = generate_theme_metadata(os.path.abspath(f".{os.sep}{theme_name}"), force=True)
            if not data["created"]:
                data["created"] = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
            if not data["ezcv_version"]:
                data["ezcv_version"] = version
            data["updated"] = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
            with open(metadata_path, "w+") as metadata_file:
                yaml.dump(dict(data), metadata_file)
        else: # Theme could not be found
            print(f"Theme {theme_name} not found and was unable to be copied")

    if copy_theme and not metadata:
        if os.path.exists(os.path.join(THEMES_FOLDER, theme_name)): # If the theme exists in the themes folder
            try: # Try to copy the theme to ./<theme>
                logging.debug(f"[ezcv cli.theme()] Copying theme {theme_name} to ./{theme_name}")
                shutil.copytree(os.path.join(THEMES_FOLDER, theme_name), theme_name)
            except FileExistsError: # If a folder exists at ./<theme> remove and then re-copy
                shutil.rmtree(theme_name)
                shutil.copytree(os.path.join(THEMES_FOLDER, theme_name), theme_name)
            print(f"Copied {os.path.join(THEMES_FOLDER, theme_name)} to .{os.sep}{theme_name}")
            print(f"Generating/updating theme metadata for {theme_name}")
            metadata_path = os.path.abspath(f".{os.sep}{theme_name}{os.sep}metadata.yml")
            data = generate_theme_metadata(os.path.abspath(f".{os.sep}{theme_name}"))
            if not data["created"]:
                data["created"] = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
            if not data["ezcv_version"]:
                data["ezcv_version"] = version
            data["updated"] = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
            with open(metadata_path, "w+") as metadata_file:
                yaml.dump(dict(data), metadata_file)
            
        else: # Theme could not be found
            print(f"Theme {theme_name} not found and was unable to be copied")

    if list_themes:
        # Get local themes
        logging.debug("[ezcv cli.theme()] Listing local themes")
        print(f"\nAvailable local themes\n{'='*22}")
        for current_theme in os.listdir(THEMES_FOLDER):
            if not current_theme == "remotes.yml":
                print(f"  - {current_theme}")

        # Get remote themes
        logging.debug("[ezcv cli.theme()] Getting remote themes")
        print(f"\nAvailable remote themes\n{'='*23}")
        with open(os.path.join(THEMES_FOLDER, "remotes.yml")) as remote_themes:
            for current_theme in yaml.safe_load(remote_themes):
                print(f"  - {current_theme}")
        print() # empty newline after list



def section(section_name:str, section_type:str):
    """Creates a new section, or prints details about a section if it already exists

    Parameters
    ----------
    section_name : str
        The name you want to give to the section, used to generate folder and template filename

    section_type : str
        The type of section you want to create, i.e. 'markdown'

    Notes
    -----
    - Needs to be run from the main folder of a site
    """    
    logging.debug(f"[ezcv cli.section({section_name=}, {section_type=})] Calling section command")

    # Sanatizing section name so resulting folder name is valid
    logging.debug(f"[ezcv cli.section()] Sanatizing {section_name=}")
    legal_path_characters = string.ascii_letters + string.digits+ " ()[]_-" # Allowed characters in file path
    section_name = section_name.replace(" ", "_")
    section_name = ''.join(current_character for current_character in section_name if current_character in legal_path_characters).lower()
    logging.debug(f"[ezcv cli.section()] Sanatized {section_name=}")

    if os.path.exists("config.yml"):
        config_path = "config.yml"
    else:
        print(f"{fg(1)}You are not in a project root folder, please run from folder with config.yml{fg(15)}\n")
        return 

    logging.debug("[ezcv cli.section()] Getting site config")
    config = get_site_config(config_file_path=config_path)
    if not config["theme"]: # Set to default theme if no theme is set
        config["theme"] = "dimension"

    logging.debug("[ezcv cli.section()] Getting theme metadata")
    theme_path = locate_theme_directory(config["theme"], {"config": config})
    theme_name = config["theme"]
    if os.path.exists(config["theme"]): # Theme is at cwd i.e. ./aerial
        theme_path = theme_name
    elif theme_path == os.path.join(THEMES_FOLDER, theme_name): # Theme is in package theme folder i.e. THEME_FOLDER/aerial
        try: # Try to copy the theme to ./<theme>
            print(f"[ezcv cli.section()] Copying theme {theme_name} to ./{theme_name}")
            logging.debug(f"[ezcv cli.section()] Copying theme {theme_name} to ./{theme_name}")
            shutil.copytree(os.path.join(THEMES_FOLDER, theme_name), config["theme"])
        except FileExistsError: # If a folder exists at ./<theme> remove and then re-copy
            shutil.rmtree(theme_name)
            shutil.copytree(os.path.join(THEMES_FOLDER, theme_name), theme_name)
        print(f"Copied {os.path.join(THEMES_FOLDER, theme_name)} to .{os.sep}{theme_name}")
        theme_path = theme_name
    else:
        print(f"{fg(1)}Could not find theme at any of the possible locations\n\t{config['theme']}\n\t{os.path.join('..', config['theme'])}\n\t{os.path.join(THEMES_FOLDER, config['theme'])} {fg(15)}\n")
        return 

    logging.debug("[ezcv cli.section()] Getting content directory")
    if os.path.exists("content"):
        content_path = "content"
    elif os.getcwd().split(os.sep)[-1] == "content": # Inside the current content folder
        content_path = os.getcwd()
    else:
        return
    
    logging.debug("[ezcv cli.section()] Getting theme metadata")
    theme_metadata = generate_theme_metadata(theme_path)
    if theme_metadata["sections"]:
        if theme_metadata["sections"].get(section_name, False):
            if theme_metadata["sections"][section_name].get("fields", False):
                fields_text = "\n\t• Fields: "
                for field in theme_metadata["sections"][section_name]["fields"]:
                    if type(theme_metadata["sections"][section_name]["fields"][field]) == str :
                        fields_text += f"\n\t\t • {field}: {theme_metadata['sections'][section_name]['fields'][field]} (optional)"
                    elif type(theme_metadata["sections"][section_name]["fields"][field]) == dict or type(theme_metadata["sections"][section_name]["fields"][field]) == defaultdict:
                        fields_text += f"\n\t\t • {field}: {theme_metadata['sections'][section_name]['fields'][field]['type']} ({'required' if theme_metadata['sections'][section_name]['fields'][field]['required'] else 'optional'})"
            else: # No fields specified
                fields_text = ""
            if theme_metadata["sections"][section_name].get("type", False) == "blog":
                print(f"""Section {section_name} details:
    • Type: Blog
    • Feed: {theme_metadata['sections'][section_name].get('feed', False)}
    • Single: {theme_metadata['sections'][section_name].get('single', False)}
    • Overview: {theme_metadata['sections'][section_name].get('overview', False)}{fields_text}
    """)
                return
            elif theme_metadata["sections"][section_name].get("type", False) == "gallery":
                print(f"Section {section_name} details:\n\t• Type: Gallery")
                return
            else:
                print(f"Section {section_name} details:\n\t• Type: Markdown{fields_text}")
            return
    if section_type.startswith("m"):
        # The content for the template in the generated section
        default_section_page_templte = f"""\n{{% for page in {section_name} %}} <!--Lets you iterate through each page -->
            {{{{ page[0] }}}} <!--Metadata access -->
            {{{{ page[1] | safe }}}} <!--content access -->
{{% endfor %}}
\n"""
    elif section_type.startswith("b"):
        section_type = section_type.replace("b", "").replace("blog","")
        # Parse which sections to include ([s]ingle.jinja, [f]eed.jinja, [o]verview.jinja)
        default_section_page_templte = defaultdict(lambda: False)
        if not section_type:
            section_type = "sfo" # If no additional type is specified, default to sfo
        if "s" in section_type:
            default_section_page_templte["single"] = f"""<!DOCTYPE html>\n<html>\n\t<body>
\t\t<h1>{{{{ content[0]['title'] }}}}</h1>
\t\t<h2>Created: {{{{ content[0]['created'] }}}} <br>Updated: {{{{ content[0]['updated'] }}}}</h1>
\t\t{{{{ content[1] | safe }}}}
\n\t</body>\n</html>"""
        if "f" in section_type:
            default_section_page_templte["feed"] = f"""{{% for post in {section_name} %}}
\t\t<h4> {{{{ post[0]["title"] }}}}</h4>
\t\t<!-- Metadata -->
\t\t<p>Created: {{{{ post[0]["created"] }}}}</p>
\t\t<p>updated:{{{{ post[0]["updated"] }}}}</p>
\t\t<a href='{{{{ post[0]["title"] }}}}'>{{{{ post[0]["title"] }}}}</a>
\t\t<!-- Content -->
\t\t<p>{{{{ post[1] | safe}}}}</p>
{{% endfor %}}"""
        if "o" in section_type:
            if "f" in section_type:
                default_section_page_templte["overview"] = f"""<!DOCTYPE html>\n<html>\n\t<body>
{{{{ {section_name}_html | safe}}}}
\n\t</body>\n</html>"""
            else:
                default_section_page_templte["overview"] = f"""<!DOCTYPE html>\n<html>\n\t<body>
{{% for post in {section_name} %}}
\t\t<h4> {{{{ post[0]["title"] }}}}</h4>
\t\t<!-- Metadata -->
\t\t<p>Created: {{{{ post[0]["created"] }}}}</p>
\t\t<p>updated:{{{{ post[0]["updated"] }}}}</p>
\t\t<!-- Content -->
\t\t<p>{{{{ post[1] | safe}}}}</p>
{{% endfor %}}
\n\t</body>\n</html>"""
    elif section_type.startswith("g"):
        # The content for the template in the generated section
        default_section_page_templte = f"""\n{{% for image in {section_name} %}} <!--Lets you iterate through each image -->
            {{{{ image[0] }}}} <!--Metadata -->
            <img src="{{{{ image[0]['file_path'] }}}}" alt="{{{{ image[0]['file_path'].split()[-1] }}}}"> <!--Image -->
{{% endfor %}}
\n"""
    if not os.path.exists(os.path.join(theme_path, "sections")):
        os.mkdir(os.path.join(theme_path, "sections"))
    # Begin creating content folder and template file(s)
    if type(default_section_page_templte) == str:
        if not os.path.exists(os.path.join(content_path, section_name)): # If the content folder doesn't already exist
            if not os.path.exists(os.path.join(theme_path, "sections", f"{section_name}.jinja")) and not os.path.exists(os.path.join(theme_path, "sections", f"{section_name}.html")): # If jinja theme doesn't already exist
                logging.debug("[ezcv cli.new_section()] Creating section folder")
                if not os.path.exists(os.path.join(content_path, section_name)):
                    os.mkdir(os.path.join(content_path, section_name))
                logging.debug("[ezcv cli.new_section()] Creating section theme file")
                if not os.path.exists(os.path.join(theme_path, "sections")):
                    os.mkdir(os.path.join(theme_path, "sections"))
                with open(os.path.join(theme_path, "sections", f"{section_name}.jinja"), 'w+') as section_file:
                    section_file.write(default_section_page_templte)
            else: # Theme file already existed
                print(f"{fg(1)}Could not create path, path already exists at either: \n\t{os.path.join(theme_path, 'sections', f'{section_name}.jinja')}\n\tor\n\t{os.path.join(theme_path, 'sections', f'{section_name}.jinja')}\n{fg(15)}")
                return 
        else: # Content folder already existed
            print(f"{fg(1)}Could not create path, path already exists at {os.path.join(content_path, section_name)}\n{fg(15)}")
            return 
        if not theme_metadata["sections"]:
            theme_metadata["sections"] = {}
        theme_metadata["sections"][section_name] = {"type": "markdown" if "m" in section_type else "gallery"}
        print(f"Section successfully created\n\nTheme file created at:\n\t{os.path.join(theme_path, 'sections', f'{section_name}.jinja')}\nContent folder created at:\n\t{os.path.join(content_path, section_name)}")
    elif type(default_section_page_templte) == defaultdict:
        os.mkdir(os.path.join(theme_path, "sections", section_name))
        if not os.path.exists(os.path.join(content_path, section_name)):
            os.mkdir(os.path.join(content_path, section_name))
        if default_section_page_templte["single"]:
            with open(os.path.join(theme_path, "sections", section_name, "single.jinja"), 'w+') as section_file:
                section_file.write(default_section_page_templte["single"])
        if default_section_page_templte["feed"]:
            with open(os.path.join(theme_path, "sections", section_name, "feed.jinja"), 'w+') as section_file:
                section_file.write(default_section_page_templte["feed"])
        if default_section_page_templte["overview"]:
            with open(os.path.join(theme_path, "sections", section_name, "overview.jinja"), 'w+') as section_file:
                section_file.write(default_section_page_templte["overview"])
        if not theme_metadata["sections"]:
            theme_metadata["sections"] = {}
        theme_metadata["sections"][section_name] = {"fields":{"title": {"required": True, "type":"str"},"created": {"required": True, "type":"str"},"updated": {"required": True, "type":"str"}, },"type": "blog"}
        theme_metadata["sections"][section_name]["single"] = bool(default_section_page_templte["single"])
        theme_metadata["sections"][section_name]["overview"] = bool(default_section_page_templte["overview"])
        theme_metadata["sections"][section_name]["feed"] = bool(default_section_page_templte["feed"])
        print(f"Section successfully created\n\nTheme file(s) created at:\n\t{os.path.join(theme_path, 'sections', f'{section_name}')}(remember to add your CSS)\nContent folder created at:\n\t{os.path.join(content_path, section_name)}")
    with open(os.path.join(theme_path, "metadata.yml"), 'w+') as metadata_file:
        yaml.dump(dict(theme_metadata), metadata_file)

def optimize(directory:str = "site"):
    """Goes through and minifies html, css, js and image files in directory

    Notes
    -----
    - This assumes you are following the standard template layout: https://ezcv.readthedocs.io/en/latest/theme-development/#folder-layout
    - Only image extensions supported are:

        - .jpg
        - .png
        - .jpeg

    Parameters
    ----------
    directory : str
        The directory you want to minify all files from
    """
    logging.debug(f"[ezcv cli.optimize({directory=})] Optimizing files")
    # Minify html/css/js
    html = glob(f'{directory}{os.sep}*.html')
    css = glob(f'{os.path.join(os.path.join(directory, "css"))}{os.sep}*.css')
    js = glob(f'{os.path.join(os.path.join(directory, "js"))}{os.sep}*.js')

    for file in html:
        logging.debug(f"[ezcv cli.optimize()] Processing html file: {file}")
        process_single_html_file(file, overwrite=True)
    
    for file in css:
        logging.debug(f"[ezcv cli.optimize()] Processing css file: {file}")
        process_single_css_file(file, overwrite=True)
    
    for file in js:
        logging.debug(f"[ezcv cli.optimize()] Processing js file: {file}")
        process_single_js_file(file, overwrite=True)

    # Find and process images
    png = glob(f'{os.path.join(os.path.join(directory, "images"))}{os.sep}*.png')
    jpg = glob(f'{os.path.join(os.path.join(directory, "images"))}{os.sep}*.jpg')
    jpeg = glob(f'{os.path.join(os.path.join(directory, "images"))}{os.sep}*.jpeg')

    for extension in [png, jpg, jpeg]:
        if extension: # if list is not empty
            for image in extension:
                logging.debug(f"[ezcv cli.optimize()] Processing image file: {image}")
                pil_object = Image.open(image)
                pil_object.save(image, optimize=True, quality=85)

def main():
    """The primary entrypoint for the ezcv cli"""
    args = docopt(usage, version=version)
    logging.debug(f"[ezcv cli.main()] Arguments: {args}")

    if len(argv) == 1: # Print usage if no arguments are given
        print("\n", usage)
        exit()

    if args["--preview"] and not args["build"]:
        preview()

    elif args["init"]:
        if args["<theme>"] and args["<name>"]: # Both a theme and name are specified
            init(args["<theme>"], args["<name>"], flask=args["--flask"])
        elif args["<name>"]: # Only a name is specified
            init(name = args["<name>"], flask=args["--flask"])
        else: # No values are specified
            init(flask=args["--flask"])
        exit()

    elif args["build"]:
        if not args["--dir"]:
            generate_site()
        else:
            generate_site(args["--dir"])

        if args["--optimize"]:
            if args["--dir"]:
                optimize(args["--dir"])
            else:
                optimize()
        exit()

    elif args["theme"]:
        if args["--metadata"]:
            if not args["<theme>"]:
                args["<theme>"] = get_site_config()["theme"]
            theme(args["--list"], args["--copy"], args["<theme>"], metadata=True)
            exit()
        elif args["<theme>"]:
            theme(args["--list"], args["--copy"], args["<theme>"])
            exit()
        elif args["--copy"]: # If copy is flagged, but no theme is provided
            if os.path.exists("config.yml"):
                theme(args["--list"], args["--copy"], get_site_config()["theme"])
            else: # If no theme, or config.yml file is present
                theme(args["--list"], args["--copy"], "freelancer")
            exit()
        elif args["--list"]:
            theme(args["--list"])
            exit()
        else: # If theme argument is called with no other flags
            print("\n", usage)
            exit()
    
    elif args["section"]:
        if not args["--type"]:
            args["--type"] = "markdown"
        section(args["<SECTION_NAME>"], args["--type"])
        exit()

    elif args["--preview"]: # If preview flag is specified with no other flags
        preview()
        exit()

    else: # No top level argument is provided
        print("\n", usage)
        exit()

if __name__ == "__main__": # For testing
    main()
