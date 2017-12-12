"""Utility functions for paneler.
Used to load data, save rendered output, and preview results.
Also contains wrappers for picking and status functions.
"""

from __future__ import print_function
import os
import pickle
import shutil

def copy_styles():
    src = sketchPath() + '/styles'
    dest = sketchPath() + '/data/output/styles'
    try:
        shutil.copytree(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        # print('Error: %s' % e)
        pass
    # eg. source or destination doesn't exist
    except IOError as e:
        # print('Error: %s' % e.strerror)
        pass
    except OSError as e:
        # print('Error: %s' % e.strerror)
        pass
        
def decomment(item, delim):
    for itemline in item:
        seg = itemline.split(delim, 1)[0].strip()
        if seg != '':
            yield seg
        else:
            ## align line numbers in oarse error checking with original
            yield ''

def exists(filename, path=''):
    """Load panelcode file as string."""
    if path == '':
        path = sketchPath() + '/data/output/'
    return os.path.exists(path+filename)

def load_str(filename='panelcode.txt', path=''):
    """Load panelcode file as string."""
    if path == '':
        path = sketchPath() + '/data/input/'
    strings = loadStrings(path + filename)
    return strings

def pickle_dump(obj, filename, path=''):
    """Save (serialize) panelcode object to a pickle file."""
    if path == '':
        path = sketchPath() + '/data/output/'
    try:
        with open(path+filename, 'wb') as handle:
            pickle.dump(obj, handle)
    except EnvironmentError as err:
        print(filename + ' not saved.')
        print(err)
        raise

def pickle_load(filename, path=''):
    """Load pickle file to panelcode object."""
    if path == '':
        path = sketchPath() + '/data/output/'
    try:
        with open(path+filename, 'rb') as handle:
            return pickle.load(handle)
    except EnvironmentError as err:
        print(filename + ' not loaded.')
        print(err)
        raise

def pickle_remove(filename, path=''):
    """Remove pickle file from disk."""
    if path == '':
        path = sketchPath() + '/data/output/'
    try:
        os.remove(path+filename)
    except OSError as err:
        print(filename + ' not removed.')
        print(err)

def preview(filename='index.html', path=''):
    """Open file preview in default web browser (on macOS)."""
    if path == '':
        path = sketchPath() + '/data/output/'
    os.system('open '+ path + filename)

def save_page(file_str, filename='index.html', path=''):
    """Save page to output directory."""
    if path == '':
        path = sketchPath() + '/data/output/'
    filepath = path + filename
    saveStrings(filepath, [file_str])

def status():
    """Print working status to console."""
    print(sketchPath())
