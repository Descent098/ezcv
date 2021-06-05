# CLI

Here is the full usage for the CLI, but see below for specifics of each command:

```bash
Usage:
    ezcv [-h] [-v] [-p]
    ezcv init [<name>] [<theme>]
    ezcv build [-d OUTPUT_DIR] [-p]
    ezcv theme [-l] [-c] [-s SECTION_NAME] [<theme>]


Options:
-h, --help            show this help message and exit
-v, --version         show program's version number and exit
-l, --list            list the possible themes
-c, --copy            copy the provided theme, or defined site theme
-p, --preview         preview the current state of the site
-d OUTPUT_DIR, --dir OUTPUT_DIR The folder name to export the site to
-s SECTION_NAME, --section SECTION_NAME The section name to initialize
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

**Note that preview is also available in the build command**

## Build

The build command is used to export the site's HTML. 

```bash
ezcv build --dir="site" -p
```

There are two optional flags:

- The ```--dir``` flag for giving a custom name to the output directory (default is "site")
- If you want to preview after the build (```-p```)

**Example**

If you want to create a site at ```./my_site``` and preview it after building you would do:

```bash
ezcv build --dir="my_site" -p
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
- ```-s``` Used to create a new section in a theme


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

*Create a new section called books in the current theme*

```bash
ezcv theme -s books
```

or

```bash
ezcv theme --section="books"
```