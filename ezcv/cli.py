"""This is where you should include a module docstring to explain this file's functionality.

There are various formats SEE: https://canadiancoding.ca/posts/post/python/docstrings/
    For this example I will use numpystyle docstrings: https://numpydoc.readthedocs.io/en/latest/format.html

Variables
---------
This is where you mention any module-global variables.

Functions
---------
This is where you can specify any functions and what they return.

Notes
-----
Any other useful information.

References
----------
If you are implementing complicated functionality that has associated references (papers, videos, presentations etc.)
    leave links to them here.

Examples
--------
Any useful examples of basic usage of this module, make sure to enclose code in 3 backtics, this is
    interpreted by most modern IDE's as needing syntax highlighting which is quite useful. Here is an
    example:
    ```
    import this
    ```
"""

# Standard Lib Dependencies
import webbrowser
from sys import argv, exit

# Third party dependencies
from docopt import docopt

usage = """Usage:
    ezcv [-h] [-v] [-p]
    ezcv init [<template>]


Options:
-h, --help            show this help message and exit
-v, --version         show program's version number and exit
-p, --preview         preview the current state of the site
"""

def init(template="default"):
    ...

if __name__ == "__main__":
    args = docopt(usage, version="0.1.0")

    if len(argv) == 1: # Print usage if no arguments are given
        print("\n", usage)
        exit()

    if args["--preview"]:
        # TODO: Generate HTML/open HTML
        webbrowser.open() 
    
    elif args["init"]:
        if args["<template>"]:
            init(args["<template>"])
        else:
            init()
