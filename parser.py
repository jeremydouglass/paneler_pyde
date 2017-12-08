import pyparsing as pp

## options and attributes

attr_word      = pp.Suppress(pp.Optional(pp.Literal("."))) + pp.Word(pp.alphas, pp.alphanums+'-') # https://pythonhosted.org/pyparsing/pyparsing.OneOrMore-class.html
attr_list      = pp.ZeroOrMore(attr_word)
panelgroupopts = (pp.Suppress(pp.Literal("{")) + pp.Optional(attr_list) + pp.Suppress(pp.Literal("}"))).setResultsName('panelgroupopts', listAllMatches=True)
layoutopts     = (pp.Suppress(pp.Literal("{:")) + pp.Optional(attr_list) + pp.Suppress(pp.Literal("}"))).setResultsName('layoutopts', listAllMatches=True)
spreadopts     = (pp.Suppress(pp.Literal("{::")) + pp.Optional(attr_list) + pp.Suppress(pp.Literal("}"))).setResultsName('spreadopts', listAllMatches=True)
galleryopts    = (pp.Suppress(pp.Literal("{:::")) + pp.Optional(attr_list) + pp.Suppress(pp.Literal("}"))).setResultsName('galleryopts', listAllMatches=True)
pcodeopts      = (pp.Suppress(pp.Literal("{::::")) + pp.Optional(attr_list) + pp.Suppress(pp.Literal("}"))).setResultsName('pcodeopts', listAllMatches=True)

## panelgroups

numrow         = pp.Regex(r"[0-9]*")
newcol         = pp.Literal("+")
newrow         = pp.Literal(",")
groupseparator = pp.Group( newcol ^ newrow )
groupunit      = pp.Group(numrow + pp.OneOrMore(attr_word) ^ numrow ^ attr_word)
groupterms     = pp.Suppress(pp.Optional(pp.Suppress(pp.Literal("(")))) + pp.Group(groupunit + pp.ZeroOrMore( groupseparator + groupunit )).setResultsName('terms', listAllMatches=True) + pp.Suppress(pp.Optional(pp.Suppress(pp.Literal(")"))))
panelgroup     = pp.Group((groupterms ^ groupunit) + pp.Optional(panelgroupopts)).setResultsName('panelgroup', listAllMatches=True)

## levels of organization

layout         = pp.Group(pp.delimitedList(panelgroup, delim="_") + pp.Optional(layoutopts)).setResultsName('layout', listAllMatches=True)
spread         = pp.Group(pp.delimitedList(layout, delim="|") + pp.Optional(spreadopts)).setResultsName('spread', listAllMatches=True) # ++
gallery        = pp.Group(pp.delimitedList(spread, delim=";") + pp.Optional(galleryopts)).setResultsName('gallery', listAllMatches=True)
root           = pp.Group(pp.delimitedList(gallery, delim="@") + pp.Optional(pcodeopts)).setResultsName('pcode', listAllMatches=True) # ;;

def parse(code_str, parselevel):
    try:
        result = parselevel.parseString(code_str, parseAll=True)
        return result
    except pp.ParseException as e:
        raise e
