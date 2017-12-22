#!/usr/bin/env python
"""A panelcode parser and renderer."""

import argparse
import os
import sys

import preparse
import parser
import render


def decode(args):
    """Read in panelcode or embedded document stream, emit html rendering."""

    data_list = []
    for line in sys.stdin:
        data_list.append(line)
    if not data_list:
        return
    data_clean = preparse.decomment(data_list, '#')
    data_str = "\n".join(data_clean)

    if '```' in data_str:
        graphs = data_str.split('```')
        for idx, graph in enumerate(graphs):
            if idx%2 == 1:
                try:
                    pcode_obj = parser.parse(graph, parser.root)
                    html_lines = render.pobj_to_html5_ccs3_grid(pcode_obj)
                    sys.stdout.write("\n".join(html_lines))
                except parser.pp.ParseException:
                    sys.stdout.write(graph)
            else:
                sys.stdout.write(graph)
        return
    else:
        try:
            pcode_obj = parser.parse(data_str, parser.root)
            html_lines = render.pobj_to_html5_ccs3_grid(pcode_obj)
            for line in html_lines:
                sys.stdout.write(line)
            return
        except parser.pp.ParseException:
            pass
    sys.stdout.write('none')
    sys.stdout.write("\n".join(data_list))


if __name__ == "__main__":
    DESC = """A panelcode parser and renderer."""
    AP = argparse.ArgumentParser(
        description=DESC,
        epilog='EXAMPLE:\n  python ' + os.path.basename(__file__)
        + '-i ./data/ -f "*.txt" -o ./output\n \n',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    AP.add_argument('-t', '--type', default='fence',
                    help='set parsing type to fence or markdown'
                    )
    CL_ARGS = AP.parse_args()
    decode(CL_ARGS)
