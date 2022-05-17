"""Contains all the configuration for the package on pip"""
import setuptools
from ezcv import __version__

def get_content(*filename:str) -> str:
    """Gets the content of a file or files and returns
    it/them as a string

    Parameters
    ----------
    filename : (str)
        Name of file or set of files to pull content from 
        (comma delimited)
    
    Returns
    -------
    str:
        Content from the file or files
    """
    content = ""
    for file in filename:
        with open(file, "r", encoding="utf-8") as full_description:
            content += full_description.read()
    return content

setuptools.setup(
    name = "ezcv",
    version = __version__,
    author = "Kieran Wood",
    author_email = "kieran@canadiancoding.ca",
    description = "An easy to use personal site generator",
    long_description = get_content("README.md", "CHANGELOG.md"),
    long_description_content_type = "text/markdown",
    project_urls = {
        "User Docs" :      "https://ezcv.readthedocs.io",
        "API Docs"  :      "https://kieranwood.ca/ezcv",
        "Forum":           "https://github.com/Descent098/ezcv/discussions",
        "Source" :         "https://github.com/Descent098/ezcv",
        "Bug Report":      "https://github.com/Descent098/ezcv/issues/new?assignees=Descent098&labels=bug&template=bug_report.md&title=%5BBUG%5D",
        "Feature Request": "https://github.com/Descent098/ezcv/issues/new?labels=enhancement&template=feature_request.md&title=%5BFeature%5D",
        "Roadmap":         "https://github.com/Descent098/ezcv/projects"
    },
    include_package_data = True,
    package_data = {"":["mkdocs.yml", "docs/*", "./themes/*"]},
    packages = setuptools.find_packages(),

    entry_points = { 
            'console_scripts': ['ezcv = ezcv.cli:main']
        },

    install_requires = [
    "docopt",                # Used for argument parsing if you are writing a CLI
    "pyyaml",                # Used for config file parsing
    "jinja2",                # used as middlewear for generating templates
    "markdown",              # Used to parse markdown
    "tqdm",                  # Used to generate progress bars
    "requests",              # Used to download remote themes
    "exifread",              # Used to read exif data from images
    "python-markdown-math",  # Used to render latex math equations
    "colored",               # Used to color terminal output for emphasis
    "pillow",                # Used to do image compression for optimized builds
    "css-html-js-minify",    # Used to minify html, css and JS files for optimized builds
    "md-mermaid",            # Used to render mermaid graphs in markdown
    "livereload",            # Used to auto-reload the site when changes are made
    "flask",                 # Used to create the web server for live reloading
        ],
    extras_require = {
        "dev" : ["mkdocs", # Used to create HTML versions of the markdown docs in the docs directory
                "pdoc3",   # Used to create development docs
                ], 

    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ],
)
