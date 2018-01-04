import re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import bygroups, RegexLexer
from pygments.lexers import load_lexer_from_file
from pygments.token import *
from pygments.style import Style
from pygments.styles import STYLE_MAP

class PanelcodeLexer(RegexLexer): # PanelcodeLexer
    name = 'Panelcode'
    aliases = ['panelcode', 'pc']
    filenames = ['*.panelcode', '*.pcode', '*.panelcode.txt', '*.pcode.txt']
    tokens = {
        'root': [
            (r'\s+',   Text),                # whitespace
            (r'//.*?$', Comment),
            (r'#.*?$', Comment),
            (r'\{:*',  Punctuation, 'opts'),
            (r'[\+\,\_\|\;\@]', Operator),
            (r'[\(\)]', Punctuation),

            # (r'([a-zA-Z])', Punctuation, 'args'),
            # (r'[0-9]', Number.Integer),
            # (r'([a-zA-Z])', Punctuation, 'args'),

            (r'\.', Punctuation, 'dotopts'),
            (r'(\.)([a-z])([0-9])', bygroups(Punctuation, Name.Attribute, Name.Property)),
            (r'(\.)([a-z])(\-[0-9a-zA-Z\-]+)', bygroups(Punctuation, Name.Attribute, Name.Property)),
            (r'(\.)([a-zA-Z][0-9a-zA-Z\-]+)', bygroups(Punctuation, Name.Attribute)),
            (r'(\.)([a-zA-Z])', bygroups(Punctuation, Name.Attribute)),

            (r'([crw])([0-9]+)', bygroups(Name.Attribute, Literal)),
            (r'([biuxz])([0-9]+)', bygroups(Name.Attribute, Literal)),

            (r'[a-zA-Z\-][0-9a-zA-Z\-]*', Name.Attribute),
            # (r'[0-9][0-9]', Error),
            (r'[0-9]', Number.Integer),
        ],
        'dotopts' : [
            (r'[\+\,\_\|\;\@]', Operator, '#pop'),
            (r'\s+', Text, '#pop'),

            (r'([crw])([0-9]+)', bygroups(Name.Attribute, Literal)),
            (r'([biuxz])([0-9]+)', bygroups(Name.Attribute, Literal)),

            (r'(\.)', Punctuation),
            (r'[^\s\.]+', Name.Attribute)
        ],
        'opts' : [
            (r'(\.)', Punctuation),
            (r'\}', Punctuation, '#pop'),
            (r'\s+', Text),

            (r'([crw])([0-9]+)', bygroups(Name.Attribute, Literal)),
            (r'([biuxz])([0-9]+)', bygroups(Name.Attribute, Literal)),

            (r'(\w+)(\s?)([\:=])(\s?)',
             bygroups(Name.Attribute, Text, Punctuation, Text), 'optarg'),
            (r'[^\}\s]+', Name.Attribute)
        ],
        'optarg' : [
            (r'(\')([^\']*)(\')', bygroups(Punctuation, String.Single, Punctuation), '#pop'),
            (r'(\")([^\']*)(\")', bygroups(Punctuation, String.Double, Punctuation), '#pop'),
            (r'[0-9]+', Number.Integer, '#pop')
        ]
    }

class SolarizedStyle(Style):
    """Maps Solarized colors to Panelcode pygments tokens."""

    mode = 'light'
    default_style = ""
    
    base03 =  '#002b36' # dark: background
    base02 =  '#073642' # dark: bg highlights
    base01 =  '#586e75' # dark: comment       | light: emphasis
    base00 =  '#657b83' #                     | light: content
    base0 =   '#839496' # dark: content
    base1 =   '#93a1a1' # dark: emphasis      | light: comment
    base2 =   '#eee8d5' #                     | light: bg highlights
    base3 =   '#fdf6e3' #                     | light: background
    yellow =  '#b58900'
    orange =  '#cb4b16'
    red =     '#dc322f'
    magenta = '#d33682'
    violet =  '#6c71c4'
    blue =    '#268bd2'
    cyan =    '#2aa198'
    green =   '#859900'

    if mode == 'dark':
        background_color = base03
        highlight =  base02
        comment =    base01
        content =    base0
        emphasis =   base1
    else:
        background_color = base3
        highlight =  base2
        comment =    base1
        content =    base00
        emphasis =   base01

    styles = {
        Operator:       'bold ' + magenta,    # Matches @ ; | _ , + - and = :
        Punctuation:    'bold ' + content,
        Comment:        'italic ' + comment,
        Comment.Single: 'italic ' + comment, # Matches // or ## and on
        Number:         'bold ' + blue,
        Name:           'bold ' + violet,
        Literal:         violet,
        String:         'italic bg:' + highlight + ' ' + cyan,
        Keyword:         red,
        Text:            content,
    }


def all_styles(code, outpath, lexer=PanelcodeLexer(),
               prefix='test_', suffix='.html'):
    """Given code, outputs an HTML file for each available built-in style.
    A testing class for quickly previewing how a particular approach to
    lexer token naming will look across a variety of pre-existing styles.
    """
    print STYLE_MAP.keys()
    for smkey in STYLE_MAP.keys():
        fname = outpath + '/' + prefix + smkey + suffix
        with open(fname, 'w') as htmlfile:
            formatter = HtmlFormatter(style=smkey)
            formatter.full = True
            highlight(code, lexer, formatter, outfile=htmlfile)


def style_string(code, lexer=PanelcodeLexer(), style=SolarizedStyle,
                 full=False):
    formatter = HtmlFormatter(style=style)
    formatter.full = full
    html_str = highlight(code, lexer, formatter)
    return html_str


def style_css(style=SolarizedStyle, inline=False, defs='.highlight'):
    """Render CSS definitions for lexed Panelcode.
    Use 'inline to wrap in <style> tags, or save results as .css or .scss.

    Markdown processors strip style tags and references, so CSS generation
    will NOT work in preprocessors for Markdown. Instead the CSS class styling
    information must be added after Markdown processing.
    """
    css_str = HtmlFormatter(style=style).get_style_defs(defs)
    if inline:
        css_str = '<style>\n' + css_str + '\n<style>\n'
    return css_str


if __name__ == '__main__':
    import os
    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    TEST_CODE = '1 _ 2.b-a _ (r2+1,1)'
    all_styles(TEST_CODE, SCRIPT_PATH)     # save full html files per-style
    print style_css(style=SolarizedStyle)  # display css
