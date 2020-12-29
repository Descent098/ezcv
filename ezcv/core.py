import os
from collections import defaultdict
from shutil import copytree, ignore_patterns, rmtree
from typing import DefaultDict

import yaml
import markdown
import jinja2

sections_list = ["projects"]

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

def render_section(environment:jinja2.Environment, section_content_dir:str) -> str:
    """Renders the particular section provided using the environment provided

    Parameters
    ----------
    environment : jinja2.Environment
        The jinja environment tagged to the templates folder

    section_content_dir : str
        The name of the section to render i.e. projects, education, work_experience etc.

    Returns
    -------
    str
        The rendered template of the section, or an empty string if no content was found
    """
    contents = []

    section_template_path = f"sections/{section_content_dir}.jinja"
    for content in os.listdir(section_content_dir): # Iterate through project files and generate markdown

        if content.endswith(".md"):
            with open(f"{section_content_dir}{os.sep}{content}", "r") as mdfile: # Parse markdown file
                text = mdfile.read()

            md = markdown.Markdown(extensions=['meta']) # Setup markdown parser with extensions
            page_html = md.convert(text) # Convert the markdown content text to hmtl
            page_meta = md.Meta # Grab the metadata from the frontmatter of the markdown file
            contents.append([page_meta, page_html])

    print(f"{contents=}") # TODO: Remove
    if len(contents) > 0:
        template = environment.get_template(section_template_path)
        return template.render({section_content_dir:contents})
    else:
        return ""

def export(environment:jinja2.Environment, site_context:dict, template_folder:str, output_folder:str = "my_project"):
    if not os.path.exists(template_folder):
        raise FileNotFoundError(f"The provided template folder does not exist: {template_folder}")

    # generate new index
    template = environment.get_template("index.jinja")
    index_html = template.render(site_context)

    # Copy source files
    try:
        copytree(template_folder, output_folder, ignore=ignore_patterns("*.jinja"))
    except FileExistsError:
        rmtree(output_folder)
        copytree(template_folder, output_folder, ignore=ignore_patterns("*.jinja"))

    # Write new index
    with open(f"{output_folder}{os.sep}index.html", "w+") as outfile:
        outfile.write(index_html)

def generate_site(output_folder:str="my_project", template:str = "freelancer", sections: list = sections_list, config_file_path="config.yml"):
    """The primary entrypoint to generating a site

    Parameters
    ----------
    output_folder : (str, optional)
        The folder to output the site files to, by default "my_project"

    template : (str, optional)
        The name of the template to use, by default "freelancer"

    sections : (list[str], optional)
        [description], by default sections_list

    config_file_path : (str, optional)
        The path to the site's config yaml file, by default "config.yml"

    Notes
    -----
    - Template options are: 
        - freelancer; https://startbootstrap.com/theme/freelancer
        - aerial; https://html5up.net/aerial
        - creative; https://startbootstrap.com/theme/creative
        - dimension; https://html5up.net/dimension
        - ethereal; https://html5up.net/ethereal
        - strata; https://html5up.net/strata
    - Available sections are:
        - Projects TODO Finish options

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
    # Initialize jinja loaders
    template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates", template))
    template_loader = jinja2.FileSystemLoader(template_folder)
    template_env = jinja2.Environment(loader=template_loader, autoescape=True, trim_blocks=True) # Grab all files in template_folder

    # Debugging the current context 
    print(f"{template_env.list_templates()=}") # TODO: remove

    site_context = {"config": get_site_config(config_file_path)}
    for section in sections:
        html = render_section(template_env, section)
        site_context[f"{section}_html"] = html

    export(template_env, site_context, template_folder, output_folder)

if __name__ == "__main__":
    generate_site(sections=["projects"])
