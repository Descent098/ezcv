"""TODO"""

# Standard Lib Dependencies
import os
import shutil
from sys import argv, exit

## internal dependencies
from ezcv.core import generate_site, SECTIONS_LIST

# Third party dependencies
from docopt import docopt

usage = """Usage:
    ezcv [-h] [-v] [-p]
    ezcv init [<name>] [<theme>]
    ezcv build [-d OUTPUT_DIR] [-p]


Options:
-h, --help            show this help message and exit
-v, --version         show program's version number and exit
-p, --preview         preview the current state of the site
-d OUTPUT_DIR, --dir OUTPUT_DIR The folder name to export the site to
"""



def init(theme="freelancer", name="John Doe"):
    print(f"Generating site at {os.path.abspath(name)}")

    shutil.copytree(os.path.join(os.path.dirname(__file__), "example_site"), os.path.abspath(name))

    # Generate initial config.yml file
    with open(os.path.join(name, "config.yml"), "w+") as config_file:
        config_file.write(f"# See https://ezprez.readthedocs.io for documentation\nname: {name}\ntheme: {theme}")

    print(f"Site generated and is available at {os.path.abspath(name)}")

def preview(temporary_foler_name = "asdfhlasdjkfhlasdjkfhasldkjfhalskfghd"):
    if not os.path.exists(temporary_foler_name):
        os.mkdir(temporary_foler_name)

    generate_site(temporary_foler_name, preview=True)
    input("Press enter when done previewing")
    shutil.rmtree(temporary_foler_name) # Clean up preview files

def main():
    args = docopt(usage, version="0.1.0")

    if len(argv) == 1: # Print usage if no arguments are given
        print("\n", usage)
        exit()

    if args["--preview"] and not args["build"]:
        preview()

    elif args["init"]:
        if args["<theme>"] and args["<name>"]: # Both a theme and name are specified
            init(args["<theme>"], args["<name>"])
        elif args["<name>"]: # Only a name is specified
            init(name = args["<name>"])
        elif args["<theme>"]: # Only a theme is specified
            init(args["<theme>"])
        else: # No values are specified
            init()

    elif args["build"]:
        if not args["--dir"]:
            generate_site()
        else:
            generate_site(args["--dir"])

        if args["--preview"]:
            preview()

if __name__ == "__main__": # For testing
    main()
