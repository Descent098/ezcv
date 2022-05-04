# ezcv + flask

Hi, welcome to [ezcv](https://ezcv.readthedocs.io/en/latest/) + [flask](https://flask.palletsprojects.com/en/2.1.x/). This is meant to be the most basic setup for integrating ezcv as a site generator with flask as an HTTP server. 

There are a few things to keep in mind while using this project:

1. By default the system is setup to generate the site content to a folder called `/site` on **each run**. It **does not regenerate on changes** to the source content. You will need to re-run `routes.py` each time to regenerate the site. If you want this live-reloading feature see the [extras](#extras) at the bottom.
2. This system **is not production ready**. There has been no security hardening done as this is meant to be a starting point. You can look at [this guide](https://flask.palletsprojects.com/en/2.1.x/tutorial/deploy/) which will help start the process, but you will need to do some research to determine best practices yourself.

## Getting started

Everything you need to get up and running.

### Requirements

To get started you will need python 3.8+ and pip for that python version. Since this version has a built in [flask](https://flask.palletsprojects.com/en/2.1.x/) server you will also need to install flask. There are two ways to do all this:

1. Install the dependencies via the requirements file: `pip install -r requirements.txt`
2. Or install the dependencies manually using `pip install ezcv` and `pip install flask`

### Running the project

Once you have flask and ezcv installed you can run the project by simply running `python routes.py` then head to a browser and go to [http://localhost:5000](http://localhost:5000/)

### Additional documentation

There is additional documentation available that will be helpful to you:

- [List of themes for ezcv](https://ezcv.readthedocs.io/en/latest/included-themes/)
- [ezcv usage guide](https://ezcv.readthedocs.io/en/latest/usage/)
- [api documentation for ezcv](https://kieranwood.ca/ezcv/)


## Extras

### Integrating live-reload

If you want your site to regenerate every time you change the content for the site you can follow the steps below:

1. You will need to install [livereload](https://pypi.org/project/livereload/), this can be done using `pip install livereload`
2. Add `Server` class to the imports at the top of the file 
```python 
from livereload import Server # Used to livereload pages in browser
```
3. Turn on `DEBUG` and `TEMPLATES_AUTO_RELOAD` in the `Flask` app config (should be lines 9 and 10 in `routes.py`)
4. Replace the last 3 lines (everything in the `if __name__ == '__main__` conditional) to: 
```python
if __name__ == '__main__':
    PORT = 5000 # The port to run the app on
    generate_site(output_folder=output_dir) # Generate the site initially
    open_in_browser() # Open the browser
    server = Server(app) # Initialize the livereload server
    server.watch('images/*', lambda: generate_site(output_folder=output_dir)) # Watch for changes in the images folder
    server.watch('*.yml', lambda: generate_site(output_folder=output_dir)) # Watch for changes in the yml files
    server.watch('content/*/*.md', lambda: generate_site(output_folder=output_dir)) # watch for changes in the markdown files
    server.serve(port=PORT) # Start the server
```