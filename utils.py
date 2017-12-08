from __future__ import print_function
import os
import pickle

# 'sketchPath()+'/input/index.html'
def exists(filename, path=''):
    if path == '':
        path = sketchPath() + '/data/output/'
    return os.path.exists(path+filename)

def load_str(filename='panelcode.txt', path=''):
    if path == '':
        path = sketchPath() + '/data/input/'
    strings = loadStrings(path + filename)
    return strings

def pickle_dump(obj, filename, path=''):
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
    if path == '':
        path = sketchPath() + '/data/output/'
    try:
        os.remove(path+filename)
    except OSError as err:
        print(filename + ' not removed.')
        print(err)

def preview(filename='index.html', path=''):
    if path == '':
        path = sketchPath() + '/data/output/'
    os.system('open '+ path + filename)

def save_page(file_str, filename='index.html', path=''):
    if path == '':
        path = sketchPath() + '/data/output/'
    filepath = path + filename
    saveStrings(filepath, [file_str])
    pass
    
def status():
    println(sketchPath())
