"""This module is for handling all the functionality around content including:
- Getting the list of content directories
- Getting the metadata and contents of content files for sections
"""


# Standard Lib Dependencies
import os                                                # Used primarily in path validation
from collections import defaultdict                      # Used to give dicts default args
from dataclasses import dataclass                        # Used to improve class performance
from typing import DefaultDict, List, Tuple, Type, Union # Used to provide accurate type hints


# Third Party Dependencies
import markdown            # Used to render and read markdown files
from colored import fg     # Used to highlight output with colors, especially errors/warnings

@dataclass
class Content(dict):
    """Base class for other Content types

    Notes
    -----
    - All subclasses are assumed to have implemented:
        - __metadata__(); Returns a defaultdict of metadata
        - __html__(); Returns the HTML to render

    Methods
    -------
    get_available_extensions() -> DefaultDict[str, Type]:
        Returns a defaultdict of available extensions and corresponding types to render them

    Raises
    ------
    NotImplementedError
        If any of __metadata__(), or __html__() are not implemented in subclass
    """


    def get_available_extensions() -> DefaultDict[str, Type]:
        """Returns a defaultdict of extensions and corresponding child types to handle them

        Returns
        -------
        DefaultDict[str, Type]:
            A defaultdict with a str for the extension as a key, and the type as a value
        """
        all_extensions:DefaultDict[str, Type] = defaultdict(lambda:False)
        for current_class in Content.__subclasses__():
            for extension in current_class.extensions:
                all_extensions[extension] = current_class
        return all_extensions


    def __metadata__(self):
        """A function to be replaced with the specific implementation of generating metadata defauldict

        Raises
        ------
        NotImplementedError
            If the function is not implemented in the subclass
        """
        raise NotImplementedError


    def get_content(self, file_path:str):
        """Generates the metadata and HTML from a peice of content

        Parameters
        ----------
        file_path : str
            The path to the md file

        Raises
        ------
        NotImplementedError
            If the function is not implemented in the subclass
        """
        raise NotImplementedError


    def __html__(self, file_path:str):
        """A function to be replaced with the specific implementation of generating HTML

        Parameters
        ----------
        file_path: (str)
            The path for the file

        Raises
        ------
        NotImplementedError
            If the function is not implemented in the subclass
        """
        raise NotImplementedError


@dataclass
class Markdown(Content):
    """Used for parsing markdown content

    Examples
    --------
    ```
    from ezcv.content import Markdown

    html, metadata = Markdown().get_content('file_1.md')
    ```
    """
    md:markdown.Markdown = markdown.Markdown(extensions=['meta']) # Setup markdown parser with extensions
    extensions:List[str] = (".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn")


    def __metadata__(self) -> defaultdict:
        """Gets the metadata from the YAML frontmatter of the markdown file

        Notes
        -----
        - This class requires __html__ to be run first, or self.md to be set manually

        Returns
        -------
        defaultdict
            Returns a defaultdict with the yaml metadata of a peice of content
        """

        metadata:defaultdict = defaultdict(lambda:False)
        for key in self.md.Meta: # Create defaultdict out of metadata
            if type(self.md.Meta[key]) == list:
                metadata[key] = self.md.Meta[key][0]
            else:
                metadata[key] = self.md.Meta[key]
        return metadata


    def __html__(self, file_path:str) -> str:
        with open(f"{file_path}", "r") as mdfile: # Parse markdown file
            text = mdfile.read()
        html = self.md.convert(text) # Convert the markdown content text to hmtl
        return html # Generated in self.__enter__()


    def get_content(self, file_path: str) -> Tuple[str, defaultdict]:
        """Gets the html content of a file, and the metadata of the file

        Parameters
        ----------
        file_path : str
            The path to the file to render

        Returns
        -------
        str, defaultdict
            Returns the html first as a string and a defaultdict of the metadata

        Raises
        ------
        FileNotFoundError
            If the provided file path does not exist

        Examples
        --------
        Render a file called file_1.md
        ```
        from ezcv.content import Markdown

        html, metadata = Markdown().get_content('file_1.md')
        ```
        """
        if not os.path.exists(file_path): # If file doesn't exist
            raise FileNotFoundError(f"{fg(1)} Could not find file: {file_path}{fg(15)}\n")
        html = self.__html__(file_path)
        metadata = self.__metadata__()
        return html, metadata


# def get_section_content_new(section_folder: str, examples: bool = False) -> List[Type[Content]]:
#     content:List[Type[Content]] = []

#     extension_handlers:DefaultDict[str, Type] = Content.get_available_extensions()
#     if not examples:
#         filenames = [os.path.abspath(filename) for filename in os.listdir(section_folder) if os.path.isfile(filename) and not filename.startswith("example")]
#     else:
#         filenames = [os.path.abspath(filename) for filename in os.listdir(section_folder) if os.path.isfile(filename)]
#     for current_file in filenames:
#         extension = "." + current_file.split(".")[-1]
#         if extension_handlers[extension]:
#             with extension_handlers[extension](current_file) as file_instance:
#                 content.append(file_instance)
#     ...


def get_content_directories() -> List[str]:
    """Gets a list of the existing content directories i.e. ["projects", "education"]

    Returns
    -------
    List[str]:
        The list of existing content directories i.e. ["projects", "education"]
    """
    result:list[str] = []
    for current_path in os.listdir("content"):
        if os.path.isdir(os.path.join("content", current_path)):
            result.append(os.path.join("content", current_path))
    return result


# NOTE: This will be deprecated and replaced with the new content system in the next release
def get_section_content(section_folder: str, examples: bool = False) -> List[List[Union[defaultdict, str]]]:
    """Gets the markdown content and metadata from each file in a given section

    Parameters
    ----------
    section_folder : (str)
        The folder path to the sections content folder i.e. ./content/projects

    examples : (bool, optional)
        Whether or not to include markdown files that have example in the name, by default False

    Returns
    -------
    List[List[defaultdict, str]]:
        A list of lists with the metadata of each page at index 0 and the content at index 1,
            returns and empty list if the folder does not exist or is empty

    Examples
    --------
    Get the contents of the ./projects content folder
    ```
    from ezcv.content import get_section_content

    contents = get_section_content("projects")
    ```
    """
    if not os.path.exists(section_folder):
        return []

    contents:List[List[defaultdict, str]] = []

    # Iterate through project files and generate markdown
    for content in os.listdir(section_folder): 
        if examples:
            if content.endswith(".md") or content.endswith(".markdown"):
                with open(f"{section_folder}{os.sep}{content}", "r") as mdfile: # Parse markdown file
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

        else: # if files with example at the start
            if content.endswith(".md") and not content.startswith("example"):
                with open(f"{section_folder}{os.sep}{content}", "r") as mdfile: # Parse markdown file
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
    return contents
