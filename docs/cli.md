# CLI

Here is the full usage for the CLI, but see below for specifics of each command:

```bash
Usage:
    ezcv [-h] [-v] [-p]
    ezcv build [-d OUTPUT_DIR] [-o]
    ezcv init [<name>] [<theme>] [-f]
    ezcv theme [-l] [-c] [-m] [<theme>]
    ezcv section <SECTION_NAME> [-t=<type>]


Options:
-h, --help            show this help message and exit
-v, --version         show program's version number and exit
-l, --list            list the possible themes
-c, --copy            copy the provided theme, or defined site theme
-p, --preview         preview the current state of the site
-o, --optimize        Optimize output files (takes longer to run)
-f, --flask           Generate Flask routes and requirements.txt
-d OUTPUT_DIR, --dir OUTPUT_DIR The folder name to export the site to
-m, --metadata        Generate metadata for the theme
-t=<type>, --type=<type> The type of section to generate [default: markdown]
```

## Init

This command is used to initialize projects from the command line. There are two optional positional arguments for the person's name and which theme to use:

```bash
ezcv init <name> <theme>
```

**Example**

If your name is Kieran and you want to use the aerial theme you could do:

```bash
ezcv init Kieran aerial
```

Which will create a site at ```/Kieran``` and set ```theme: aerial``` in the ```config.yml``` file. Along with the ```config.yml``` a demo folder structure and demo files are generated (but will be ignored unless ```examples:true``` is set in the ```config.yml``` file).

## Preview

To preview your site simply go to the root (where ```config.yml``` is) and run:

```bash
ezcv -p
```

*Note that your browser Cache may cause some issues when switching themes, please hard refresh (usually ctrl + r). Additionally **DO NOT** proxy the port for this preview, it is not designed to be a production-ready http server*

## Build

The build command is used to export the site's HTML. 

```bash
ezcv build --dir="site"
```

There are two optional flags:

- The ```--dir``` flag for giving a custom name to the output directory (default is "site")
- If you want to build the site and optimize the files after building (slower build times, but makes site faster) then use ``-o`` or ``--optimize``. Note this only works with themes using the [official folder structure](https://ezcv.readthedocs.io/en/latest/theme-development/#folder-layout), and the image minification will also clear any exif data.

**Example**

If you want to create a site at ```./my_site```:

```bash
ezcv build --dir="my_site"
```

If you want to create a site at ```./site``` that has it's files optimized you could do:

```bash
ezcv build -o
```

If you want to create a site at ```./my_site``` that has it's files optimized you could do:
```bash
ezcv build --dir="my_site" -o
```

## Theme

This command is used to get information about themes and/or copy theme files for customization.

```bash
ezcv theme -l -c <theme>
```

There are two optional flags and one positional argument:

- ```-l``` indicates you want to see a list of the available themes
- ```-c``` indicates you want to copy a theme
  - First it will check if a ```<theme>``` argument has been passed, and if it has it will copy that theme
  - Then it will check if there's a ```config.yml``` file in the current directory and copy that one
  - Then it will just default to exporting the dimension theme
- ```-m``` used to generate metadata file (note will also copy into project folder if not already there, and `required_config` will not be specified)


**Examples**

*List all available themes*

```bash
ezcv theme -l
```

*Copy the theme used in a ```config.yml``` file in the same directory*

```bash
ezcv theme -c
```

*Copy the aerial theme*

```bash
ezcv theme -c aerial
```

*Generate a `metadata.yml` file for provided theme in the ```config.yml``` file in the same directory (note copies the theme if it's not already in the project directory)*

```bash
ezcv theme -m
```

## Section

This command is used to create new sections

```bash
ezcv section <SECTION_NAME> [-t=<type>]
```

*Note that if a section exists it will just print details about the section*

There are two optional flags and one positional argument:

- ```-t``` The type of section to generate [default: markdown], can be a few options:
  - `m` or `markdown`: Generate markdown section
  - `g` or `gallery`: Generate gallery section
  - `b` or `blog`: Generate blog section, note you can control which theme files to generate (by default all 3 will be generated but you can optionally specify 1-3 other letters)
    - Add an `s` to generate `single.jinja` (i.e. `ezcv section <SECTION_NAME> -t bs`)
    - Add an `f` to generate `feed.jinja` (i.e. `ezcv section <SECTION_NAME> -t bf`)
    - Add an `o` to generate `overview.jinja` (i.e. `ezcv section <SECTION_NAME> -t bo`)

*Create a new markdown section called books in the current theme*

```bash
ezcv section books
```

or

```bash
ezcv section "books" -t m
```

or

```bash
ezcv section books --type="markdown"
```

*Create a new gallery section called gallery in the current theme*

```bash
ezcv section gallery -t g
```

*Create a new blog section called blog (with all 3 jinja files) in the current theme*

```bash
ezcv section blog -t b
```

*Create a new blog section called blog with only single templates in the current theme*

```bash
ezcv section blog -t bs
```

*Create a new blog section called blog with only overview and feed templates in the current theme*

```bash
ezcv section blog -t bof
```

*Print details about existing section called 'blog'*

```bash
ezcv section blog
```
