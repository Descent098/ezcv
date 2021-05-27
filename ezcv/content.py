"""This module is for handling all the functionality around content including:
- Getting the list of content directories
- Getting the metadata and contents of content files for sections
"""


# Standard Lib Dependencies
import os
from typing import Any, DefaultDict, List, Type, Union # Used to create a 
from dataclasses import dataclass
from collections import defaultdict

# Third Party Dependencies
import markdown

@dataclass
class Content:
    """Base class for other Content types

    Notes
    -----
    - All subclasses are assumed to have implemented:
        - __enter__(); Implementation of "opening" context manager
        - __exit__(); Implementation of "closing" context manager
        - __metadata__(); Returns a defaultdict of metadata
        - __html__(); Returns the HTML to render

    Methods
    -------
    get_available_extensions() -> DefaultDict[str, Type]:
        Returns a defaultdict of available extensions and corresponding types to render them

    Raises
    ------
    NotImplementedError
        If any of __enter__(), __exit__(), __metadata__(), or __html__() are not implemented in subclass
    """
    file_path:str # The absolute/relative path to a file

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

    def __html__(self):
        """A function to be replaced with the specific implementation of generating HTML

        Raises
        ------
        NotImplementedError
            If the function is not implemented in the subclass
        """
        raise NotImplementedError

    def __enter__(self):
        """A function to be replaced with the specific implementation of "opening" the content

        Raises
        ------
        NotImplementedError
            If the function is not implemented in the subclass
        """
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        """A function to be replaced with the specific implementation of "closing" the content

        Raises
        ------
        NotImplementedError
            If the function is not implemented in the subclass
        """
        raise NotImplementedError


@dataclass
class Markdown(Content):
    md:markdown.Markdown = markdown.Markdown(extensions=['meta']) # Setup markdown parser with extensions
    html:str = ""
    extensions:List[str] = (".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn")

    def __metadata__(self) -> defaultdict:
        """Gets the metadata from the YAML frontmatter of the markdown file

        Returns
        -------
        defaultdict
            [description]
        """

        metadata:defaultdict = defaultdict(lambda:False)

        for key in self.md.Meta: # Create defaultdict out of metadata
            if type(self.md.Meta[key]) == list:
                metadata[key] = self.md.Meta[key][0]
            else:
                metadata[key] = self.md.Meta[key]

        return metadata


    def __html__(self) -> str:
        return self.html # Generated in self.__enter__()

    def __enter__(self):
        """The implementation of "opening" the content"""
        with open(f"{self.file_path}", "r") as mdfile: # Parse markdown file
            text = mdfile.read()
        self.html = self.md.convert(text) # Convert the markdown content text to hmtl
        return self

    def __exit__(self, error_type, value, traceback) -> bool:
        """The implementation of "closing" the content"""
        return isinstance(value, TypeError)


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





#TODO: remove
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
            if content.endswith(".md"):
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

