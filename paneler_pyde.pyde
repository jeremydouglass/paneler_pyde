"""A panelcode parser and renderer in a Processing.py (Python Mode) sketch."""

from __future__ import print_function
import datetime
import parser
import render
import templates
import tests
import utils
from batch import BatchProcess
from ui import TextList, Button

# pylint: disable=invalid-name

## Batch Processor

bp = None

## UI components list

ui_list = []

## File configuration

# pylint: disable=bad-whitespace
cfg = { 'data' : { 'path': '/data/input/'    , 'file' : 'data.panelcode.txt' },
        'tmpl' : { 'path': '/data/templates' , 'file' : 'gallery_css3.html'  },
        'save' : { 'path': '/data/output/'   , 'file' : 'index.html' }
      }
# pylint: enable=bad-whitespace

## Has this config been previewed in the browser? If so,
## view = True so that re-running doesn't generate endless
## browser tabs.

view = False

def setup():
    """Set up sketch."""
    size(300, 350)
    frameRate(30)

    reset()

def reset():
    """(Re)Build batch processor and UI."""
    ## new batch processor
    global bp
    bp = BatchProcess(processItem)
    bp.source_trees.add(sketchPath()+'/data')

    ## user interface
    global ui_list

    ## label
    b_title = Button("PANELER", 0, -4, width, 36)
    b_title.textsize = 18
    b_title.bgcolor = color(207, 236, 207)
    b_title.no_change()

    ## text list elements with attached status methods for live text

    tl_sources = TextList(bp.sources, 0, 32, width, 64, title='Sources')
    tl_template = TextList(bp.get_template, width/3, 120, 2*width/3, 24, title='')
    tl_tasks = TextList(bp.task_names, 0, 144, width, 96, title='Tasks')
    tl_errors = TextList(bp.get_errors, 0, 240, width, height-240, title='Errors')

        ## Buttons
    ## with attached call Processing dialog types + callbacks

    b_add_file = Button("+file", 0, 96, width/4, 24,
                        calltype='selectInput',
                        callback='bpAddFileSelected')
    b_add_fold = Button("+folder", width/4, 96, width/4, 24,
                        calltype='selectFolder',
                        callback='bpAddFolderSelected')
    b_add_tree = Button("+tree", 2*width/4, 96, width/4, 24,
                        calltype='selectFolder',
                        callback='bpAddTreeSelected')
    b_clear = Button("clear", 3*width/4, 96, width/4, 24,
                     calltype='', callback=bp.clear)

    ## Template button
    b_temp = Button("template", 0, 120, width/3, 24,
                    calltype='', callback='')
    b_temp.bgcolor = color(220, 220, 220)
    b_temp.no_change()

    ## Reset button
    b_reset = Button("RESET", 5*width/6-8, 5, width/6, 20,
                     calltype='', callback=reset)
    b_reset.textsize = 10
    if frameCount > 0: ## indicate a successful reset
        b_reset.click_time = 30

    ## Run button
    ## populates the process queue, which is consumed
    ## each frame by draw when non-empty.
    b_run = Button("RUN", 2*width/3, height-32, width/3, 32, calltype='', callback=bp.queue)
    b_run.bgcolor_click = color(255, 64, 64)

    ## UI components list
    ## build list for display
    ui_list = [b_title, tl_sources, b_add_file, b_add_fold, b_add_tree,
               tl_template, b_clear, b_temp, tl_tasks, tl_errors, b_run, b_reset]

    ## Copy template styles dir to output if it doesn't exist
    utils.copy_styles()

def draw():
    """Visual UI."""
    background(192)
    for element in ui_list:
        try:
            element.over(mouseX, mouseY)
        except AttributeError:
            pass
        try:
            element.display()
        except AttributeError:
            pass

    ## process the next item if available
    bp.next() # template=bp.get_template()

def processItem(item, **kwargs):
    """Per-item process controlled by batch job.
       Load data, insert into html template, preview result."""

    global cfg

    print('processing: ' + item)
    for key, val in kwargs.items():
        print('  kwarg: ', key, val)

    ## update source and destination
    cfg['data']['path'] = utils.os.path.dirname(item)
    cfg['data']['file'] = utils.os.path.basename(item)
    ## ...leave standard save path in place
    cfg['save']['file'] = cfg['data']['file'] + '.html'
    print('Rendering:  {0}\n template:  {1}\ninto file: {2}'.format(
        cfg['data']['file'], cfg['tmpl']['file'], cfg['save']['file']))

    ## load template
    template = cfg['tmpl']['file']
    print(template)
    tmpl = templates.load(filename=template)

    ## load data
    datapath = cfg['data']['path'] + '/' + cfg['data']['file']
    print(datapath)
    data = loadStrings(datapath)

    ## strip comment lines
    dataclean = utils.decomment(data, '#')
    data = [dline for dline in dataclean]

    ## merge into one string
    pcode_str = '\n'.join(data)

    ## remove bottom notes
    if '\n---' in pcode_str:
        pcode_str = pcode_str.split('\n---')[0]

    ## preview (w/ flatten unicode)
    # print(pcode_str..encode('ascii', 'replace') + '\n')

    ## embedded code blocks:
    ## split on markdown-style codeblock begin-end line delimiters
    ## and take every second item
    if '```' in pcode_str:
        pcode_list = (pcode_str+'\n').split('\n```')[1::2]
    else:
        pcode_list = [pcode_str]

    ## gallery splitting
    if '@' in pcode_str:
        pcode_list = [gallery for pcode_block in pcode_list for gallery in pcode_block.split('@')]

    ## parse panelcode to object
    pcode_objs = []
    for pcode_str in pcode_list:
        try:
            pcode_obj = parser.parse(pcode_str, parser.root)
            pcode_objs.append(pcode_obj)
        except parser.pp.ParseException as err:
            bp.errors.append((item, err))
    ## render panelcode object to html
    html_results = []
    for pcode_obj in pcode_objs:
        html_lines = render.pobj_to_html5_ccs3_grid(pcode_obj)
        html_str = '\n'.join(html_lines)
        html_results.append(html_str)

    ## wrap html in page template
    html_page_str = tmpl.render(panelcode=html_results, pagetitle=cfg['data']['file'],
                                datetime=datetime.datetime.now())

    ## preview html page contents
    # print(html_page_str)

    ## save html page to file
    ## ...leave standard save path in place
    utils.save_page(html_page_str, cfg['save']['file'])

    ## launch preview in browser if not already opened
    global view
    if view is False:
        ## preview html page file in web browser
        print('Launch preview: ' + cfg['save']['file'])
        utils.preview(cfg['save']['file'])
        view = True

    global ui_list
    for element in ui_list:
        try:
            if element.title == 'RUN':
                element.click_time = 120
        except AttributeError:
            pass


########################################
## event handling
########################################

def keyPressed():
    """Key events: respond to key input events each frame."""
    global view
    if key == ' ':
        print('Process and render data.')
        bp.next() # template=bp.get_template()
        if view is False:
            ## preview html page file in web browser
            utils.preview(cfg['save']['path'] + cfg['save']['file'])
            view = True
    if key == 'd':
        print('Select a data file.')
        selectInput("Select a data file:", "fileSelected")
    if key == 'e':
        print('\n')
        for error in bp.errors:
            print('\n', error)
    if key == 't':
        print('Select a template.')
        selectInput("Select a template:", "templateSelected")
        # path = os.getcwd()
        # fp=open(path,'r+')
        # selectInput("Select a template:", "templateSelected", fp)
    if key == 'p':
        print('Launch preview: ' + cfg['save']['file'])
        utils.preview(cfg['save']['file'])
        view = True
    if key == 'q':
        exit() # sets exit flag, but does not terminate loop
        return
    ## Copy data input name to html output name
    if key == 's':
        cfg['save']['file'] = cfg['data']['file'] + '.html'
    if key == '?':
        print('Run all tests.')
        tests.run() # run all tests

def mousePressed():
    """Mouse events: respond to mouse input events each frame."""
    for b in ui_list:
        try:
            b.click(mouseX, mouseY)
        except AttributeError:
            pass


########################################
## File section callbacks
########################################
## Called as Processing input callbacks,
## so they must:
##
## 1. be at the top level of the sketch
## 2. take only 'selection' as an arg
##
## These are not implemented as lambdas
## in order to maintain compatability
## with the function-name-as-string call
## method of the Processing(Java) API
## in selectInput() and selectFolder().
########################################

def bpAddFileSelected(selection):
    """Redirect results of user file dialog."""
    bp.source_files.add(selection.getAbsolutePath())

def bpAddFolderSelected(selection):
    """Redirect results of user file dialog."""
    bp.source_folders.add(selection.getAbsolutePath())

def bpAddTreeSelected(selection):
    """Redirect results of user file dialog."""
    bp.source_trees.add(selection.getAbsolutePath())

def bpAddTreeFilesSelected(selection):
    """Redirect results of user file dialog."""
    bp.add_tree_files(selection.getAbsolutePath())
