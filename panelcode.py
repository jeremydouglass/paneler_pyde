#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A panelcode parser and renderer."""

from __future__ import print_function
import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "panelcode", "libs"))

from panelcode import preparse
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
        if args.type == 'fence':
            result_list = preparse.parse_fenced_to_html(data_list, mode='pre')
            try:
                sys.stdout.write('\n'.join(result_list).encode('utf-8'))
            except TypeError as err:
                print(err)
        elif args.type == 'markdown':
            try:
                mdresult = render.pc_md_to_html(data_list)
                sys.stdout.write(mdresult.encode('utf-8'))
            except TypeError as err:
                print(err)


if __name__ == "__main__":
    DESC = """A panelcode parser and renderer."""
    AP = argparse.ArgumentParser(
        description=DESC,
        epilog='EXAMPLE:\n  python ' + os.path.basename(__file__) +
        '-t markdown\n \n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    AP.add_argument('-t', '--type', default='fence',
                    help='set parsing type to fence or markdown')
    CL_ARGS = AP.parse_args()
    decode(CL_ARGS)
