"""Contains utilities related to theme management, discovery and creation including:

- Section template discovery and creation
- Remote repo management
- Theme discovery & updating


"""

# Standard Library Dependencies 
import os                    # Used for path validation and manipulation
import shutil                    
import tempfile              # Used to generate temporary folders for downloads
from zipfile import ZipFile  # Used to extract all directories from zip archives

# Third Party Depenencies
import requests
from tqdm import tqdm

THEMES_FOLDER = os.path.join(os.path.dirname(__file__), "themes")

def get_theme_section_directories(theme_folder:str, sections:list = []) -> list:
    """Gets a list of the available sections

    Parameters
    ----------
    sections : (list, optional)
        A list of sections names, or an empty list if they need to be searched for

    theme_folder : str
        The path to the theme folder

    Returns
    -------
    list
        The name(s) of the section templates that exist within the sections list
    """
    if sections:
        return sections
    if not sections and os.path.exists(os.path.join(theme_folder, "sections")):
        for section in os.listdir(os.path.join(theme_folder, "sections")):
            if section.endswith(".jinja"):
                section = section.replace(".jinja", "")
                sections.append(section)
    return sections

def setup_remote_theme(name: str, url: str):
    """downloads a remote theme (zip file) and extracts it to cwd

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

def locate_theme_directory(theme:str, site_context:dict) -> str:
    """Preprocess theme folder, and find correct path

    Parameters
    ----------
    theme : str
        [description]

    site_context : dict
        [description]

    Returns
    -------
    str
        [description]

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
    else:
        raise FileNotFoundError(f"Theme {theme} does not exist")

    return theme_folder
