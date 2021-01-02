# Quick start

...

## Installation

...

## No-code usage

...

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
| **theme** | The name of the theme to use | the name of any included theme i.e. freelancer |

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
theme: freelancer # Which of the included themes to use
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

...
