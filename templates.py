"""Template wrapping functions for paneler, using Jinja2."""

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

def load(filename, path=''):
    """Load template for rendering -- with sketch defaults."""
    if path == '':
        path = sketchPath() + '/data/templates/'
    env = Environment(loader=FileSystemLoader(path))
    tmpl = env.get_template(filename)
    return tmpl

def render(tmpl, code, title='Panelcode viewer'):
    """Render code in template as content string"""
    return tmpl.render(panelcode=code, pagetitle=title)
