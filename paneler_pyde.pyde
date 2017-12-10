"""A panelcode parser and renderer in a Processing.py (Python Mode) sketch."""

from __future__ import print_function
import datetime
import parser
import render
import templates
import tests
import utils

# pylint: disable=bad-whitespace
# pylint: disable=invalid-name

## File configuration

cfg = { 'data' : { 'path': '/data/input/'    , 'file' : 'data.panelcode.txt' },
        'tmpl' : { 'path': '/data/templates' , 'file' : 'gallery_css3.html'  },
        'save' : { 'path': '/data/output/'   , 'file' : 'index.html' }
        }

## process_status handle the main parsing and rendering state
## This enables the UI to update on the next frame after it
## is invoced rather than freezing (when not threaded). Also
## guards against multiple calls.

P_CLEAR = 0
P_PREP = 1
P_RUN  = 2
P_WAIT = 3
process_status = P_CLEAR

## Has this config been previewed in the browser? If so,
## view = True so that re-running doesn't generate endless
## browser tabs.

view = False

def setup():
    """Set up sketch."""
    size(200,250)
    stroke(192)
    strokeWeight(1)
    textAlign(CENTER,CENTER)
    textSize(16)
    
    b_title = Label("PANELER", 10, -1, width-20, 31)
    b_title.bgcolor = color(207, 236, 207)
    b_data = Button("DATA",     10,  40, width-20, 40, cfg_key='data', call='selectInput', callback='fileSelectedData')
    b_temp = Button("TEMPLATE", 10,  90, width-20, 40, cfg_key='tmpl', call='selectInput', callback='fileSelectedTemplate')
    b_out  = Button("OUTPUT",   10, 140, width-20, 40, cfg_key='save', call='selectInput', callback='fileSelectedSave')
    b_run  = Button("RUN",      10, 190, width-20, 40, cfg_key='',     call='',            callback='runProcess')
    b_run.bgcolor_click = color(255, 64, 64)
    global button_list
    button_list = [b_title, b_data, b_temp, b_out, b_run]

def draw():
    """Visual UI."""
    for b in button_list:
        b.over(mouseX, mouseY)
    background(224,238,253)
    fill(207,221,236)
    rect(10,10,width-20, 20)
    fill(0)
    text("PANELER", width/2, 18)
    for b in button_list:
        b.display()

    global process_status
    if process_status == P_PREP:
        process_status = P_RUN
    if process_status == P_RUN:
        process()
        process_status == P_WAIT
    
def process():
    """Load data, insert into html template, preview result."""

    global process_status
    if process_status == P_WAIT:
        return
    else:
        process_status = P_WAIT;

    print('Rendering:  {0}\n template:  {1}\ninto file:  {2}'.format(cfg['data']['file'], cfg['tmpl']['file'], cfg['save']['file']))

    ## load template and data
    tmpl = templates.load(cfg['tmpl']['path'] , cfg['tmpl']['file'])
    data = utils.load_str(cfg['data']['file'])
    ## merge into one string
    pcode_str = '\n'.join(data)
    ## remove bottom notes
    pcode_str = pcode_str.split("---")[0]

    ## preview (w/ flatten unicode)
    # print(pcode_str..encode('ascii', 'replace') + '\n')

    ## split on delimiter
    pcode_list = pcode_str.split('@')

    ## parse panelcode to object
    pcode_objs = []
    for pcode_str in pcode_list:
        pcode_obj = parser.parse(pcode_str, parser.root)
        pcode_objs.append(pcode_obj)

    ## render panelcode object to html
    html_results = []
    for pcode_obj in pcode_objs:
        html_lines = render.pobj_to_html5_ccs3_grid(pcode_obj)
        html_str = '\n'.join(html_lines)
        html_results.append(html_str)

    ## wrap html in page template
    html_page_str = tmpl.render(panelcode=html_results, pagetitle=cfg['data']['file'], datetime=datetime.datetime.now())

    ## preview html page contents
    # print(html_page_str)

    ## save html page to file
    utils.save_page(html_page_str, cfg['save']['file'])

    ## launch preview in browser if not already opened
    global view
    if view==False:
        ## preview html page file in web browser
        print('Launch preview: ' + cfg['save']['file'])
        utils.preview(cfg['save']['file'])
        view=True
    
    process_status = P_CLEAR
    
    global button_list
    for b in button_list:
        if b.label == 'RUN':
            b.click_time = 120


########################################
## event handling
########################################

def keyPressed():
    """Key events: respond to key input events each frame."""
    global view
    if key == ' ':
        print('Process and render data.')
        process()
        if view==False:
            ## preview html page file in web browser
            utils.preview(cfg['save']['path'] + cfg['save']['file'])
            view=True
    if key == 'd':
        print('Select a data file.')
        selectInput("Select a data file:", "fileSelected")
    if key == 't':
        print('Select a template.')
        selectInput("Select a template:", "templateSelected")
        # path = os.getcwd()
        # fp=open(path,'r+')
        # selectInput("Select a template:", "templateSelected", fp)
    if key == 'p':
        print('Launch preview: ' + cfg['save']['file'])
        utils.preview(cfg['save']['file'])
        view=True
    if key == 'q':
        exit(); return
    ## Copy data input name to html output name
    if key == 's':
        cfg['save']['file'] = cfg['data']['file'] + '.html'
    if key == '?':
        print('Run all tests.')
        tests.run() # run all tests

def mousePressed():
    """Mouse events: respond to mouse input events each frame."""
    for b in button_list:
        b.click(mouseX, mouseY)


########################################
## classes
########################################

class Label(object):
    """A simple label."""
    def __init__(self, label, x, y, w, h):
        self.label = label
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bgcolor = color(207,221,236)
        self.textcolor = color(0)

    def display(self):
        with pushStyle():
            stroke(64)
            strokeWeight(1)
            fill(self.bgcolor)
            rect(self.x, self.y, self.w, self.h)
            fill(self.textcolor)
            textAlign(CENTER, CENTER)
            text(self.label, self.x + (self.w / 2), self.y + (self.h / 2))

    def click(self, px, py):
        return False

    def over(self, px, py):
        return False

class Button(object):
    """A simple button."""
    
    def __init__(self, label, x, y, w, h, click_duration=30, cfg_key='', callback='', call=''):
        self.label = label
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.click_duration = click_duration
        self.callback = callback
        self.cfg_key = cfg_key
        self.call = call

        self.is_over = False
        self.click_time = 0
        
        self.strokecolor = color(64)
        self.strokeweight = 1
        self.bgcolor = color(207,221,236)
        self.bgcolor_over = color(207,207,255)
        self.bgcolor_click = color(255,221,207)
        self.labelcolor = color(0)
        self.labelsize = 10
        self.textcolor = color(0)
        self.textsize = 16
        
    def display(self):
        if self.click_time > 0:
            self.click_time -= 1
        with pushStyle():
            stroke(64)
            strokeWeight(1)
            if(self.click_time != 0):
                fill(self.bgcolor_click)
            elif(self.is_over):
                fill(self.bgcolor_over)
            else:
                fill(self.bgcolor)
            rect(self.x, self.y, self.w, self.h)
            fill(0)
            # textAlign(CENTER, CENTER)
            if self.cfg_key:
                text(self.label, self.x + (self.w / 2), self.y + (self.h / 2) - 5)
                textSize(10)
                fname = cfg[self.cfg_key]['file']
                text(fname, self.x + (self.w / 2), self.y + (self.h / 2) + 10)
            else:
                text(self.label, self.x + (self.w / 2), self.y + (self.h / 2))

    def click(self, px, py):
        """Perform click actions if the point over the object."""
        if self.collide(px, py):
            if self.click_time == 0:
                ## start timer for click display
                self.click_time = self.click_duration
                if self.call=='selectInput':
                    print('Select a data file:')
                    selectInput("Select a data file:", self.callback)
                elif self.call=='selectFolder':
                    pass
                else:
                    eval(self.callback+'()')
        return self.click_time

    def over(self, px, py):
        """Perform hover actions if the point over the object."""
        if self.collide(px, py):
            if self.click_time == 0:
                self.is_over = True
        else:
            if self.click_time == 0:
                self.is_over = False
        return self.is_over

    def collide(self, px, py):
        """Point-rectangle collision detection."""
        return px >= self.x and px <= self.x + self.w and py >= self.y and py <= self.y + self.h


########################################
## File section callbacks
########################################
## Called as Processing input callbacks,
## so they must:
## 
## 1. be at the top level of the sketch
## 2. take only 'selection' as an arg
########################################

def fileSelectedData(selection):
    """Updates data file cfguration from a user file dialog."""
    fileSelected(selection, 'data')

def fileSelectedTemplate(selection):
    """Updates template file cfguration from a user file dialog."""
    fileSelected(selection, 'tmpl')

def fileSelectedSave(selection):
    """Updates save file cfguration from a user file dialog."""
    fileSelected(selection, 'save')

def fileSelected(selection, cfg_key):
    """Load user-selected file into a config key."""
    if selection == None:
        print("Window was closed or the user hit cancel.")
    else:
        print("User selected " + selection.getAbsolutePath())
        newpath = utils.os.path.dirname(selection.getAbsolutePath())
        newfile = utils.os.path.basename(selection.getAbsolutePath())
        cfg[cfg_key] = { 'path' : newpath , 'file' : newfile }
        ## reset view due to new file config
        global view; view = False

def runProcess():
    """Run process."""
    process()
