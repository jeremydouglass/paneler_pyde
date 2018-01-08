#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render a panelcode.md scaffold from a directory of images."""

from __future__ import print_function
import argparse
import datetime
import fnmatch
import os

import templates


def fpath_to_fnamelist(fpath, fnpattern):
    """
    Filepath to filename list:
    Take a directory and pattern, return a list of file paths.

    fnpattern filters results use Unix shell-style wildcards:
      (*, ?, [abc], [!abc])
    Uses fnmatch.filter.
    """
    return [os.path.join(dirpath, f)
            for dirpath, _dirnames, files in os.walk(fpath)
            for f in fnmatch.filter(files, fnpattern)]


def cl_scaffold(args):
    """Wrapper for dispatching different scaffolding calls.
    Currently only supports images to markdown scaffolding.
    """
    return images_to_markdown(args.input,
                              args.pattern,
                              args.template)


def images_to_markdown(fpath, fnpattern, template):
    """For a group of image files in a source path fpath ('/images')
    matching a file pattern ('*.png') render a panelcode markdown file.
    """
    tmpl = templates.load2(filename=template)
    fnamelist = fpath_to_fnamelist(fpath, fnpattern)
    results = []
    for fname in fnamelist:
        result = r" 1z {: img='" + fname + r"' }"
        results.append(result)

    page_str = tmpl.render(panelcode=fnamelist,
                           pagetitle='Panelcode-markdown scaffold',
                           datetime=datetime.datetime.now(),
                           galleryopts=r'{::: iafter autoilabel }'
                           )
    return page_str


if __name__ == "__main__":
    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    DESC = """Render a panelcode.md scaffold from a directory of images."""
    AP = argparse.ArgumentParser(
        description=DESC,
        epilog='EXAMPLE:\n  python ' + os.path.basename(__file__) +
        '-i dirpath -o outfile.panelcode.md\n \n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    AP.add_argument('-i', '--input',
                    default='/Users/jeremydouglass/git/panelcode-data/works' +
                    '/Asterios_Polyp/tmb/',
                    help='directory path for images'
                    )
    AP.add_argument('-p', '--pattern',
                    default='*.jpeg',
                    help='file name pattern for matching images'
                    )
    AP.add_argument('-t', '--template',
                    default='/data/templates/markdown_scaffold.md',
                    help='template file for scaffold layout'
                    )
    AP.add_argument('-o', '--output',
                    default='',  # Asterios_Polyp.panelcode.md
                    help='output path/filename out.panelcode.md'
                    )
    CL_ARGS = AP.parse_args()

    PAGE_STR = cl_scaffold(CL_ARGS)

    if CL_ARGS.output:
        try:
            with open(CL_ARGS.output, 'wb') as handle:
                handle.write(PAGE_STR)
        except EnvironmentError as err:
            print(CL_ARGS.output + ' not saved.')
            print(err)
            raise
    print(PAGE_STR)
