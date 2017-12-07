import templates
import tests
import utils

def setup():
    process(pcode_filename    = 'data.panelcode.txt',
            template_filename = 'gallery_css3.html',
            result_filename   = 'index.html')
    print('Done.')
    exit()

def draw():
    pass

def process(pcode_filename, template_filename, result_filename):
    """load data, insert into html template, preview result"""
    
    ## load jinja2 template
    tmpl = templates.load(template_filename)

    ## load panelcode input file and merge into one string
    pcode_str = utils.load_str(pcode_filename)
    pcode_str = '\n'.join(pcode_str)

    ## render input through template into output html
    html_str = tmpl.render(panelcode=pcode_str)

    ## save output to html page
    utils.save_page(html_str, result_filename)

    ## preview page in web browser
    utils.preview(result_filename)

def keyPressed():
    if key == 't':
        tests.run() # run all tests
