#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Formatting for Panelcode
Utility functions to support autoformatter methods that can convert Panelcode
back and forth between different forms, e.g.
-  minified
-  compact
-  flat
-  indent
"""

import argparse
import os
import random
import re
import textwrap
import sys
from functools import wraps


def cl_format(args):
    """Wrapper for dispatching different formatting calls."""
    data_list = []
    for line in sys.stdin:
        if isinstance(line, unicode):
            data_list.append(line)
        else:
            data_list.append(line.decode('utf8'))
    data = '\n'.join(data_list)
    formatter = PanelcodeFormatter(args.mode)
    data = formatter.format(data)
    if args.align:
        if args.column:
            data = formatter.align(data, args.align, int(args.column))
        else:
            data = formatter.align(data, args.align)
    if args.decomment:
        data = decomment(data, args.decomment)
    return data


def decomment(string, delims=None):
    """Remove whole line and end-of-line comments."""

    def delim_strip(string, delims):
        """Remove everything after e.g. a delimiter: '#'
           or a list of delimiters: #, //.
        """
        lines = string.split('\n')
        if isinstance(delims, basestring):
            delims = [delims]
        for idx, line in enumerate(lines):
            for delim in delims:
                if delim in line:
                    line = line[:line.find(delim)]
                    lines[idx] = line
        return '\n'.join(lines)

    if not delims:
        delims = ['#', '//']
    result = delim_strip(string, delims)
    return result


class PanelcodeGenerator(object):
    """Generator for Panelcode.
    Accepts a code sample as input; produces Markov chain output.
    """
    def __init__(self, string, maxwords=100, crop=True):
        super(PanelcodeGenerator, self).__init__()
        self.string = string
        self.maxwords = maxwords
        self.crop = crop
        self.table = None

    def chain(self, maxwords=None):
        """"Generate markov output."""
        if not maxwords:
            maxwords = self.maxwords
        result = self.markov_gen(maxwords=maxwords)
        result = result.replace(';', ';\n')
        result = self.comment_gen(result)
        return result

    def comment_gen(self, string=None, delim='#'):
        """Add random endline and full-line comments."""
        if not string:
            string = self.string

        def rtext(size=10):
            """Mock comment: random text string."""
            chars = '123456789'
            return ''.join(random.choice(chars) for _ in range(size))

        lines = string.split('\n')
        result = []
        for line in lines:
            if random.random() < 0.50:
                size = random.randint(3, 3)
                if random.random() < .75:
                    result.append(line + ' ' + delim + ' ' +
                                  'EOLCOMMENT-' + rtext(size) + '-\n')
                else:
                    result.extend([line, delim + ' ' +
                                  'LINECOMMENT-' + ' ' + rtext(size) + '-\n'])
            else:
                result.append(line)
        return '\n'.join(result)

    def markov_gen(self, maxwords=None):
        """Generate up to n tokens based on Markov chain."""

        def crop_open(string, delim1, delim2):
            """Trim end of string if it terminates with an open pair."""
            if delim1 in string:
                string = re.sub(r'' + delim1 + r'[^' + delim2 + ']*$',
                                '', string)
            return string

        if not self.table:
            self.markov_table()
        if not maxwords:
            maxwords = self.maxwords

        nonword = "\n"
        word1 = nonword
        word2 = nonword
        results = []
        for _ in xrange(self.maxwords):
            newword = random.choice(self.table[(word1, word2)])
            if newword == nonword:
                break
            results.append(newword)
            word1, word2 = word2, newword
        result_string = ' '.join(results)
        if self.crop:
            result_string = crop_open(' '.join(results), '{', '}')
        return result_string

    def markov_table(self):
        """Build a Markov chain transition table based on an example string.
        See code.activestate.com/recipes/194364-the-markov-chain-algorithm/
        """
        nonword = "\n"
        word1 = nonword
        word2 = nonword
        table = {}
        string = decomment(self.string)
        for word in string.split():
            table.setdefault((word1, word2), []).append(word)
            word1, word2 = word2, word
        table.setdefault((word1, word2), []).append(nonword)  # mark EOF
        self.table = table

    def tidy(self):
        """Standardize, e.g. add ommited dots."""
        self.string = re.sub(r'(\b[0-9]+)([a-zA-Z])', r'\1.\2', self.string)
        self.string = re.sub(r'[\(\)]', '', self.string)
        self.string = decomment(self.string)
        self.table = None


# pylint: disable=no-self-use
class PanelcodeFormatter(object):
    """Format Panelcode with minify, compact, flatten, or indent."""
    def __init__(self, mode='flatten'):
        super(PanelcodeFormatter, self).__init__()
        self.mode = mode

    # Decorators

    def _separate_comments(func):  # pylint: disable=no-self-argument
        """Parse comment blocks separately."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            """decorator wrapper"""
            string = args[0]
            lines = string.split('\n')
            opt_splitter = re.compile(r'(#[^\n]*)')
            results = []
            for line in lines:
                splits = opt_splitter.split(line)
                for item in splits:
                    if '#' not in item:
                        nargs = list(args)
                        nargs[0] = item
                        results.append(func(  # pylint: disable=not-callable
                            self, *nargs, **kwargs))
                    else:
                        results.append('  ' + item)
            return '\n'.join(results)
        return wrapper

    def _separate_opts(func):  # pylint: disable=no-self-argument
        """Parse option blocks separately."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            """decorator wrapper"""
            string = args[0]
            opt_splitter = re.compile(r'({[^}]*})')
            splits = opt_splitter.split(string)
            results = []
            for item in splits:
                if '{' not in item:
                    nargs = list(args)
                    nargs[0] = item
                    results.append(func(  # pylint: disable=not-callable
                        self, *nargs, **kwargs))
                else:
                    results.append(re.sub(r'\s+', ' ', item))
            return ' '.join(results)
        return wrapper

    def _flatten_opts(func):  # pylint: disable=no-self-argument
        """Option block on their own lines."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            """decorator wrapper"""
            string = func(self, *args, **kwargs)  # pylint:disable=not-callable
            string = re.sub(r'({[\@;\|_\+\,\:]+)', r'\n  \1', string)
            return string
        return wrapper

    # Formats

    def format(self, string, mode=None):
        """Format using the default formatter, or pass formatter name."""
        if not mode:
            mode = self.mode
        if mode == 'compact':
            return self.compact(string)
        elif mode == 'indent':
            return self.indent(string)
        elif mode == 'minify':
            return self.minify(string)
        elif mode == 'flatten':
            return self.flatten(string)
        return self.flatten(string)

    def compact(self, string, width=40):
        """Format panelcode in compact style - 80 char wrapped, few spaces."""
        string = decomment(string)
        delims = ['@', ';', '|', '_', '(', ')', '+', ',']
        string = self.wrap(string, delims, wrapper=' ')
        string = re.sub(r'\s+', ' ', string)
        if width:
            string = textwrap.fill(string, width=width)
        return string

    @_flatten_opts
    @_separate_opts
    def flatten(self, string):
        """Flat format: gallery / spread / layout on new lines."""
        string = decomment(string)
        string = re.sub(r'\s+', '', string)
        string = self.wrap(string, '@', '\n')
        delims = [';', '|', '{']
        string = self.wrap(string, delims, wrapper=['\n', ' '])
        delims = ['_', '(', ')', '+', ',']
        string = self.wrap(string, delims, wrapper=' ')
        string = '  ' + string.replace('  ', ' ')
        string = string.replace('#', ' #')
        string = self.tight_lines(string)
        return string

    def indent(self, string, tab='  ', base=0, parens=False):
        """Indent format: galleries / spreads+layouts / panels+groups."""
        if not parens:
            string = re.sub(r'[\(\)]', '', string)
        string = self.flatten(string)
        string = self.wrap(string, [';', '|'],
                           wrapper=['\n' + tab * base, ''])
        string = self.wrap(string, ['_'],
                           wrapper=['\n' + tab * (base + 1), ''])
        string = self.wrap(string, ['+', ','],
                           wrapper=['\n' + tab * (base + 2), ''])
        string = self.tight_lines(string)
        return string

    @_separate_opts
    def minify(self, string):
        """Format panelcode in minified style - minimal space, one line."""
        string = decomment(string)
        string = re.sub(r'\s+', '', string)
        return string

    # Utilities

    def align(self, string, delims,       # pylint: disable=too-many-arguments
              dist='auto', auto_max=50, skip_full=True):
        """Given a delimiter, create a visually aligned column.
        Respects existing text that makes alignment impossible.
        By default skips "full" comments with no other content.
        May align to a set distance, or find one automatically.
        Limit auto alignment to maximum distance with auto_max.

        Useful for pretty-printing columns of end-line comments
        and/or columns of option blocks. Supports multi-delims,
        but use multiple passes for different alignment rules.
        """
        # add hanging indent function for option blocks on multiple lines?

        if isinstance(delims, basestring):
            delims = [delims]

        def align_line(line, delim, dist):
            """Given a line, attempt to align delimiter to column distance."""
            pos = line.find(delim)
            if not line[:pos].strip() and skip_full:
                return line
            if pos < dist:
                return line[:pos] + (' ' * (dist - pos)) + line[pos:]
            if pos > dist:
                gap = line[dist - 1:pos]
                if not gap.strip():
                    return line[:dist - 1] + ' ' + line[pos:]
            return line

        lines = string.split('\n')
        if dist == 'auto':
            dist = 0
            for line in lines:
                pos = len(line)
                for delim in delims:
                    if delim in line:
                        pos = min(pos, line.find(delim))
                dist = max(dist, 1 + len(line[:pos - 1].strip()))
            dist = min(dist, auto_max)
        for delim in delims:
            for idx, line in enumerate(lines):
                if delim in line:
                    lines[idx] = align_line(line, delim, dist)
        return '\n'.join(lines)

    def join_opt_braces(self, string):
        """Reconnect opt opening brace modifiers."""
        delims = ['@', r'\;', r'\|', r'\_', r'\(', r'\)', r'\+', r'\,']
        for delim in delims:
            string = re.sub(r'{\n' + delim + r'\n', '{' + delim + ' ', string)
        return string

    def remove_space(self, string, new=''):
        """Minimize all whitespace."""
        return re.sub(r'\s+', new, string)

    def tight_lines(self, string):  # no blank lines
        """Remove blank lines (containing any whitespace)."""
        return '\n'.join([line for line in string.split('\n')
                          if line.strip() != ''])

    def wrap(self, string, toks, wrapper=' '):
        """Pad one or more tokens in a string with padding characters.
        Optionally takes a pre and post wrapper.
        """
        if isinstance(wrapper, basestring):
            wrap_left = wrapper
            wrap_right = wrapper
        else:
            wrap_left, wrap_right = wrapper[:2]
        if isinstance(toks, basestring):
            string = string.replace(toks, wrap_left + toks + wrap_right)
        for tok in toks:
            if tok in string:
                string = string.replace(tok, wrap_left + tok + wrap_right)
        return string


if __name__ == "__main__":
    DESC = """Autoformatting of Panelcode. Convert between minified, compact,
              flat, and indented. Align comment and option blocks.
              $ cat ex.panelcode.md | python format.py -m flatten -a { -c 25
              """
    AP = argparse.ArgumentParser(
        description=DESC,
        epilog='EXAMPLE:\n  python ' + os.path.basename(__file__) +
        '-m flatten -a {\n \n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    AP.add_argument('-m', '--mode', default='flatten',
                    help='set to minify, compact, flatten, indent, or pass')
    AP.add_argument('-a', '--align', default='',
                    help='pass a delimiter to align in a column')
    AP.add_argument('-c', '--column', default='',
                    help='column distance for delimiter alignment')
    AP.add_argument('-d', '--decomment', default='#',
                    help='strip comments')
    CL_ARGS = AP.parse_args()
    try:
        RESULT = cl_format(CL_ARGS)
        sys.stdout.write(RESULT.encode('utf-8'))
    except TypeError as err:
        print err
