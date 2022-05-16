from flask import render_template, Flask
from ezcv.core import generate_site
from jinja2.exceptions import TemplateNotFound

template_dir = 'site' # The folder you want to export your site to

app = Flask(__name__, static_url_path='', static_folder=template_dir,  template_folder=template_dir)

# Turn these on when you're developing
# app.config["DEBUG"] = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():
    """display the homepage"""
    return render_template("index.html")

@app.route('/<path>')
def static_file(path:str):
    """Takes in a path and tries to return the template file with that title
    So if a user types in /test then it will try to find a template called test.html

    Parameters
    ----------
    path : str
        The path the user puts in the browser
    """
    try:
        return render_template(f"{path}.html")
    except TemplateNotFound:
        try: # Try to look for a 404 page
            return render_template("404.html")
        except TemplateNotFound: # If no 404 page exists, return a generic 404 page
            return """<div style='font-size: XXX-large;text-align: center;'>
            <h1>404 page not found</h1>
            </br>
            <button onclick='history.go(-1)'> Click to go back</button>
            </div>"""

if __name__ == '__main__':
    generate_site(output_folder=template_dir)
    app.run(host='localhost', port=5000)