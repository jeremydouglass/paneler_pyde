import os

# 'sketchPath()+'/input/index.html'

def load_str(filename='panelcode.txt', path=''):
    if path == '':
        path = sketchPath() + '/data/input/'
    strings = loadStrings(path + filename)
    return strings

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
