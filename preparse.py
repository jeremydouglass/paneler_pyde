"""Panelcode preparse methods for detecting types of panelcode for parsing and
   cleaning, joining, segmenting or labeling them before parsing.
"""


def decomment(item, delim):
    """Remove whole line and end-of-line comments marked with a delimiter."""
    for itemline in item:
        seg = itemline.split(delim, 1)[0].strip()
        if seg != '':
            yield seg
        else:
            ## align line numbers in oarse error checking with original
            yield ''
