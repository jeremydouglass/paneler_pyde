"""Panelcode preparse methods for detecting types of panelcode for parsing and
   cleaning, joining, segmenting or labeling them before parsing.
"""

import re
import parser
import render
import highlight
import templates

JQUERY_SCRIPT_CDN = """<script
  src="https://code.jquery.com/jquery-2.2.4.min.js"
  integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44="
  crossorigin="anonymous"></script>
 """
SIZER_SCRIPT = """<script type="text/javascript">
  $(document).ready(function(){
    // On load
    $('.gallery-size').change(function(){
      $(this).closest('div.gallery')
      .removeClass('default small thumb mini micro micro2')
        .addClass( $(this).val() );
    })
    $('.all-size').change(function(){
      $('div.gallery')
      .removeClass('default small thumb mini micro micro2')
        .addClass( $(this).val() );
    })
})
</script>
"""


def console_html(size_list='', content='', summary='panelcode',
                 css_class='gallery-size', reveal='open'):
    """Render a console area for a gallery. Includes:
    1. a code view (syntax highlighting)
    2. resizing of gallery layouts
    3. show / hide console contents
    """
    if not size_list:
        size_list = ['', 'default', 'small', 'thumb', 'mini', 'micro2']
    template = 'console.html'
    tmpl = templates.load2(filename=template)
    html_str = tmpl.render(summary=summary, option_list=size_list,
                           css_class=css_class, content=content,
                           reveal=reveal).encode('utf-8')
    return html_str


def parse_fenced_to_html(data_list, mode='replace', reveal='',
                         consoles=True, colorize=True):
    """Parse panelcode only within markdown fenced code blocks.
    Split a list of lines on fence open and close markers,
    attempt to render code block contents as panelcode or pass through,
    return a list of unchanged contents and possibly changed blocks.

    Results can replace the code block ('replace') or come
    before or after it ('pre' / 'post')
    """
    result_list = []
    fences = re.compile(  # see mistune
        r' *(`{3,}|~{3,})( *\S+ *)?\n'  # ```lang (removed)
        r'([\s\S]+?\s*)'
        r'(\1)(?: *\n+|$)'  # ```
        )
    data_fence_list = fences.split('\n'.join(data_list))
    # General approach does not work -- Markdown processors strip style tags.
    # Instead the css class styling information needs to already be available
    #  via external stylsheets.
    #
    # if colorize==True:
    #     highlight_style = "<style>\n" + highlight.style_css() + "\n</style>"
    #     result_list.append(highlight_style)
    if consoles and len(data_fence_list) > 1:
        result_list.extend([JQUERY_SCRIPT_CDN, SIZER_SCRIPT])
    for idx, graph in enumerate(data_fence_list):
        graph = graph.replace('\n\n', '\n')
        if idx % 5 == 0:
            result_list.append(graph)
        if idx % 5 == 3:
            result = ''
            if colorize:
                graph_out = '\n' + str(highlight.style_string(graph)) + '\n'
            else:
                graph_out = '\n```panelcode' + graph + '\n```\n'
                # ... or use data_fence_list[idx-2] -- catches ~~~ etc.
            try:
                delims = ['#', '//']
                graph_clean = ''.join(decomment(graph.split('\n'), delims))
                pcode_obj = parser.parse(graph_clean, parser.root)
                html_lines = render.pobj_to_html5_ccs3_grid(pcode_obj)
                console_str = ''
                if consoles or 'console' in graph:
                    if 'noconsole' not in graph:
                        console_str = console_html(content=graph_out,
                                                   css_class='gallery-size',
                                                   reveal=reveal)
                if mode == 'pre':
                    html_lines.insert(-1, console_str)
                    result += ''.join(html_lines)
                elif mode == 'post':
                    result += '\n' + graph_out + '\n'
                    result += ''.join(html_lines)
                elif mode == 'replace':
                    result = ''.join(html_lines)
            except parser.pp.ParseException:
                result = graph_out
            result_list.append(result)
    if consoles and len(data_fence_list) > 1:
        console_str = console_html(content='',
                                   summary='Resize all galleries: ',
                                   css_class='all-size',
                                   reveal=reveal)
        result_list.append(console_str)
    result_list.append('\n<p style="font-size:x-small">'
                       + '<em>panelcode: fence pre-processor</em></p>\n')
    return result_list


def decomment(item, delims):
    """Remove whole line and end-of-line comments marked with delimiters.
    Checks for a delimiter '#' or a list of delimiters ['#, '//', ...].
    """
    for itemline in item:
        if isinstance(delims, basestring):
            seg = itemline.split(delims, 1)[0].strip()
        else:
            for delim in delims:
                seg = itemline.split(delim, 1)[0].strip()
        if seg != '':
            yield seg
        else:
            # align line numbers in oarse error checking with original
            yield ''
