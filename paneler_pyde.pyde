import parser
import render
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
    
    ## parse panelcode to object
    pcode_obj = parser.parse(pcode_str, parser.root)
    print(pcode_obj)

    ## render panelcode object to html
    html_str = "\n".join(render.pobj_to_html5_ccs3_grid(pcode_obj))
    print(html_str)

    ## wrap html in page template
    html_page_str = tmpl.render(panelcode=html_str)

    ## save html page to file
    utils.save_page(html_page_str, result_filename)

    ## preview html page file in web browser
    utils.preview(result_filename)

def keyPressed():
    if key == 't':
        tests.run() # run all tests
