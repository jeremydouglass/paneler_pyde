import re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import bygroups, RegexLexer
from pygments.lexers import load_lexer_from_file
from pygments.token import *
from pygments.styles import STYLE_MAP

class PanelcodeLexer(RegexLexer): # PanelcodeLexer
    name = 'Panelcode'
    aliases = ['panelcode', 'pc']
    filenames = ['*.panelcode', '*.pcode', '*.panelcode.txt', '*.pcode.txt']
    tokens = {
        'root': [
            (r'\s+',   Text),                # whitespace
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

            (r'([crw])([0-9]+)', bygroups(Keyword.Reserved, Name.Attribute)),
            (r'([biuxz])([0-9]+)', bygroups(Name.Builtin, Name.Attribute)),

            (r'[a-zA-Z\-][0-9a-zA-Z\-]*', Name.Attribute),
            # (r'[0-9][0-9]', Error),
            (r'\b[0-9]', Number.Integer),
        ],
        'dotopts' : [
            (r'[\+\,\_\|\;\@]', Operator, '#pop'),
            (r'\s+', Text, '#pop'),
            (r'([crw])([0-9]+)', bygroups(Keyword.Reserved, Name.Attribute)),
            (r'([biuxz])([0-9]+)', bygroups(Name.Builtin, Name.Attribute)),
            (r'(\.)', Punctuation),
            (r'[^\s\.]+', Name.Attribute)
        ],
        'opts' : [
            (r'(\.)', Punctuation),
            (r'\}', Punctuation, '#pop'),
            (r'\s+', Text),
            (r'([crw])([0-9]+)', bygroups(Keyword.Reserved, Name.Attribute)),
            (r'([biuxz])([0-9]+)', bygroups(Name.Builtin, Name.Attribute)),
            (r'(\w+)(\s?)(=)(\s?)',
             bygroups(Name.Attribute, Text, Operator, Text), 'optarg'),
            (r'[^\}\s]+', Name.Attribute)
        ],
        'optarg' : [
            (r'\'[^\']*\'', String.Single, '#pop'),
            (r'[0-9]+', Number.Integer, '#pop')
        ]
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
    return HtmlFormatter(style=style).get_style_defs() # '.highlight'
