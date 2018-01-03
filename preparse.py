"""Panelcode preparse methods for detecting types of panelcode for parsing and
   cleaning, joining, segmenting or labeling them before parsing.
"""

import re
import parser
import render
import highlight

def parse_fenced_to_html(data_list, mode='replace', panel='open', sizers=True, colorize=True):
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
    if colorize==True:
        highlight_style = "<style>\n" + highlight.style_css() + "\n</style>"
        result_list.append(highlight_style)
    if sizers==True and len(data_fence_list)>1:
        jquery_cdn = """<script
  src="https://code.jquery.com/jquery-2.2.4.min.js"
  integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44="
  crossorigin="anonymous"></script>
 """
        size_script ="""<script type="text/javascript">
  $(document).ready(function(){
    // On load
    $('.gallery-size').change(function(){
      $(this).closest('div.gallery')
      .removeClass('default small thumb mini micro micro2')
        .addClass( $(this).val() );
    })
})
</script>
"""
        size_selector_global = """Resize All: <select class="all-size">
  <option value=""></option>
  <option value="default">default</option>
  <option value="small">small</option>
  <option value="thumb">thumb</option>
  <option value="mini">mini</option>
  <option value="micro">micro</option>
  <option value="micro2">micro2</option>
</select>
<div style="clear: both;"></div>
"""
        result_list.extend([jquery_cdn, size_script, size_selector_global])
        size_selector = """<select class="gallery-size">
  <option value="">--size--</option>
  <option value="default">default</option>
  <option value="small">small</option>
  <option value="thumb">thumb</option>
  <option value="mini">mini</option>
  <option value="micro">micro</option>
  <option value="micro2">micro2</option>
</select>
"""
    for idx, graph in enumerate(data_fence_list):
        graph = graph.replace('\n\n', '\n')
        if idx % 5 == 0:
            result_list.append(graph)
        if idx % 5 == 3:
            result = ''
            if colorize:
                graph_out = '\n'+ str(highlight.style_string(graph)) +'\n'
            else:
                graph_out = '\n```panelcode' + graph + '\n```\n' # data_fence_list[idx-2]
            try:
                graph_clean = ''.join(decomment(graph.split('\n'), '#'))
                pcode_obj = parser.parse(graph_clean, parser.root)
                html_lines = render.pobj_to_html5_ccs3_grid(pcode_obj)
                control_str = ''
                if (sizers == True or 'control' in graph):
                    if 'nocontrol' not in graph:
                        control_str = '<div style="clear: both;"></div><bdo dir="ltr"><details ' + panel + '><summary>panelcode</summary>\n' + size_selector + graph_out + '\n</details></bdo>\n'
                if mode == 'pre':
                    html_lines.insert(-1, control_str)
                    result += ''.join(html_lines)
                elif mode == 'post':
                    result += '\n' + graph_out + '\n'
                    result += ''.join(html_lines)
                elif mode == 'replace':
                    result = ''.join(html_lines)
            except parser.pp.ParseException as err:
                result = graph_out
            result_list.append(result)
    result_list.append('\n<p style="font-size:x-small"><em>panelcode: fence pre-processor</em></p>\n')
    return result_list


def decomment(item, delim):
    """Remove whole line and end-of-line comments marked with a delimiter."""
    for itemline in item:
        seg = itemline.split(delim, 1)[0].strip()
        if seg != '':
            yield seg
        else:
            # align line numbers in oarse error checking with original
            yield ''
