"""This module is for handling all the functionality around content including:

- Getting the list of content directories
- Getting the metadata and contents of content files for sections
- Classes for parsing all extensions

Classes
-------
Content:
    Base class for other Content types

Markdown:
    Used for parsing markdown content

Image:
    Used for parsing images

Functions
-------
get_content_directories() -> List[str]:
    Gets a list of the existing content directories i.e. ["projects", "education"]

get_section_content() -> List[List[Union[defaultdict, str]]]:
    Takes in a section folder and gets all the content from the files using the Content subclass asigned to the file extension

"""
# Standard Lib Dependencies
import os                                                # Used primarily in path validation
import logging                                           # Used to log information for internal testing
import datetime                                          # Used for date formatting and date validation
from collections import defaultdict                      # Used to give dicts default args
from dataclasses import dataclass, field                 # Used to improve class performance
from typing import DefaultDict, List, Tuple, Type, Union # Used to provide accurate type hints


# Third Party Dependencies
import exifread            # Used to get metadata of image files
import markdown            # Used to render and read markdown files
from colored import fg     # Used to highlight output with colors, especially errors/warnings


def get_content_directories() -> List[str]:
    """Gets a list of the existing content directories i.e. ["projects", "education"]

    Returns
    -------
    List[str]:
        The list of existing content directories i.e. ["projects", "education"]
    """
    logging.debug("[ezcv get_content_directories()] Getting content directories")
    result:list[str] = []
    for current_path in os.listdir("content"):
        if os.path.isdir(os.path.join("content", current_path)):
            result.append(os.path.join("content", current_path))

    logging.debug(f"[ezcv get_content_directories()] result {result}")
    return result


def get_section_content(section_content_folder: str, examples: bool = False, blog:bool = False) -> List[List[Union[defaultdict, str]]]:
    """Takes in a section folder and gets all the content from the files using the Content subclass asigned to the file extension

    Parameters
    ----------
    section_content_folder : str
        The string representation of the path to the section folder (i.e. 'content/education')

    examples : bool, optional
        Whether or not to render files with example in the name, by default False
    
    blog : bool, optional
        Whether or not the current section is a blog section, by default False

    Returns
    -------
    List[List[Union[defaultdict, str]]]
        A list representing each file in the section of sublists where the metadata is the first element (as a defaultdict), and the HTML is the second (as a string)


    Examples
    --------
    getting the section content of the education section

    ```
    from ezcv.content import get_section_content

    section_content_folder = 'content/education'

    content = get_section_content(section_content_folder)

    print(content[0]) # Prints [defaultdict(<function <lambda> at 0x000001F1B97CE040>, {'title': 'This is the title', 'company': 'This is the company'}), '<p>This is some content</p>']
    ```
    """
    logging.debug(f"[ezcv get_section_content({section_content_folder=}, {examples=}, {blog=})] Getting section content for {section_content_folder}")
    content:List[List[Union[defaultdict, str]]] = []
    extension_handlers:DefaultDict[str, Type] = Content.get_available_extensions()
    logging.debug("[ezcv get_section_content()] Beggining file iteration")
    for file_name in os.listdir(section_content_folder):                   # Iterate through the section_content folder and get the content from each file
        if not examples and file_name.startswith("example"):
            continue
        else:
            logging.debug(f"[ezcv get_section_content()] Getting content for {file_name}")
            extension = "." + file_name.lower().split(".")[-1]      # Get the file extension
            if extension_handlers[extension]:                       # Checking if there exists a Content subclass capable of handling the file
                extension_handler = extension_handlers[extension]() # Instantiate the proper extension

                # Get the content and add it to the list
                if not blog:
                    metadata, html = extension_handler.get_content(os.path.join(section_content_folder, file_name))
                    content.append([metadata, html])
                else:
                    metadata, html = extension_handler.get_content(os.path.join(section_content_folder, file_name))
                    # TODO: Add data if not there
                    if not metadata["created"]:
                        metadata["created"] = datetime.datetime.now().strftime("%Y-%m-%d")
                    if not metadata["updated"]:
                        metadata["updated"] = datetime.datetime.now().strftime("%Y-%m-%d")
                    

                    content.append([metadata, html, file_name])
    logging.debug(f"[ezcv get_section_content()] Returning section content {content=}")
    return content


@dataclass
class Content(dict):
    """Base class for other Content types

    Notes
    -----
    - All subclasses are assumed to have implemented:
        - __metadata__(); Returns a defaultdict of metadata
        - __html__(); Returns the HTML to render
        - A list attribute called extensions, for example in markdown it would be
            extensions:List[str] = ['.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.mdwn']

    Methods
    -------
    get_available_extensions() -> DefaultDict[str, Type]:
        Returns a defaultdict of available extensions and corresponding types to render them

    Raises
    ------
    NotImplementedError
        If any of __metadata__(), or __html__() are not implemented in subclass

    Examples
    --------
    ### Get the list of extensions and their handlers
    ```
    extension_handlers = Content.get_available_extensions()
    print(extension_handlers) ''' defaultdict(
        <function Content.get_available_extensions.<locals>.<lambda> at 0x00000240878690D0>, 
        {
        '.md': <class '__main__.Markdown'>, 
        '.markdown': <class '__main__.Markdown'>,
        '.jpg': <class '__main__.Image'>,
        '.png': <class '__main__.Image'>
        }
    )'''

    # Get an extension handler for a specific extension (in thise case .md files)
    print(extension_handlers[".md"]) # <class '__main__.Markdown'>
    ```

    ### Get content of a list of files
    ```
    content = [] # The list that
    filenames = ['file.md', 'image.jpg'] # Gotten from somewhere else
    extension_handlers = Content.get_available_extensions()

    for current_file in filenames:
        extension = '.' + current_file.split('.')[-1]
        if extension_handlers[extension]:
            extension_handler = extension_handlers[extension]()
            metadata, html = extension_handler.get_content(current_file)
            content.append([metadata, html])
    ```
    """


    def get_available_extensions() -> DefaultDict[str, Type]:
        """Returns a defaultdict of extensions and corresponding child types to handle them

        Returns
        -------
        DefaultDict[str, Type]:
            A defaultdict with a str for the extension as a key, and the type as a value
        """
        logging.debug("[ezcv Content.get_available_extensions()] Getting available extensions")
        all_extensions:DefaultDict[str, Type] = defaultdict(lambda:False)
        for current_class in Content.__subclasses__():
            for extension in current_class.extensions:
                all_extensions[extension] = current_class

        logging.debug(f"[ezcv Content.get_available_extensions()] Found extensions {all_extensions=}")
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

    Notes
    -----
    - Default extensions are 
        - [footnotes](https://python-markdown.github.io/extensions/footnotes/)
        - [tables](https://python-markdown.github.io/extensions/tables/)
        - [toc (Table of contents)](https://python-markdown.github.io/extensions/toc/)
        - [abbr(abbreviations)](https://python-markdown.github.io/extensions/abbreviations/)
        - [def_list(Definition lists)](https://python-markdown.github.io/extensions/definition_lists/)
        - [sane_lists(Sane lists)](https://python-markdown.github.io/extensions/sane_lists/)
        - [meta](https://python-markdown.github.io/extensions/meta)
        - [mdx_math](https://github.com/mitya57/python-markdown-math)
        - [mermaid](https://github.com/oruelle/md_mermaid)

    Examples
    --------
    ```
    from ezcv.content import Markdown

    html, metadata = Markdown().get_content('file_1.md')
    ```
    """
    md:markdown.Markdown = markdown.Markdown(extensions=['meta', 'footnotes', 'tables', 'toc', 'abbr', 'def_list', 'sane_lists', "mdx_math", "md_mermaid"]) # Setup markdown parser with extensions
    extensions:List[str] = (".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn")


    def __metadata__(self) -> defaultdict:
        """Gets the metadata from the YAML frontmatter of the markdown file

        Notes
        -----
        - This class requires __html__ to be run first, or self.md to be set manually and run self.md.convert(text:str) over the text of the document

        Returns
        -------
        defaultdict
            Returns a defaultdict with the yaml metadata of a peice of content
        """
        logging.debug("[ezcv Markdown.__metadata__()] Getting metadata")
        metadata:defaultdict = defaultdict(lambda:False)
        for key in self.md.Meta: # Create defaultdict out of metadata
            if type(self.md.Meta[key]) == list:
                metadata[key] = self.md.Meta[key][0]
            else:
                metadata[key] = self.md.Meta[key]
        logging.debug(f"[ezcv Markdown.__metadata__()] Returning metadata {metadata=}")
        return metadata


    def __html__(self, file_path:str) -> str:
        """Parses the markdown file and returns a string with the resulting HTML

        Parameters
        ----------
        file_path : str
            The path to the file to generate the HTML for

        Returns
        -------
        str
            The HTML rendered from the markdown file
        """
        logging.debug(f"[ezcv Markdown.__html__()] Getting HTML for {file_path=}")
        with open(f"{file_path}", "r") as mdfile: # Parse markdown file
            text = mdfile.read()
        html = self.md.convert(text) # Convert the markdown content text to hmtl
        logging.debug(f"[ezcv Markdown.__html__()] Returning HTML for {file_path=}")
        return html


    def get_content(self, file_path: str) -> Tuple[defaultdict, str]:
        """Gets the html content of a file, and the metadata of the file

        Parameters
        ----------
        file_path : str
            The path to the file to render

        Returns
        -------
        defaultdict, str
            Returns a defaultdict of the metadata first then the html content as a string

        Raises
        ------
        FileNotFoundError
            If the provided file path does not exist

        Examples
        --------
        Render a file called file_1.md
        ```
        from ezcv.content import Markdown

        metadata, html  = Markdown().get_content('file_1.md')
        ```
        """
        logging.debug(f"[ezcv Markdown.get_content()] Getting content for {file_path=}")
        if not os.path.exists(file_path): # If file doesn't exist
            raise FileNotFoundError(f"{fg(1)} Could not find file: {file_path}{fg(15)}\n")
        html = self.__html__(file_path)
        metadata = self.__metadata__()
        logging.debug(f"[ezcv Markdown.get_content()] Returning content for {file_path=}")
        return metadata, html


@dataclass
class Image(Content):
    """Used for parsing images
    
    Notes
    -----
    - Exif data is NOT available on PNG images (it is only available of jpg and tiff)
    - Since there are so many conditionals it is recommended to use the existing gallery stylesheet

    Examples
    --------
    Render a file called 1.jpg
    ```
    from ezcv.content import Image

    metadata, html = Image().get_content('1.jpg')
    ```
    """
    ignore_exif_data:bool = False
    extensions:List[str] = (".jpg", ".png", ".jpeg", ".gif", ".svg", ".webp", ".apng", ".jfif", ".pjpeg", ".pjp")
    image_paths:List[str] = field(default_factory=lambda: []) # TODO: find way to implement this properly


    def __metadata__(self, filename:str) -> defaultdict:
        """Return the metadata of the file (and exif data if available)

        Parameters
        ----------
        filename : str
            The path to the file to get the metadata from

        Returns
        -------
        defaultdict
            A defaultdict of the keys with the metadata in it
        """
        logging.debug(f"[ezcv Image.__metadata__()] Getting metadata for {filename=}")
        if self.ignore_exif_data:
            return defaultdict(lambda:False)

        elif filename.lower().endswith("jpg"):
            with open(filename ,"rb") as f:
                tags = exifread.process_file(f)
            tags = defaultdict(lambda:False, tags)
            logging.debug(f"[ezcv Image.__metadata__()] Returning EXIF Tags for {filename=} {tags=}")

            return tags

        else:
            logging.debug(f"[ezcv Image.__metadata__()] No EXIF Tags for {filename=}")
            return defaultdict(lambda:False)


    def __html__(self, tags:defaultdict) -> str:
        """Parses the tags of the image and returns HTML for the EXIF data

        Parameters
        ----------
        file_path : str
            The path to the file to generate the HTML for

        Returns
        -------
        str
            The HTML of the EXIF data from the file
        """
        logging.debug(f"[ezcv Image.__html__({tags=})] Getting HTML for {self.image_paths=}")
        html = ""

        # Lens detail
        if tags['EXIF LensModel']:
            html += f"<p class='lens'>{tags['EXIF LensModel']}</p>\n"
        
        # Focal length
        if tags['EXIF FocalLengthIn35mmFilm']:
            if tags['EXIF FocalLengthIn35mmFilm'] != tags['EXIF FocalLength']:
                html += f"<p class='focal-length'>{tags['EXIF FocalLengthIn35mmFilm']}mm (full frame equivalent)</p>\n"
            else:
                html += f"<p class='focal-length'>{tags['EXIF FocalLengthIn35mmFilm']}mm</p>\n"
        else:
            if tags['EXIF FocalLength']:
                html += f"<p class='focal-length'>{tags['EXIF FocalLength']}mm</p>\n"

        # ISO, Shutter speed, Apperture
        if tags['EXIF ISOSpeedRatings']:
            html += f"<p class='iso'>ISO {tags['EXIF ISOSpeedRatings']}</p>\n"
        if tags['EXIF ExposureTime']:
            html += f"<p class='shutter-speed'>{tags['EXIF ExposureTime']} Second(s)</p>\n"
        if tags['EXIF FNumber']:
            from fractions import Fraction
            tags['EXIF FNumber'] = str(float(Fraction(str(tags['EXIF FNumber'])))) # Convert aperture to str i.e. 6.3
            html += f"<p class='aperture'>f{tags['EXIF FNumber']}</p>\n"

        # Camera body details
        if tags['Image Make'] and tags['Image Model']:
            html += f"<p class='camera-type'>{tags['Image Make']} {tags['Image Model']}</p>\n"
        elif tags['Image Make']:
            html += f"<p class='camera-type'>{tags['Image Make']}</p>\n"
        elif tags["Image Model"]:
            html += f"<p class='camera-type'>{tags['Image Model']}</p>\n"
        else:
            ...
        return html


    def get_content(self, file_path: str) -> Tuple[defaultdict, str]:
        """Gets the html content of a file, and the metadata/exif of the file

        Parameters
        ----------
        file_path : str
            The path to the file to render

        Returns
        -------
        str, defaultdict
            Returns the defaultdict of the metadata, and then the html of the exif data

        Raises
        ------
        FileNotFoundError
            If the provided file path does not exist

        Examples
        --------
        Render a file called 1.jpg
        ```
        from ezcv.content import Image

        metadata, html = Image().get_content('1.jpg')
        ```
        """
        logging.debug(f"[ezcv Image.get_content()] Getting content for {file_path=}")
        tags = self.__metadata__(file_path)
        html = self.__html__(tags)
        tags["file_path"] = f"images/gallery/{file_path.split(os.path.sep)[-1]}"
        self.image_paths.append(file_path)
        return tags, html
