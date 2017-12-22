#!/usr/bin/env python
"""A panelcode parser and renderer."""

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
            result_list = preparse.parse_fenced_to_html(data_list)
            try:
                sys.stdout.write('\n'.join(result_list))
                return
            except TypeError as err:
                print err
        elif args.type == 'markdown':
            try:
                mdresult = render.pc_md_to_html(data_list)
                sys.stdout.write(mdresult)
                return
            except TypeError as err:
                print err
        sys.stdout.write('\n'.join(data_list))
        return


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
