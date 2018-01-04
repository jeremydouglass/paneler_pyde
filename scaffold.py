"""Render a starter panelcode file from a directory of page images."""

from __future__ import print_function
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


def images_to_markdown(fpath, fnpattern='*.png', fout='scaffold.md'):
    """For a group of image files in a source path fpath ('/images')
    matching a file pattern ('*.png') render a panelcode markdown file.
    """

    template = '/data/templates/markdown_scaffold.md'
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

    try:
        with open(fout, 'wb') as handle:
            handle.write(page_str)
    except EnvironmentError as err:
        print(fout + ' not saved.')
        print(err)
        raise

if __name__ == '__main__':
    context = '/Users/jeremydouglass/git/panelcode-data/works'
    images_to_markdown(context + '/Asterios_Polyp/tmb/',
                       '*.jpeg', 'Asterios_Polyp.md')
