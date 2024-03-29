#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A panelcode parser and renderer."""

from __future__ import print_function
import argparse
import os
import sys

import panelcode
from panelcode import render

def decode(args):
    """Read in panelcode or embedded document stream, emit html rendering."""

    data_list = []
    for line in sys.stdin:
        if isinstance(line, unicode):
            data_list.append(line)
        else:
            data_list.append(line.decode('utf8'))
    if data_list:
        result_list = render.parse_fenced_to_html(data_list, mode='pre', fmt=args.type)
        try:
            sys.stdout.write('\n'.join(result_list).encode('utf-8'))
        except TypeError as err:
            print(err)


if __name__ == "__main__":
    DESC = """A panelcode parser and renderer."""
    AP = argparse.ArgumentParser(
        description=DESC,
        epilog='EXAMPLE:\n  python ' + os.path.basename(__file__) +
        '-t markdown\n \n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    AP.add_argument('-t', '--type', default='markdown',
                    help='set output type to: markdown, html, htmlpage')
    CL_ARGS = AP.parse_args()
    decode(CL_ARGS)
