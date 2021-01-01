"""TODO"""
# Standard Lib Dependencies
import os
import shutil
import webbrowser
from collections import defaultdict

# Third Party Dependencies
import yaml
import jinja2
import markdown
from tqdm import tqdm

# The global list of currently supported first party sections
SECTIONS_LIST = ["projects", "education", "work_experience", "volunteering_experience"]


def get_site_config(config_file_path: str = "config.yml") -> defaultdict:
    """Gets the site config from provided file path and returns defaultdict of values

    Parameters
    ----------
    config_file_path : str, optional
        The path to the config file, by default "config.yml"

    Returns
    -------
    defaultdict
        The configuration, if any key is not present defaults to False
    """
    with open(config_file_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    # Convert config dict to defaultdict so that all empty values are False instead of giving KeyNotFoundError
    default_dict_config = defaultdict(lambda: False)

    for key in config: # Copy config dict to default_dict_config
        default_dict_config[key] = config[key]

    return default_dict_config


def render_section(theme_folder:str, section_content_dir:str, examples:bool = False) -> str:
    """Renders the particular section provided using the environment provided

    Parameters
    ----------
    theme_folder : (str)
        The absolute path to the theme

    section_content_dir : (str)
        The name of the section to render i.e. projects, education, work_experience etc.

    examples : (bool, optional)
        If False then markdown files that have example in the name are ignored, by default False

    Returns
    -------
    str
        The rendered theme of the section, or an empty string if no content was found

    Examples
    --------
    ### Render projects section
    ```
    # NOTE: This example assumes you have a folder with projects at ./projects and a section theme at <ezcv install directory>/themes/freelancer/projects.jinja

    from ezcv import render_section

    theme = "freelancer"
    section = "projects" # The relative path to the content folder for this 

    theme_folder = os.path.abspath(os.path.join(os.path.dirname(ezcv.__file__), "themes", theme))

    # render projects html
    render_section(theme_folder, section)
    ```
    """
    contents = [] # Will be filled with each file in the sections' metadata and markdown content
    content_folder = False # Set to True if current section is in /content/<section>

    # Initialize jinja loaders
    theme_loader = jinja2.FileSystemLoader(theme_folder)
    environment = jinja2.Environment(loader=theme_loader, autoescape=True, trim_blocks=True) # Grab all files in theme_folder

    # If content for current section is stored within a folder called /content/<section>
    if os.path.exists(os.path.join("content", section_content_dir)): 
        content_folder = True

    section_theme_path = f"sections/{section_content_dir}.jinja" # Where in the theme folder to find the section theme

    # The folder to iterate through and find sections markdown files
    content_iteration_directory = os.path.join("content", section_content_dir) if content_folder else section_content_dir

    for content in os.listdir(content_iteration_directory): # Iterate through project files and generate markdown
        if examples:
            if content.endswith(".md"):
                with open(f"{content_iteration_directory}{os.sep}{content}", "r") as mdfile: # Parse markdown file
                    text = mdfile.read()

                md = markdown.Markdown(extensions=['meta']) # Setup markdown parser with extensions
                page_html = md.convert(text) # Convert the markdown content text to hmtl
                page_meta = defaultdict(lambda:False)
                # Grab the metadata from the frontmatter of the markdown file
                for key in md.Meta: # Copy config dict to default_dict_config
                    if type(md.Meta[key]) == list:
                        page_meta[key] = md.Meta[key][0]
                    else:
                        page_meta[key] = md.Meta[key]
                contents.append([page_meta, page_html])

        else: # if files with example in the name should be ignored
            if content.endswith(".md") and (not "example" in content):
                with open(f"{content_iteration_directory}{os.sep}{content}", "r") as mdfile: # Parse markdown file
                    text = mdfile.read()

                md = markdown.Markdown(extensions=['meta']) # Setup markdown parser with extensions
                page_html = md.convert(text) # Convert the markdown content text to hmtl
                page_meta = defaultdict(lambda:False)
                # Grab the metadata from the frontmatter of the markdown file
                for key in md.Meta: # Copy config dict to default_dict_config
                    if type(md.Meta[key]) == list:
                        page_meta[key] = md.Meta[key][0]
                    else:
                        page_meta[key] = md.Meta[key]
                contents.append([page_meta, page_html])

    if len(contents) > 0:
        try:
            theme = environment.get_template(section_theme_path)
        except jinja2.TemplateNotFound: # If current section is not supported
            print(f"Section {section_content_dir.split(os.sep)[-1]} is not available")
            return ""
        return theme.render({section_content_dir:contents})
    else:
        return ""


def render_page(theme_folder:str, page:str, site_context:dict) -> str:
    """Renders the page provided from the specified theme

    Parameters
    ----------
    theme_folder : (str)
        [description]

    page : (str)
        [description]

    site_context : (dict)
        [description]

    Returns
    -------
    str
        The rendered html of the page
    """
    # Initialize jinja loaders
    theme_loader = jinja2.FileSystemLoader(theme_folder)
    environment = jinja2.Environment(loader=theme_loader, autoescape=True, trim_blocks=True) # Grab all files in theme_folder

    # generate new index
    theme = environment.get_template(page)
    return theme.render(site_context)

def export(site_context:dict, theme_folder:str, output_folder:str = "site", pages:list=["index.jinja"]):
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
            shutil.copyfile(os.path.join("images", file), os.path.join(output_image_dir, file))

    ## Copy images in content directories
    ### TODO

    # Iterate through top level pages and write to the output folder
    print("\nGenerating output html from theme")
    pages_iterator = tqdm(pages)
    pages_iterator.set_description_str("Generating top level pages")
    for page in pages_iterator:  # Write new pages
        html = render_page(theme_folder, page, site_context)
        if page.endswith(".jinja"):
            page = f"{page[:-6:]}.html"
        pages_iterator.set_description_str(f"Writing {page}")
        pages_iterator.refresh()
        with open(f"{output_folder}{os.sep}{page}", "w+") as outfile:
            outfile.write(html)


def generate_site(output_folder:str="site", theme:str = "freelancer", sections: list = SECTIONS_LIST, config_file_path="config.yml", preview:bool = False):
    """The primary entrypoint to generating a site

    Parameters
    ----------
    output_folder : (str, optional)
        The folder to output the site files to, by default "site"

    theme : (str, optional)
        The name of the theme to use, by default "freelancer"

    sections : (list[str], optional)
        A list of the sections to include in export, by default ezprez.core.SECTIONS_LIST

    config_file_path : (str, optional)
        The path to the site's config yaml file, by default "config.yml"

    preview : (bool, optional)
        If true then the index.html will be auto opened in the system webbrowser, by default False

    Notes
    -----
    - theme options are: 
        - freelancer; https://startbootstrap.com/theme/freelancer
        - aerial; https://html5up.net/aerial
        - creative; https://startbootstrap.com/theme/creative
        - dimension; https://html5up.net/dimension
        - ethereal; https://html5up.net/ethereal
        - strata; https://html5up.net/strata
    - Available sections are:
        - Projects (projects)
        - Education (education)
        - Volunteering experience (volunteering_experience)
        - Work Experience (work_experience)

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

    generate_site(output_folder="resume", sections=["projects"])
    ```
    """
    print(f"Exporting site to {output_folder}")
    pages = [] # Filled with a list of all the pages to render

    # The data passed to render all pages
    site_context = {"config": get_site_config(config_file_path)} 

    # If no theme argument, and a theme is defined in the site config file
    if site_context["config"]["theme"] and theme == "freelancer": 
        theme = site_context["config"]["theme"]

    # Preprocess theme folder, and find correct path
    if os.path.exists(os.path.abspath(theme)):
        theme_folder = os.path.abspath(theme)
    elif os.path.exists(os.path.abspath(os.path.join("themes", theme))):
        theme_folder = os.path.abspath(os.path.join("themes", theme))
    elif os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "themes", theme))):
        theme_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "themes", theme))
    else:
        raise ValueError(f"theme {theme} does not exist")

    # Get a list of all the top level pages in the theme folder and add them to the pages list
    for top_level_file in os.listdir(theme_folder):
        if top_level_file.endswith(".jinja") or top_level_file.endswith(".html"):
            pages.append(top_level_file)
    
    # Go through each section, render the html and add it to the site context
    print("\nGenerating content from sections")
    sections_iterator = tqdm(sections)
    sections_iterator.set_description_str("Writing section content")
    for section in sections_iterator: 
        html = render_section(theme_folder, section, site_context["config"]["examples"])
        site_context[f"{section}_html"] = html

    # Generate and export all the pages of a site
    export(site_context, theme_folder, output_folder, pages)

    if preview:
        browser_types = ["chromium-browser", "chromium", "chrome", "google-chrome", "firefox", "mozilla", "opera", "safari"] # A list of all the types of browsers to try
        for browser_name in browser_types:
            try:
                webbrowser.get(browser_name) # Search for browser
                break # Browser has been found
            except webbrowser.Error:
                continue
        webbrowser.open(f"file:///{os.path.abspath(output_folder)}/index.html")
