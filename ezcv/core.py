"""The module containing all primary functionality of ezcv including:

- Content parsing
- HTML generation
- Site exporting

Functions
---------
generate_site():
    The primary entrypoint to generating a site

get_site_config() -> defaultdict:
    Gets the site config from provided file path and returns defaultdict of values


Module Variables
----------------
SECTIONS_LIST (list[str]):
    The list of the first party supported sections

Examples
--------
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

# Standard Lib Dependencies
import os                           # Used for path validation
import shutil                       # Used for file/folder copying and removal
import logging                      # Used to log information for internal testing
from collections import defaultdict # Used to instatiate dictionaries with default arguments on unspecified keys
from typing import Callable, Union  # Used to add additional typehints to help with documentation and usage on functions

# Internal Dependencies
from ezcv.themes import *
from ezcv.content import *
from ezcv.filters import inject_filters

# Third Party Dependencies
import yaml                         # Used for config file parsing
import jinja2                       # used as middlewear for generating templates
from tqdm import tqdm               # Used to generate progress bars during iteration

# The global list of currently supported first party sections
SECTIONS_LIST = ["projects", "education", "work_experience", "volunteering_experience", "gallery", "blog"]

def get_site_config(config_file_path:str = "config.yml", remotes_file_path:str = os.path.join(THEMES_FOLDER, "remotes.yml")) -> defaultdict:
    """Gets the site config from provided file path and returns defaultdict of values

    Parameters
    ----------
    config_file_path : str, optional
        The path to the config file, by default "config.yml"

    Returns
    -------
    defaultdict:
        The configuration, if any key is not present it defaults to False
    """
    logging.debug(f"[ezcv get_site_config({config_file_path}, {remotes_file_path})]: Loading config file")
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Config file at {config_file_path} was not found")

    with open(config_file_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    logging.debug(f"[ezcv get_site_config({config_file_path}, {remotes_file_path})]: Loading remotes file")
    config["remotes"] = get_remote_themes(remotes_file_path)

    # Convert config dict to defaultdict so that all empty values are False instead of giving KeyNotFoundError
    default_dict_config = defaultdict(lambda: False, config)

    return default_dict_config


def _render_section(section_name:str, site_context:dict, environment:jinja2.Environment, blog:bool=False) -> str:
    """Renders the particular section provided using the environment provided

    Parameters
    ----------
    section_name : (str)
        The name of the section to render i.e. projects, education, work_experience etc.

    site_context: (dict)
        The dictionary containing the site's context

    environment : (jinja2.Environment)
        The jinja environment pre-loaded with the themes and filters

    blog : (bool, optional)
        Wheter or not the section is a blog, by default False

    Returns
    -------
    str:
        The rendered template of the section
    """
    logging.debug(f"[ezcv _render_section({section_name}, {site_context}, {environment})]: Begin rendering section")
    try:
        contents = site_context["sections"][section_name]
    except KeyError:
        print(f"Could not find content for section '{section_name}', skipping")
        if blog:
            return "", "", ""
        else:
            return ""

    logging.debug(f"[ezcv _render_section({section_name}, {site_context}, {environment})]: Rendering sections")
    if not blog: # Rendering sections that are not blog sections
    # If a section template exists set it to the path, else False i.e. if <theme folder>/sections/<section name>.jinja exists set it to that
        section_template_file = f"sections/{section_name}.jinja"
        if len(contents) > 0: # If there is any markdown content
            try:
                logging.debug("[ezcv _render_section()] Found markdown section")
                theme = environment.get_template(section_template_file)
            except jinja2.TemplateNotFound: # If current section is not supported
                print(f"Section {section_name} template is not available")
                return ""
            return theme.render({section_name:contents, "config": site_context["config"]})
        else:
            return ""
    else: # Rendering blog sections
        logging.debug("[ezcv _render_section()] Found blog section")
        overview_file = f"sections/{section_name}/overview.jinja"
        feed_file = f"sections/{section_name}/feed.jinja"
        single_file = f"sections/{section_name}/single.jinja"
        theme_folder = environment.loader.searchpath[0]
        overview_file_path = os.path.join(theme_folder, overview_file)
        feed_file_path = os.path.join(theme_folder, feed_file)
        single_file_path = os.path.join(theme_folder, single_file)
        if not overview_file_path:
            logging.debug("[ezcv _render_section()] No overview template file found")
            overview_file = ""
        if not feed_file_path:
            logging.debug("[ezcv _render_section()] No feed template file found")
            html = ""
        elif feed_file_path:
            if len(contents) > 0: # If there is any markdown content
                logging.debug("[ezcv _render_section()] Rendering feed file")
                html = environment.get_template(feed_file).render({section_name:contents, "config": site_context["config"]})
            else:
                html = ""
        if not single_file_path:
            logging.debug("[ezcv _render_section()] No single template file found")
            single_file = ""
        return single_file, overview_file, html


def _render_page(page:str, site_context:dict, environment:jinja2.Environment) -> str:
    """Renders the page provided from the specified theme

    Parameters
    ----------
    page : (str)
        The filename inside the theme folder to render i.e. 'index.jinja'

    site_context : (dict)
        A dictionary containing the config values, and all sections html

    environment : (jinja2.Environment)
        The jinja environment pre-loaded with the themes and filters

    Returns
    -------
    str:
        The rendered html of the page
    """
    logging.debug(f"[ezcv _render_page({page}, {site_context}, {environment})]: Begin rendering page")
    inject_filters(environment) # Add in custom filters
    # Render template and return contents
    theme = environment.get_template(page)
    return theme.render(site_context)


def _export(site_context:dict, theme_folder:str, environment:jinja2.Environment, output_folder:str = "site",  pages:list=None ):
    """Generates all the site html from pages specified and outputs them to the output folder

    Parameters
    ----------
    site_context : (dict)
        The site context containing all sections html and dict + config dict

    theme_folder : (str)
        The absolute path to the folder for the theme to use

    environment : (jinja2.Environment)
        The jinja environment pre-loaded with the themes and filters

    output_folder : (str, optional)
        The folder to output the HTML files to, by default "site"

    pages : (list, optional)
        The list of pages to use, by default None which gets set to ["index.jinja"]

    Raises
    ------
    FileNotFoundError
        If the provided theme folder does not exist
    """
    if pages is None:
        pages = ["index.jinja"]
    if not os.path.exists(theme_folder): # Error out if provided theme folder does not exist
        raise FileNotFoundError(f"The provided theme folder does not exist: {theme_folder}")

    # Copy source files
    try:
        shutil.copytree(theme_folder, output_folder, ignore=shutil.ignore_patterns("*.jinja"))

    except FileExistsError:
        shutil.rmtree(output_folder)
        shutil.copytree(theme_folder, output_folder, ignore=shutil.ignore_patterns("*.jinja"))
    
    # Copy images
    output_image_dir = os.path.join(output_folder, "images")
    if os.path.exists("images"):
        if not os.path.exists(output_image_dir): # Create output_folder/images if it's not present
            os.mkdir(output_image_dir)
        for file in os.listdir("images"): # Copy file from source images folder to output image directory
            # TODO: Add catch for if image already exists
            shutil.copyfile(os.path.join("images", file), os.path.join(output_image_dir, file))

    # Copy Gallery images
    output_fallery_image_dir = os.path.join(output_folder, "images", "gallery")
    if os.path.exists(os.path.join("content", "gallery")):
        if not os.path.exists(output_fallery_image_dir): # Create output_folder/images/gallery if it's not present
            os.mkdir(output_fallery_image_dir)
        for file in os.listdir(os.path.join("content", "gallery")): # Copy file from source images folder to output image directory
            # TODO: Add catch for if image already exists
            shutil.copyfile(os.path.join("content", "gallery", file), os.path.join(output_fallery_image_dir, file))

    # Iterate through top level pages and write to the output folder
    print("\nGenerating output html from theme")
    pages_iterator = tqdm(pages)
    pages_iterator.set_description_str("Generating top level pages")
    templates_list = environment.list_templates()
    for page in pages_iterator:  # Write new pages
        if type(page) == str: # Standard markdown sections
            try:
                html = _render_page(page, site_context, environment)
            except jinja2.UndefinedError as e:
                print(e)
                raise ValueError("A required configuration value is missing")
            if page.endswith(".jinja"):
                page = f"{page[:-6:]}.html"
            pages_iterator.set_description_str(f"Writing {page}")
            pages_iterator.refresh()
            with open(f"{output_folder}{os.sep}{page}", "w+") as outfile:
                outfile.write(html)
        elif type(page) == list: # Blog sections
            if len(page) == 2: # overview pages
                logging.debug(f"[ezcv _export()]: Rendering {page[0]} overview page")
                if not "sections/blog/overview.jinja" in templates_list:
                    print("[ezcv _export()]: No overview template found")
                    continue
                try:
                    html = _render_page(page[1], site_context, environment)
                except jinja2.UndefinedError as e:
                    print(e)
                    raise ValueError("A required configuration value is missing")
                if page[1].endswith(".jinja"):
                    page = f"{page[0]}.html"
                pages_iterator.set_description_str(f"Writing {page}")
                pages_iterator.refresh()
                with open(f"{output_folder}{os.sep}{page}", "w+") as outfile:
                    outfile.write(html)
            elif len(page) == 3: # Single pages
                logging.debug(f"[ezcv _export()]: Rendering {page[0]} single pages")
                if not "sections/blog/single.jinja" in templates_list:
                    print("[ezcv _export()]: No single blog post template found")
                    continue
                template_file = page[1]
                for content_file in page[2]:
                    if content_file[0]["title"]:
                        title = content_file[0]["title"]
                    else:
                        title = content_file[2].replace('.md', '')
                    if title == "index":
                        raise ValueError("The title of a blog post cannot be 'index'")
                    try:
                        single_page_context = {"config": site_context["config"], "content": [content_file[0], content_file[1]]}
                        html = _render_page(template_file, single_page_context, environment)
                    except jinja2.UndefinedError as e:
                        print(e)
                        raise ValueError("A required configuration value is missing")
                    if template_file.endswith(".jinja"):
                        page = f"{title}.html"
                    pages_iterator.set_description_str(f"Writing {page}")
                    pages_iterator.refresh()
                    with open(f"{output_folder}{os.sep}{page}", "w+") as outfile:
                        outfile.write(html)
    logging.debug("Cleaning up metadata.yml")
    if os.path.exists(os.path.join(output_folder, "metadata.yml")):
        os.remove(os.path.join(output_folder, "metadata.yml")) # Remove metadata file


def generate_site(output_folder:str="site", theme:str = "dimension", sections: list = None, config_file_path="config.yml", preview:bool = False, extra_filters:List[Callable] = None):
    """The primary entrypoint to generating a site

    Parameters
    ----------
    output_folder : (str, optional)
        The folder to output the site files to, by default "site"

    theme : (str, optional)
        The name of the theme to use, by default "dimension"

    sections : (list[str], optional)
        A list of the sections to include in export, by default []

    config_file_path : (str, optional)
        The path to the site's config yaml file, by default "config.yml"

    preview : (bool, optional)
        Changes generation to work for the autoreload server, by default False

    extra_filters : List[Callable], optional
        An optional set of method objects containing additional filter functions you want to use

    Notes
    -----
    - theme options are: 
        - aerial; https://html5up.net/aerial
        - base; included theme that can be used for debugging
        - creative; https://startbootstrap.com/theme/creative
        - cv; https://startbootstrap.com/theme/resume
        - dimension; https://html5up.net/dimension
        - ethereal; https://html5up.net/ethereal
        - freelancer; https://startbootstrap.com/theme/freelancer
        - Grayscale; https://startbootstrap.com/theme/grayscale
        - identity; https://html5up.net/identity
        - Lens; https://html5up.net/lens
        - Paradigm Shift; https://html5up.net/paradigm-shift
        - read_only; https://html5up.net/read-only
        - solid_state; https://html5up.net/solid-state
        - strata; https://html5up.net/strata
    - Available sections are:
        - Projects (projects)
        - Education (education)
        - Volunteering experience (volunteering_experience)
        - Work Experience (work_experience)
        - Gallery (gallery)
    - If sections is an empty list then the theme's section directory will be searched for themes

    Raises
    ------
    FileNotFoundError
        If the provided theme folder does not exist

    Examples
    --------
    Generating a site with all default settings
    ```
    from ezprez.core import generate_site

    generate_site()
    ```

    Generating a site that outputs to /resume and only generating the projects section
    ```
    from ezprez.core import generate_site

    generate_site(output_folder="my_site", sections=["projects"])
    ```
    """
    if sections is None:
        sections = []
    if extra_filters is None:
        extra_filters = []
    print(f"Exporting site to {output_folder}")
    pages = [] # Filled with a list of all the pages to render

    # The data passed to render all pages
    logging.debug("[ezcv] Initializing site context with config file")
    site_context:dict[str, Union[list, defaultdict, dict]] = {"config": get_site_config(config_file_path)}

    logging.debug("[ezcv] Getting ignore_exif_data config value")
    if site_context["config"]["ignore_exif_data"]:
        Image.ignore_exif_data = True

    # If no theme argument, and a theme is defined in the site config file
    logging.debug("[ezcv] Getting theme config value")
    if site_context["config"]["theme"] and theme == "dimension": 
        logging.debug(f"Using theme from site config file: {site_context['config']['theme']}")
        theme = site_context["config"]["theme"]

    # Find theme directory based on name, or download it if it's a remote theme
    logging.debug("[ezcv] Getting theme directory")
    theme_folder = locate_theme_directory(theme, site_context)
    logging.info(f"[ezcv] theme directory: {theme_folder}" )

    # Check required_config values
    if not os.path.exists(os.path.join(theme_folder, "metadata.yml")):
        new_metadata = dict(generate_theme_metadata(theme_folder))
        with open(os.path.join(theme_folder, "metadata.yml"), "w+") as outfile:
            yaml.dump(new_metadata, outfile)
    theme_metadata = get_theme_metadata(theme_folder)
    if theme_metadata["required_config"]:
        for value in theme_metadata["required_config"]:
            if not value in site_context["config"].keys():
                if not isinstance(theme_metadata["required_config"][value], dict):
                    theme_metadata["required_config"][value] = {"type": "str", "default": "", "description": ""}
                theme_metadata["required_config"][value]["default"] = theme_metadata["required_config"][value].get("default", "")
                theme_metadata["required_config"][value]["type"] = theme_metadata["required_config"][value].get("type", "str")
                theme_metadata["required_config"][value]["description"] = theme_metadata["required_config"][value].get("description", "")
                print(f"\n\x1b[31mThe theme requires the '{value}'configuration value \n\n\ttype: { theme_metadata['required_config'][value]['type'] } \n\tdescription: { theme_metadata['required_config'][value]['description'] }\n\n please add\n\n\x1b[37m\t {value}: <value> \n\n\x1b[31mto your config.yml file\x1b[37m")
                exit(1)

    # Initialize jinja loaders
    logging.debug("[ezcv] Initializing jinja2 loaders")
    theme_loader = jinja2.FileSystemLoader(theme_folder)
    environment = jinja2.Environment(loader=theme_loader, autoescape=True, trim_blocks=True) # Grab all files in theme_folder

    logging.debug("[ezcv] Injecting extra jinja filters into environment (if available)")
    environment = inject_filters(environment, extra_filters)

    # Initialize sections key in site context to empty dict
    site_context["sections"] = {}

    # Get a list of the section names, and section theme directories
    logging.debug("[ezcv] Getting info about sections content")
    sections = get_theme_section_directories(theme_folder, sections, preview) # TODO: Add support for blog sections
    sections_content_dirs = get_content_directories()
    logging.info(f"[ezcv] Found sections: {sections}\n[ezcv] Found section content directories: {sections_content_dirs}" )

    # Go through all section content files to get content (i.e. ./sections/education/*.md)
    logging.debug("[ezcv] Getting content for each section")
    for section in sections_content_dirs: 
        if not section.split(os.sep)[-1] == "blog": #TODO: make parametric
            # Get content to store in site_context["sections"][section]
            site_context["sections"][section.split(os.sep)[-1]] = get_section_content(section, site_context["config"]["examples"])
        else:
            # Get content to store in site_context["sections"][section]
            site_context["sections"][section.split(os.sep)[-1]] = get_section_content(section, site_context["config"]["examples"], blog=True)

    # Get a list of all the top level pages in the theme folder and add them to the pages list
    logging.debug("[ezcv] Getting list of top-level files (.jinja and .html)")
    for top_level_file in os.listdir(theme_folder):
        if top_level_file == "resume.jinja" and not site_context["config"]["resume"]: # Ignore resume.jinja if resume config var is False
            continue
        # TODO: add support for blog overview files
        if top_level_file.endswith(".jinja") or top_level_file.endswith(".html"):
            pages.append(top_level_file)
    
    # Go through each section, render the html and add it to the site context
    print("\nGenerating content from sections")
    logging.debug("[ezcv] Generating html from section content")
    sections_iterator = tqdm(sections)
    sections_iterator.set_description_str("Writing section content")
    for section in sections_iterator:
        if section == "blog": #TODO: Make parametric based on setup
            single_page, overview_page, feed_html = _render_section(section, site_context, environment, blog=True)
            if single_page or overview_page or feed_html:
                site_context[f"{section}_html"] = feed_html
                pages.append([section, overview_page])
                pages.append([section, single_page, site_context["sections"][section]])
        else:
            html = _render_section(section, site_context, environment)
            site_context[f"{section}_html"] = html

    # Generate and export all the pages of a site
    logging.debug("[ezcv] Generating html from pages")
    _export(site_context, theme_folder, environment, output_folder, pages)
