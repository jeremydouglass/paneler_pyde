from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from jinja2 import Template

spath = sketchPath()

def load(filename, path = ''):
    if path=='':
        path = sketchPath() + '/data/templates/'
    env = Environment(loader=FileSystemLoader(path))
    tmpl = env.get_template(filename)
    return tmpl

def render(tmpl, code, title='Panelcode viewer'):
    return tmpl.render(panelcode = code, pagetitle = title)
