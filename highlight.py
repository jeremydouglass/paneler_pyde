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

def all_styles(code, lexer=PanelcodeLexer(), prefix='test_'):
    print STYLE_MAP.keys()
    for smkey in STYLE_MAP.keys():
        with open(sketchPath() + '/' + prefix + smkey + '.html', 'w') as htmlfile: 
            formatter = HtmlFormatter(style=smkey)
            formatter.full = True
            html_str = highlight(code, lexer, formatter, outfile=htmlfile)

def style_string(code, lexer=PanelcodeLexer(), style='paraiso-dark'):
    formatter = HtmlFormatter(style=style)
    # formatter.full = True
    html_str = highlight(code, lexer, formatter)
    return html_str

def style_css(style='paraiso-dark'):
    return HtmlFormatter(style=style).get_style_defs('.highlight')

if __name__ == '__main__':
    print style_css(style=SolarizedStyle)
