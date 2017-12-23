"""Panelcode preparse methods for detecting types of panelcode for parsing and
   cleaning, joining, segmenting or labeling them before parsing.
"""

import re
import parser
import render


def parse_fenced_to_html(data_list, mode='replace'):
    """Parse panelcode only within markdown fenced code blocks.
    Split a list of lines on fence open and close markers,
    attempt to render code block contents as panelcode or pass through,
    return a list of unchanged contents and possibly changed blocks.

    Results can replace the code block ('replace') or come
    before or after it ('pre' / 'post')
    """
    result_list = []
    result_list.append('<p><em>panelcode: fence pre-processor</em></p>\n')
    fences = re.compile(  # see mistune
        r' *(`{3,}|~{3,})( *\S+ *)?\n'  # ```lang (removed)
        r'([\s\S]+?\s*)'
        r'(\1)(?: *\n+|$)'  # ```
        )
    data_fence_list = fences.split('\n'.join(data_list))
    for idx, graph in enumerate(data_fence_list):
        graph = graph.replace('\n\n', '\n')
        if idx % 5 == 0:
            result_list.append(graph)
        if idx % 5 == 3:
            result = ''
            try:
                graph_clean = ''.join(decomment(graph.split('\n'), '#'))
                pcode_obj = parser.parse(graph_clean, parser.root)
                html_lines = render.pobj_to_html5_ccs3_grid(pcode_obj)
                if mode == 'pre':
                    result += ''.join(html_lines)
                    result += '\n' + data_fence_list[idx-2] + graph + '\n```\n'
                elif mode == 'post':
                    result += '\n' + data_fence_list[idx-2] + graph + '\n```\n'
                    result += ''.join(html_lines)
                elif mode == 'replace':
                    result = ''.join(html_lines)
            except parser.pp.ParseException as err:
                result = graph
            result_list.append(result)
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
