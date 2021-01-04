# Quick start

Everything you need to get you up and running with ezcv. 

There are two different ways to get started:

- Local installation
- Remote editing

If you are familiar with git, github and markdown then I would recommend starting from [Local Installation](#local-installation).

If you are unfamiliar with any of the above then see directly below for getting started with remote editing.

## Remote editing

...

## Local Installation

To use ezcv you will need python 3.6+ (earlier versions wont work) and pip for python 3.

### From PyPi

1. Run ```pip install ezcv```

### From source

1. Clone this repo: [https://github.com/Descent098/ezcv](https://github.com/Descent098/ezcv)
2. Run ```pip install .``` or ```sudo pip3 install .```in the root directory

## Getting started

The easiest way to get started is by running:

```ezcv init <name>```

Replacing the ```<name>``` argument with your name (use "" if you want to use your full name i.e. ```ezcv init "Kieran Wood"```). 

### File structure

When you run the command a new folder will be created with your name, and some starter files like this:

**Legend**

| Icon | Meaning |
|------|---------|
|📁| File Folder |
|📷| Image file |
|📝| File you should edit/delete |
|📄| File you don't need to edit/shouldn't delete |

```
📁<name>/
├── 📁.github/
│   └── 📁workflows/
│       └── 📄ezcv-publish.yml
├── 📁content/
│   ├── 📁education/
│   |   ├── 📝example-current.md
│   |   └── 📝example-old.md
│   ├── 📁projects/
│   |   └── 📝example.md
│   ├── 📁volunteering_experience/
│   |   ├── 📝example-current.md
│   |   └── 📝example-old.md
│   └── 📁volunteering_experience/
│       ├── 📝example-current.md
│       └── 📝example-old.md
├── 📁images/
│   ├── 📷 abstract-landscape.jpg
│   └── 📷 ice-caps.jpg
├── 📄.gitignore
└── 📝config.yml
```

From here you can go into your ```config.yml``` file and [pick a theme](https://ezcv.readthedocs.io/en/latest/included-themes/), then start filling out your content according to what's available for the theme.

To preview your content use:

```ezcv -p```

If you're on github then pushing the contents to master/main will activate the publish workflow and automatically publish the site to ```<username>.github.io```.


## Configuration Settings

Each site will have a ```config.yml``` file, this file is in the [YAML format](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) and defines settings for configuring your site. Below are the list of **all** of the first-party supported fields.

*See [config example](#configuration-file-example) for an example file.*

| Field name | description | options |
|------------|-------------|---------|
| **name** | The name of who's site this is | Any name |
| **background** | Path to an image if the theme uses a background image | A path or url to an image file |
| **avatar** | Path to an image of the person who's site it is | A path or url to an image file |
| **email** | The email of who's site this is | Any valid email (i.e. example@example.com) |
| **phone** | The phone number of who's site this is | Any valid phone number (i.e. 123-134-1324) |
| **biography** | A biography of who's site this is | Any text (use ```|``` or ```>``` to span multiple lines see [config example](#configuration-file-example) below for details) |
| **role** | The role/job title of who's site this is| Any text (i.e. CEO) |
| **company** | The company of employment for who's site this is | Any text (i.e. Google) |
| **address** | Your physical address | The full text of your address |
| **social** | Social media links | github, twitch, youtube, instagram, twitter, snapchat, linkedin, facebook |
| **examples** | Whether to include content files that have example in the name | true or false |
| **theme** | The name of the theme to use | the name of any included theme i.e. dimension |

</br>

### Configuration File Example

Here is an example ```config.yml``` file with every field (they can be in any order):

```yaml
name: Your Name
background: background.png # An image to use as a background for the site
avatar: avatar.png # The avatar/profile picture of the person's site
email: email@example.com
phone: 123-123-1234
biography: | # Used to allow the description to go across multiple lines
  A vivid and succinct description of yourself.
  This biography is so important it spans multiple lines.
role: Your job role/title (i.e. CEO)
company: Company name
address: 123 first street SE
social:
  github: descent098 # Your username on github 
  twitch: username # Your username on twitch (everything after https://twitch.tv) i.e. https://twitch.tv/canadiancoding would be canadiancoding
  youtube: /channel/channel-ID or custom_url # Your custom url (i.e. https://youtube.com/mkbhd would be just mkbhd) or see this guide to find your channel ID: https://support.google.com/youtube/answer/3250431?hl=en
  instagram: username # Your username
  twitter: handle # Your handle (without the @)
  snapchat: username # Username others use to add you
  linkedin: name # go to linkedin and go to your profile, your name will be at the end of the url i.e. www.linkedin.com/in/<name>
  facebook: your id # go to facebook and go to your profile, your ID will be at the end of the url i.e. www.facebook.com/<your id>
examples: true # If you want to include the example.md files in your final build (good for developing new themes)
theme: dimension # Which of the included themes to use
```
## Sections

Sections is the name given to the content you use to fill your site. For example if you have content that lists your work experience then that would be a section.

### First Party sections

Here is the list of first party sections supported (check each theme to see which of these is supported):

```
Projects: Various projects you have worked on in the past
Education: Your education at various educational institutions
Publications: Any publications that you've made (site, article, book etc.)
Work Experience: Any current/old work experience that you want to include
Volunteering Experience: Your current/old volunteer experience that you want to include
```

## Image management

To include images in your site add them to the images folder (in the same spot as your ```config.yml``` file).

From there, there's two possible ways to include images:

1. In the metadata of a file, for example in ```/content/projects/example.md``` you will see an image field.
2. Inline in a file, like if you wanted to include an image of a diagram in a file.

To include an image in the metadata of a file, you just simply put the filename. For example if you have ```abstract-landscape.jpg``` inside the ```images``` folder then you would just do something like

```md
---
image: abstract-landscape.jpg
---
<!--- This is where your other content would go -->
```

To include an image inline you use standard markdown syntax and reference the file using the full path i.e. ```images/abstract-landscape.jpg``` would be:

```md
---
<!-- This is where your metadata is -->
---
This is a cool image:

![abstract landscape](images/abstract-landscape.jpg)
```

