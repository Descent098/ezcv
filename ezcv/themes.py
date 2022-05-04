"""Contains utilities related to theme management, discovery and creation including:

- Section template discovery and creation
- Remote repo management
- Theme discovery & updating
"""

# Standard Library Dependencies 
import os                    # Used for path validation and manipulation
import shutil                # Used to make copying and deletion of paths easier
import datetime
import tempfile              # Used to generate temporary folders for downloads
from zipfile import ZipFile  # Used to extract all directories from zip archives
from collections import defaultdict

# Internal Dependencies
from ezcv.content import Markdown

# Third Party Depenencies
import yaml
import requests              # Used to access remote files
from tqdm import tqdm        # Used to generate progress bars during iteration

THEMES_FOLDER = os.path.join(os.path.dirname(__file__), "themes")

#TODO: Add a way to update themes from CLI, will require theme metadata to implement
def get_theme_section_directories(theme_folder:str, sections:list = [], preview:bool=False) -> list:
    """Gets a list of the available sections for a theme

    Explanation
    -----------
    Essentially this function goes into a theme folder (full path to a theme), looks for a folder 
    called sections and returns a list of all the .jinja files available stripped of the extension
    so i.e. if `<theme folder>/sections` had 3 files `education.jinja`, `work_experience.jinja` and
    `volunteering_experience.jinja` this function would return ['education', 'work_experience', 'volunteering_experience']

    Parameters
    ----------
    sections : (list, optional)
        A list of sections names, or an empty list if they need to be searched for

    theme_folder : str
        The full path to the theme folder (typically from calling locate_theme_directory() )

    preview : bool, optional
        Whether or not the caller is in preview mode (ignore existing sections), by default False

    Returns
    -------
    list
        The name(s) of the section templates that exist within the sections list without extensions
    """
    if preview:
        sections = []
        if os.path.exists(os.path.join(theme_folder, "sections")):
            for section in os.listdir(os.path.join(theme_folder, "sections")):
                if section.endswith(".jinja"):
                    section = section.replace(".jinja", "")
                    sections.append(section)
                elif os.path.isdir(os.path.join(theme_folder, "sections", section)): # blog sections
                    sections.append(section)
            return sections
        else:
            return []
    elif sections and not preview:
        return sections
    elif os.path.exists(os.path.join(theme_folder, "sections")):
        for section in os.listdir(os.path.join(theme_folder, "sections")):
            if section.endswith(".jinja"):
                section = section.replace(".jinja", "")
                sections.append(section)
            elif os.path.isdir(os.path.join(theme_folder, "sections", section)): # blog sections
                sections.append(section)
        return sections
    else:
        return []


def setup_remote_theme(name: str, url: str):
    """downloads a remote theme (zip file) and extracts it to the THEMES_FOLDER

    Parameters
    ----------
    name : str
        The name of the theme (will be the folder name for the theme also)

    url : str
        The URL to the .zip file
    """
    theme_folder_path = os.path.join(THEMES_FOLDER, name)

    if os.path.exists(theme_folder_path): # If theme folder already exists
        return # Exit function

    else: # Download remote theme

        # Setting up necessary download variables
        file_stream = requests.get(url, stream=True) # The open http request for the file
        chunk_size = 1024 # Setting the progress bar chunk size to measure in kb
        total_length = int(file_stream.headers.get('content-length')) # Getting file size

        # Setting up the download progress bar
        progress_bar = tqdm(total=total_length, unit='iB', unit_scale=True)
        progress_bar.set_description(f"Download progress for {name}:")

        # Write the incoming data stream to a file and update progress bar as it downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_folder_path = os.path.join(temp_dir, f"{name}.zip")
            
            with open(zip_folder_path, 'wb') as download_file: 
                for chunk in file_stream.iter_content(chunk_size): 
                    if chunk:
                        progress_bar.update(len(chunk))
                        download_file.write(chunk)
            print(f"file Downloaded to {zip_folder_path}")
            progress_bar.close()

            # Extract zip file to theme folder
            with ZipFile(zip_folder_path, "r") as archive:
                    archive.extractall(theme_folder_path) # Extract to theme folder
                    print(f"Extracted theme from {zip_folder_path} to folder {theme_folder_path}")

    # If theme is at THEME_FOLDER/<name>/<name> move code to THEME_FOLDER/<name>
    if os.path.exists(os.path.join(theme_folder_path, name)): 
        print(f"moving {os.path.join(theme_folder_path, name)} to {theme_folder_path}")
        for current_file in os.listdir(os.path.join(theme_folder_path, name)):
            shutil.move(os.path.join(theme_folder_path, name, current_file), os.path.join(theme_folder_path))
        shutil.rmtree(os.path.join(theme_folder_path, name))
    elif len(os.listdir(theme_folder_path)) == 1: # If only one file in theme folder
        print(f"moving {os.listdir(theme_folder_path)[0]} to {theme_folder_path}")
        theme_files = os.listdir(os.path.join(theme_folder_path, os.path.join(os.listdir(theme_folder_path)[0])))
        theme_files_folder = os.path.join(theme_folder_path, os.listdir(theme_folder_path)[0])
        print(f"Checking {theme_files=} and {theme_files_folder=}")
        if os.path.isdir(theme_files_folder): # If it's a folder
            for current_file in theme_files:
                print(f"moving {os.path.join(theme_files_folder, current_file)} to {os.path.join(theme_folder_path, current_file)}")
                shutil.move(os.path.join(theme_files_folder, current_file), os.path.join(theme_folder_path, current_file))


def locate_theme_directory(theme:str, site_context:dict) -> str:
    """Preprocess theme folder, and find correct full path to a theme

    Parameters
    ----------
    theme : str
        The name of the theme to locate

    site_context : dict
        The site context with the site configuration

    Returns
    -------
    str
        The path to the theme directory

    Raises
    ------
    FileNotFoundError
        If no theme folder exists, or remote is defined
    """
    if os.path.exists(os.path.abspath(theme)):
        theme_folder = os.path.abspath(theme)
    elif os.path.exists(os.path.abspath(os.path.join("themes", theme))):
        theme_folder = os.path.abspath(os.path.join("themes", theme))
    elif os.path.exists(os.path.abspath(os.path.join(THEMES_FOLDER, theme))):
        theme_folder = os.path.abspath(os.path.join(THEMES_FOLDER, theme))
    elif theme in site_context["config"]["remotes"]:
        setup_remote_theme(theme, site_context["config"]["remotes"][theme])
        theme_folder = os.path.abspath(os.path.join(THEMES_FOLDER, theme))
    elif theme.startswith("http"):
        theme_name = theme.split("/")[-1].replace(".zip", "")
        print(f"Downloading theme {theme_name} from {theme} to {os.path.join(THEMES_FOLDER, theme_name)}")
        setup_remote_theme(theme_name, theme)
        theme_folder = os.path.abspath(os.path.join(THEMES_FOLDER, theme_name))
    else:
        raise FileNotFoundError(f"Theme {theme} does not exist")

    return theme_folder


def get_remote_themes(remotes_file_path:str = os.path.join(THEMES_FOLDER, "remotes.yml")) -> dict:
    """Takes in the path to a yml/YAML file and returns a dict of name:url pairs to download themes

    Parameters
    ----------
    remotes_file_path : str, optional
        The path to the yml/YAML file that defines remote themes, by default os.path.join(THEMES_FOLDER, "remotes.yml")

    Returns
    -------
    dict
        A key-value pair of name to url of themes
    """
    import yaml
    if os.path.exists(remotes_file_path):
        with open(remotes_file_path, "r") as remotes_file:
            remotes = yaml.safe_load(remotes_file)

    return remotes


def get_theme_metadata(theme_folder:str) -> defaultdict:
    """Gets the data from the metadata.yml file in the theme folder

    Parameters
    ----------
    theme_folder : str
        The full path to the theme folder

    Returns
    -------
    defaultdict
        The metadata of the theme, all keys will return false if

    Examples
    --------
    Get the metadata of the dimensions theme
    ```
    from ezcv.themes import get_theme_metadata

    theme_name = "dimensions"

    metadata = get_theme_metadata(os.path.join(THEMES_FOLDER, theme_name))
    ```
    """

    # Get the metadata file
    with open(os.path.join(theme_folder, "metadata.yml"), "r") as metadata:
        data = yaml.safe_load(metadata)

    return defaultdict(lambda: False, data)


def _generate_fields(section_content_folder:str) -> dict:
    """Generates a dictionary of fields for a section

    Parameters
    ----------
    section_content_folder : str
        _description_

    Notes
    -----
    - The field types that exist are
        - str
        - datetime
        - bool
        - int

    Returns
    -------
    dict
        The dictionary for the fields i.e. {'fields':{'title': 'str', 'date': 'datetime'}}

    Raises
    ------
    ValueError
        If the content folder does not exist or does not contain exclusively markdown files

    Examples
    --------
    ```
    from ezcv.themes import _generate_fields
    
    fields = _generate_fields(os.path.join('content', 'dimension'))
    ```
    """
    fields = {}
    # section_content_folder would be like /content/education
    files = os.listdir(section_content_folder)
    if not files:
        raise ValueError(f"No files in {section_content_folder}")

    if files[0].endswith("md"):
        metadata, _ = Markdown().get_content(os.path.join(section_content_folder, files[0]))
        for field in metadata: # Get each field type from the first markdown file
            if type(metadata[field]) == str:
                if len(metadata[field]) == 10 and metadata[field][4] == "-" and metadata[field][7] == "-":
                    fields[field] = "datetime"
                elif metadata[field].isnumeric():
                    fields[field] = "int"
                elif metadata[field].lower() == "true" or metadata[field].lower() == "false":
                    fields[field] = "bool"
                else:
                    fields[field] = "str"
            elif type(metadata[field]) == datetime:
                fields[field] = "datetime"
            else:
                fields[field] = type(metadata[field]).__name__
    elif files[0].endswith(".jpg") or files[0].endswith(".png"):
        raise ValueError(f"There are no fields in image files: Directory {section_content_folder}")

    return fields


def generate_theme_metadata(theme_folder:str, force:bool=False) -> defaultdict:
    """Generates the metadata.yml file in the theme folder

    Parameters
    ----------
    theme_folder : str
        The full path to the theme folder

    force : bool, optional
        Whether to force the generation of the metadata file, by default False

    Notes
    -----
    - Will generate fields if a content folder relative to the current working directory is \
        present it will use the first file in the directory to determine the field types

    Returns
    -------
    defaultdict:
        The defaultdict of the content of the themes metadata.yml file

    Raises
    ------
    ValueError:
        If the theme folder does not exist or does not contain a index.jinja file

    Examples
    --------
    Generate metadata for the dimensions theme
    ```
    from ezcv.themes import generate_theme_metadata, THEMES_FOLDER

    data_2 = generate_theme_metadata(os.path.join(THEMES_FOLDER, 'dimension'))
    ```

    Generate metadata.yml file for the dimensions theme
    ```
    import yaml # Requires pyyaml
    from ezcv.themes import generate_theme_metadata, THEMES_FOLDER

    data_2 = generate_theme_metadata(os.path.join(THEMES_FOLDER, 'dimension'))

    with open(os.path.join(THEMES_FOLDER, 'dimension', 'metadata.yml'), 'w+') as metadata_file:
        yaml.dump(dict(data_2), metadata_file)
    ```
    """    
    if not os.path.exists(theme_folder):
        raise ValueError(f"Theme folder {theme_folder} does not exist")
    elif not os.path.exists(os.path.join(theme_folder, "index.jinja")):
        raise ValueError(f"Theme folder {theme_folder} does not contain an index.jinja file")
    elif os.path.exists(os.path.join(theme_folder, "metadata.yml")) and not force:
        return defaultdict(lambda:False, get_theme_metadata(theme_folder))

    data = defaultdict(lambda:False)
    data["name"] = os.path.basename(theme_folder)
    data["created"] = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
    data["updated"] = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"
    data["folder"] = os.path.basename(theme_folder)
    from ezcv import __version__ as version
    data["ezcv_version"] = version
    if os.path.exists(os.path.join(theme_folder, "sections")):
        data["sections"] = {}
        for section in os.listdir(os.path.join(theme_folder, "sections")):
            if os.path.isdir(os.path.join(theme_folder,"sections", section)):
                data["sections"][section] = {"type": "blog"}
                if os.path.isdir(os.path.join("content", section)):
                    data["sections"][section]["fields"] = _generate_fields(os.path.join("content", section))
                else:
                    data["sections"][section]["fields"] = {"current": "datetime", "updated": "datetime", "title": "str"}
                if os.path.exists(os.path.join(theme_folder, "sections", section, "single.jinja")):
                    data["sections"][section]["single"] = True
                else:
                    data["sections"][section]["single"] = False

                if os.path.exists(os.path.join(theme_folder, "sections", section, "overview.jinja")):
                    data["sections"][section]["overview"] = True
                else:
                    data["sections"][section]["overview"] = False

                if os.path.exists(os.path.join(theme_folder, "sections", section, "feed.jinja")):
                    data["sections"][section]["feed"] = True
                else:
                    data["sections"][section]["feed"] = False

            elif section == "gallery.jinja":
                data["sections"]["gallery"] = {"type": "gallery"}
            else:
                if os.path.isdir(os.path.join("content", section.replace(".jinja", ""))):
                    data["sections"][section.replace(".jinja", "")] = {"type": "markdown", "fields": _generate_fields(os.path.join("content", section.replace(".jinja", "")))}
                else:
                    data["sections"][section.replace(".jinja", "")] = {"type": "markdown"}
            # TODO: add support for gallery
    return data

def get_repo_last_updated(user_name:str="QU-UP", repo_name: str="ezcv-themes") -> datetime.datetime:
    """Get the last updated date of a github repository

    Parameters
    ----------
    user_name : str
        The name of the user or organization that owns the repository

    repo_name : str
        The name of the repository

    Returns
    -------
    datetime.datetime
        A datetime object representing the last updated date of the repository
    """
    response = requests.get(f'https://api.github.com/repos/{user_name}/{repo_name}/branches/master')
    date_changed = datetime.datetime.strptime(response.json()["commit"]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
    return date_changed
