#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Template wrapping functions for paneler, using Jinja2."""

import os
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader


def load(abspath='', filename='template.html'):
    """Load template for rendering -- with sketch defaults.
       Jinja2 is designed to work only within a relative
       list established by its Environment.
    """
    pathlist = []
    if abspath:
        pathlist.append(abspath)
    # Processing: load sketchPath() if in Processing PDE
    try:  
        pathlist.append(sketchPath() + '/data/templates/')
        pathlist.append(sketchPath() + '/data/')
        pathlist.append(sketchPath())
    except NameError:
        pass
    # Try current working directory
    pathlist.append(os.getcwd() + '/templates/')
    pathlist.append(os.getcwd() + '/data/templates/')
    pathlist.append(os.getcwd() + '/data/')
    pathlist.append(os.getcwd())
    # Try relative to script
    script_path = os.path.dirname(os.path.realpath(__file__))
    pathlist.append(script_path + '/templates/')
    pathlist.append(script_path + '/../data/templates/')
    pathlist.append(script_path + '/../data/')
    pathlist.append(script_path + '/data/templates/')
    pathlist.append(script_path + '/data/')
    pathlist.append(script_path)
    env = Environment(loader=FileSystemLoader(pathlist))
    tmpl = env.get_template(filename)
    return tmpl
