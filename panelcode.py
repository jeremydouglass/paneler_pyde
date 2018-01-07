#!/usr/bin/env python
"""A panelcode parser and renderer."""

from __future__ import print_function
import argparse
import os
import sys

import preparse
import render


def decode(args):
    """Read in panelcode or embedded document stream, emit html rendering."""

    data_list = []
    for line in sys.stdin:
        data_list.append(line)
    if data_list:
        if args.type == 'fence':
            result_list = preparse.parse_fenced_to_html(data_list, mode='pre')
            try:
                sys.stdout.write('\n'.join(result_list))
            except TypeError as err:
                print(err)
        elif args.type == 'markdown':
            try:
                mdresult = render.pc_md_to_html(data_list)
                sys.stdout.write(mdresult)
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
