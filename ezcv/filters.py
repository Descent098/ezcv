"""This is a module that provides additional jinja filters to help with theme development

Functions
---------
inject_filters() -> jinja2.Environment:
    Takes in a jinja environment and injects the filters from this module + functions fom the extra_filters parameter

split_to_sublists() -> List[list]:
    Takes a list and splits it into sublists of size n

get_image_path() -> str:
    Takes in the path to an image and returns it in usable format to use in img tags as src attribute

get_filename_without_extension() -> str:
    Takes in path and returns filename without extension

pretty_datetime() -> str:
    A utility function for pretty printing dates provided for jobs/getting a degree/volunteering etc

pretty_defaultdict() -> str:
    Returns a prettyprinted form of a defaultdict
"""
# Standard library dependencies
import logging
from pprint import pformat                     # Used to help pretty print dictionaries
from inspect import stack, currentframe        # Used to get error messages from jinja templates
from typing import Callable, DefaultDict, List # Used to typehint accurately for inline documentation


# Third Party Dependencies
import jinja2           # Used mostly to typehint and allow for autocompletion in the file


def inject_filters(env:jinja2.Environment, extra_filters:List[Callable] = None) -> jinja2.Environment:
    """Takes in a jinja environment and injects the filters from this module + functions fom the extra_filters parameter

    Parameters
    ----------
    env : jinja2.Environment
        The existing environment you want to inject the filters into

    extra_filters : List[Callable], optional
        An optional set of method objects containing additional filter functions you want to use

    Returns
    -------
    jinja2.Environment
        The input environment with the filters injected
    """
    if extra_filters is None:
        extra_filters = []
    logging.debug("[ezcv inject_filters()]: Beggining to inject filters")
    filters = [split_to_sublists, get_image_path, get_filename_without_extension, pretty_datetime, pretty_defaultdict]

    if extra_filters:
        logging.debug("[ezcv inject_filters()]: Extra filters found")
        for current_filter in extra_filters:
            filters.append(current_filter)

    for current_filter in filters:
        env.filters[current_filter.__name__] = current_filter

    return env


def split_to_sublists(initial_list:list, n:int, strict:bool=True) -> List[list]:
    """Takes a list and splits it into sublists of size n

    Parameters
    ----------
    initial_list : list
        The initial list to split into sublists

    n : int
        The size of each sublist

    strict: bool
        Whether to force an error if the length of the initial list is not divisible by n (split into even groups), default True

    Returns
    -------
    List[list]
        A list of lists of size n (unless strict is False, then the last list may be > n)

    Examples
    --------

    ### Split gallery images into sublists of 3

    #### JINJA USAGE
    ```jinja2
    {% if gallery|length % 3 == 0 %}
    {% for sublist in gallery|split_to_sublists(3) %}
        <div class="row">

        <div class="col-md-4">
            <img src="{{ sublist.0[0]['file_path'] }}" alt="{{ sublist.0[0]['file_path'].split()[-1] }}">
        </div>

        <div class="col-md-4">
            <img src="{{ sublist.1[0]['file_path'] }}" alt="{{ sublist.1[0]['file_path'].split()[-1]}}">
        </div>

        <div class="col-md-4">
            <img src="{{ sublist.2[0]['file_path'] }}" alt="{{ sublist.2[0]['file_path'].split()[-1] }}">
        </div>

        </div>
    {% endfor %}
    {% endif }
    ```

    The above jinja is roughly equivalent to something like this in pure python:

    ```python
    gallery = ["image 1" , "image 2", "image 3", "image 4" , "image 5", "image 6"]

    if len(images) % 3 == 0:
        for sublist in split_to_sublists(gallery, 3): # Returns [["image 1" , "image 2", "image 3"], ["image 4" , "image 5", "image 6"]]
        ... # Do stuff with each sublist
    ```
    """
    logging.debug(f"[ezcv split_to_sublists({initial_list}, {n}, {strict})]: Beggining filter function")
    if strict and not len(initial_list) % n == 0:
            raise ValueError(f"\033[;31m Provided list was not of correct size: \n\tList: {initial_list}\n\tSegment size {n} \033[0m")

    result = []

    for i in range(0, len(initial_list), n): # Create sublists up to size n 
        result.append( initial_list[i:i + n])

    return result

def get_image_path(path:str) -> str:
    """Takes in the path to an image and returns it in usable format to use in img tags as src attribute

    Parameters
    ----------
    path : str
        The raw image path from metadata

    Returns
    -------
    str
        The string corresponding to the correct path to use in img tags src attributes

    Examples
    --------
    ### Passing in an image path from a project in the projects section:

    #### JINJA USAGE
    ```jinja2
    {% for project in projects %}
        {% if project[0]["image"] %}
            <img src="{{ project[0]['image'] | get_image_path }}" alt="{{ project[0]['image'] | get_filename_without_extension }}" />
        {% endif %}
    {% endfor %}
    ```

    The above jinja is roughly equivalent to something like this in pure python:

    ```python
    project = [{"image": "image.jpg"}, ["other stuff"]]

    if project[0]["image"]:
        print(get_image_path(project[0]['image'])) # Prints /images/image.jpg which is a usable path

    project = [{"image": "https://example.com/img/image.jpg"}, ["other stuff"]]

    if project[0]["image"]:
        print(get_image_path(project[0]['image'])) # Prints https://example.com/img/image.jpg which is a usable path
    ```
    """
    logging.debug(f"[ezcv get_image_path({path})]: Beggining to find image path")
    try:
        if path.startswith("http"):
            return path

        elif path.startswith("images"):
            return f"{path}"

        else:
            return f"images/{path}"
    except AttributeError:
        for frameInfo in stack(): # Get the frame for the error raised
            if frameInfo.frame.f_globals.get("__jinja_template__") is not None: # Find the jinja template namespace if it exists
                template = frameInfo.frame.f_globals.get("__jinja_template__")
                break
        if not path: # If the image path is False (usually because a required image wasn't provided)
            raise ValueError(f"\033[;31m No path provided for a required image in {template.filename} #line {template.get_corresponding_lineno(currentframe().f_back.f_lineno)} \nCheck your themes documentation for details on which images are required (likely in config.yml): https://ezcv.readthedocs.io/en/latest/included-themes/ \033[0m")
        else: # If it's just an invalid image path
            raise ValueError("\033[;31m Could not get image path: {path}\n Error occured on \n{template.filename} #line {template.get_corresponding_lineno(currentframe().f_back.f_lineno)} \nCheck documentation on image management for details https://ezcv.readthedocs.io/en/latest/usage/#image-management\033[0m")

def get_filename_without_extension(path:str) -> str:
    """Takes in path and returns filename without extension

    Parameters
    ----------
    path : str
        The original path to file

    Returns
    -------
    str
        Then name without the extension on the end

    Examples
    --------
    ### Take in an image path and return the filename without extension to use for alt tag

    #### JINJA USAGE
    ```jinja2
    {% for project in projects %}
        {% if project[0]["image"] %}
            <img src="{{ project[0]['image'] | get_image_path }}" alt="{{ project[0]['image'] | get_filename_without_extension }}" />
        {% endif %}
    {% endfor %}
    ```

    The above jinja is roughly equivalent to something like this in pure python:

    ```python
    project = [{"image": "/path/to/John Doe.jpg"}, ["other stuff"]]

    if project[0]["image"]:
        print(get_filename_without_extension(project[0]['image'])) # Prints "John Doe"
    ```
    """
    logging.debug(f"[ezcv get_filename_without_extension({path})]: Beggining to find filename without path")
    return str(path.split("/")[-1].split(".")[0])

def pretty_datetime(month_started:str, year_started:str, month_ended:str, year_ended:str, current:bool) -> str:
    """A utility function for pretty printing dates provided for jobs/getting a degree/volunteering etc

    Parameters
    ----------
    month_started : str
        The month started i.e. October

    year_started : str
        The year started i.e. 2013

    month_ended : str
        The month ended i.e. December

    year_ended : str
        The year ended i.e. 2017

    current : bool
        A boolean describing if this is somewhere you are currently working/studying/volunteering at

    Returns
    -------
    str
        A pretty string of the date i.e. 'October 2013 - December 2017'

    Examples
    --------
    ### Printing the date details of a degree in the `education` section:

    #### JINJA USAGE
    ```jinja2
    {% for experience in education %}
        {{ experience[0]["month_started"] | pretty_datetime(experience[0]["year_started"], experience[0]["month_ended"], experience[0]["year_ended"], experience[0]["current"]) }}
    {%endfor%}
    ```

    The above jinja is roughly equivalent to something like this in pure python:

    ```python

    month_started = "October"
    year_started = "2013"

    month_ended = "December"
    year_ended = "2017 

    current = False

    print(pretty_datetime(month_started, year_started, month_ended, year_ended, current)) # October 2013 - December 2017
    ```
    """
    logging.debug(f"[ezcv pretty_datetime({month_started}, {year_started}, {month_ended}, {year_ended}, {current}))]: Pretty printing datetime")
    
    if month_started or year_started:
        if month_started and year_started:
            beginning = f"{month_started} {year_started}"
        elif month_started:
            beginning = f"{month_started}"
        elif year_started:
            beginning = f"{year_started}"
        sep = " - "
    else:
        sep = ""

    if current:
        end = "Present"
    
    elif month_ended or year_ended:
        if month_ended and year_ended:
            end = f"{month_ended} {year_ended}"
        elif month_ended:
            end = f"{month_ended}"
        elif year_ended:
            end = f"{year_ended}"
    else:
        end = ""
    logging.debug(f"[ezcv pretty_datetime({month_started}, {year_started}, {month_ended}, {year_ended}, {current}))]: result = {beginning}{sep}{end}")
    return f"{beginning}{sep}{end}"


def pretty_defaultdict(ugly_dict:DefaultDict) -> str:
    """Returns a prettyprinted form of a defaultdict

    Parameters
    ----------
    ugly_dict : DefaultDict
        A defaultdictionary to pretty print

    Notes
    -----
    Needs to be used with the safe filter to work properly

    Returns
    -------
    str
        The 

    Examples
    --------
    ### Pretty printing the `config` defaultdictionary:

    #### JINJA USAGE
    ```jinja2
    {{ config | pretty_defaultdict | safe }}
    ```

    The above jinja is roughly equivalent to something like this in pure python:

    ```python
    from ezcv.core import get_site_config

    config = get_site_config()

    print(pretty_defaultdict(config)) # Prints config dict in pretty form
    ```
    """
    logging.debug(f'[ezcv pretty_defaultdict({ugly_dict})]: Pretty printing defaultdict')

    return pformat(dict(ugly_dict)).replace("\n", "<br>").replace("{", "{<br>").replace("}", "<br>    }")
