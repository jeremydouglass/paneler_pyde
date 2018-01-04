"""Panelcode parsing functions.
Converts code strings into object trees for rendering.
Based on an implementation of the EBNF using pyparsing.
"""
import pyparsing as pp

# pylint: disable=bad-whitespace
# pylint: disable=invalid-name
# pylint: disable=line-too-long

## options and attributes

term = pp.Word(pp.alphas, pp.alphanums+'-')
key = term
equals = pp.Suppress('=')
value = pp.Suppress("'") + pp.Regex(r"[^']*") + pp.Suppress("'") | term
kv_expr = pp.Suppress(pp.Optional(pp.Literal("."))) + pp.Group(key + equals + value)
kv_word = pp.Suppress(pp.Optional(pp.Literal("."))) + pp.Group(pp.Regex(r"[a-zA-Z]+") + pp.Regex(r"[0-9]*"))
attr_word = pp.Suppress(pp.Optional(pp.Literal("."))) + term
attr_list = pp.ZeroOrMore(attr_word ^ kv_expr ^ kv_word)

b_opt_pg =  pp.Literal("{+") | pp.Literal("{")
b_opt_l =   pp.Literal("{|") | pp.Literal("{:")
b_opt_s =   pp.Literal("{;") | pp.Literal("{::")
b_opt_g =   pp.Literal("{@") | pp.Literal("{:::")
b_opt_r =  pp.Literal("{!") | pp.Literal("{::::")
e_opt =     pp.Literal("}")

panelgroupopts = (pp.Suppress(b_opt_pg) +
                  pp.Optional(attr_list) +
                  pp.Suppress(e_opt)).setResultsName('panelgroupopts', listAllMatches=True)
layoutopts  = (pp.Suppress(b_opt_l) +
               pp.Optional(attr_list) +
               pp.Suppress(e_opt)).setResultsName('layoutopts', listAllMatches=True)
spreadopts  = (pp.Suppress(b_opt_s) +
               pp.Optional(attr_list) +
               pp.Suppress(e_opt)).setResultsName('spreadopts', listAllMatches=True)
galleryopts = (pp.Suppress(b_opt_g) +
               pp.Optional(attr_list) +
               pp.Suppress(e_opt)).setResultsName('galleryopts', listAllMatches=True)
pcodeopts   = (pp.Suppress(b_opt_r) +
               pp.Optional(attr_list) +
               pp.Suppress(e_opt)).setResultsName('pcodeopts', listAllMatches=True)

## panelgroups

numrow         = pp.Regex(r"[0-9]*")
newcol         = pp.Literal("+")
newrow         = pp.Literal(",")
groupseparator = pp.Group(newcol ^ newrow)
groupunit      = pp.Group(numrow + pp.OneOrMore(attr_word) ^ numrow ^ attr_word)
groupterms     = pp.Suppress(pp.Optional(pp.Suppress(pp.Literal("(")))) + pp.Group(groupunit + pp.ZeroOrMore(groupseparator + groupunit)).setResultsName('terms', listAllMatches=True) + pp.Suppress(pp.Optional(pp.Suppress(pp.Literal(")"))))
panelgroup     = pp.Group((groupterms ^ groupunit) +
                          pp.Optional(panelgroupopts)).setResultsName('panelgroup', listAllMatches=True)

## levels of organization

layout         = pp.Group(pp.delimitedList(panelgroup, delim="_") +
                          pp.Optional(layoutopts)).setResultsName('layout', listAllMatches=True)
spread         = pp.Group(pp.delimitedList(layout, delim="|") +
                          pp.Optional(spreadopts)).setResultsName('spread', listAllMatches=True) # ++
gallery        = pp.Group(pp.delimitedList(spread, delim=";") +
                          pp.Optional(galleryopts)).setResultsName('gallery', listAllMatches=True)
root           = pp.Group(pp.delimitedList(gallery, delim="@") +
                          pp.Optional(pcodeopts)).setResultsName('pcode', listAllMatches=True) # ;;

def parse(code_str, parselevel):
    """Parse panelcode string at level parselevel.
    Levels are parser.root, parser.gallery etc.
    Renderers may assume a particular top-level,
    e.g. parser.root.
    """
    try:
        result = parselevel.parseString(code_str, parseAll=True)
        return result
    except pp.ParseException as err:
        raise err
