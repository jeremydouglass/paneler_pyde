#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render panelcode into target output formats.
   Includes Panelcode preparse methods for detecting types of panelcode for
   parsing and cleaning, joining, segmenting or labeling them before parsing.
"""

from __future__ import print_function
import datetime
import os
import re
import panelcode.parser as parser
import panelcode.highlight as highlight
import panelcode.templates as templates
try:
    import panelcode.libs.mistune as mistune
except ImportError:
    import mistune


CSS_ATTACH_SCRIPT = """<script type="text/javascript">
  $('head').append('<link rel="stylesheet" type="text/css" href="./custom.css">')
</script>"""
JQUERY_SCRIPT_CDN = """<script
  src="https://code.jquery.com/jquery-2.2.4.min.js"
  integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44="
  crossorigin="anonymous">
</script>"""
SIZER_SCRIPT = """<script type="text/javascript">
  $(document).ready(function(){
    // On load
    $('.gallery-size').change(function(){
      $(this).closest('div.gallery')
      .removeClass('default small thumb mini micro micro2')
        .addClass( $(this).val() );
    })
    $('.all-size').change(function(){
      $('div.gallery')
      .removeClass('default small thumb mini micro micro2')
        .addClass( $(this).val() );
    })
})
</script>"""


def console_html(size_list='', content='', summary='panelcode',
                 css_class='gallery-size', reveal='open'):
    """Render a console area for a gallery. Includes:
    1. a code view (syntax highlighting)
    2. resizing of gallery layouts
    3. show / hide console contents
    """
    if not size_list:
        size_list = ['', 'default', 'small', 'thumb', 'mini', 'micro2']
    template = 'console.html'
    tmpl = templates.load(filename=template)
    html_str = tmpl.render(summary=summary, option_list=size_list,
                           css_class=css_class, content=content,
                           reveal=reveal)
    return html_str


def parse_fenced_to_html(data_list, mode='replace', reveal='open',
                         consoles=True, colorize=True, fmt='markdown'):
    """Parse panelcode only within markdown fenced code blocks.
    Split a list of lines on fence open and close markers,
    attempt to render code block contents as panelcode or pass through,
    return a list of unchanged contents and possibly changed blocks.

    Results can replace the code block ('replace') or come
    before or after it ('pre' / 'post')
    """
    result_list = []
    global_opts = []
    fences = re.compile(  # see mistune
        r' *(`{3,}|~{3,})( *\S+ *)?\n'  # ```lang (removed)
        r'([\s\S]+?\s*)'
        r'(\1)(?: *\n+|$)')  # ```
    data_fence_list = fences.split('\n'.join(data_list))
    if consoles and len(data_fence_list) > 1:
        result_list.extend([JQUERY_SCRIPT_CDN, SIZER_SCRIPT])

    # inject css customization / override file hook
    result_list.extend([CSS_ATTACH_SCRIPT])

    # assemble all global opts from any code block and merge
    # before passing merged opts into per-code-block contexts
    global_opts_dict = dict()
    for idx, graph in enumerate(data_fence_list):
        if idx % 5 == 3:
            new_global_opts = (graph_to_pcode_obj(graph).asDict())['pcode'][0].pop('pcodeopts', [['']])
            if new_global_opts[0][0]:
                pass
            for item in new_global_opts[0]:
                if isinstance(item, list) and len(item) == 2:
                    global_opts_dict.update([item])
                if isinstance(item, basestring) and len(item) > 0:
                    global_opts_dict.update([[item, '']])
    global_opts_list = []
    for key, value in global_opts_dict.items():
        global_opts_list.append([key, value])
    global_opts.append(global_opts_list)

    for idx, graph in enumerate(data_fence_list):
        if graph is None:
            continue
        if idx % 5 == 0:
            if fmt == 'html' or 'htmlfull':
                result_list.append(mdhtml_to_html(graph))
            else:
                result_list.append(graph)
        if idx % 5 == 3:
            result = parse_graph_to_html(graph, mode, reveal,
                                         consoles, colorize, global_opts)
            result_list.append(result)
    if consoles and len(data_fence_list) > 1:
        console_str = console_html(content='',
                                   summary='Resize all galleries: ',
                                   css_class='all-size',
                                   reveal=reveal)
        result_list.append(console_str)
    result_list.append('<p style="font-size:x-small">' +
                       '<em>panelcode: fence pre-processor</em></p>\n')
    if fmt == 'htmlfull':
        result_list = html_page_wrapper(result_list)
    return result_list


def html_page_wrapper(data_list, pagetitle='', template='html_page.html',
                      styles_inline=True, show_timestamp=True, timestamp=''):
    """Wrap html contents in a full panelcode html page with styles.
    Styles_inline copies the style information into the page itself,
    rather than pointing to external stylesheets.
    """
    tmpl = templates.load(filename=template)
    if show_timestamp:
        timestamp = datetime.datetime.now().replace(microsecond=0)
    html_page_str = tmpl.render(contents=data_list,
                                pagetitle=pagetitle,
                                styles_inline=styles_inline,
                                datetime=timestamp
                                )
    result_list = html_page_str.split('\n')
    return result_list


def graph_to_pcode_obj(graph):
    """Convert panelcode code block to a pcode pyparsing object."""
    graph_clean = ''.join(decomment(graph))
    pcode_obj = parser.parse(graph_clean, parser.root)
    return pcode_obj


def parse_graph_to_html(graph, mode='replace', reveal='',
                        consoles=True, colorize=True, global_opts=None):
    """Parse panelcode only within markdown fenced code blocks.
    Split a list of lines on fence open and close markers,
    attempt to render code block contents as panelcode or pass through,
    return a list of unchanged contents and possibly changed blocks.

    Results can replace the code block ('replace') or come
    before or after it ('pre' / 'post')
    """
    result = ''
    if colorize:
        graph_out = unicode(highlight.style_string(graph))
    else:
        graph_out = '    <pre><code>' + graph + '    </code></pre>' + '\n'
        # ... or use data_fence_list[idx-2] -- catches ~~~ etc.
    try:
        pcode_obj = graph_to_pcode_obj(graph)
        html_lines = pobj_to_html5_ccs3_grid(pcode_obj, global_opts)
        console_str = ''
        if consoles or 'console' in graph:
            if 'noconsole' not in graph:
                console_str = console_html(content=graph_out,
                                           css_class='gallery-size',
                                           reveal=reveal)
        if mode == 'pre':
            html_lines.insert(-1, console_str)
            result += ''.join(html_lines)
        elif mode == 'post':
            result += '\n' + graph_out + '\n'
            result += ''.join(html_lines)
        elif mode == 'replace':
            result = ''.join(html_lines)
    except parser.pp.ParseException:
        result = graph_out
    return result


def decomment(string):
    """Remove whole line and end-of-line comments marked with delimiters.
    Checks for a delimiter '#' or a list of delimiters ['#, '//', ...].

    Design based on: https://regex101.com/r/yt1Xfy/1
    Test: https://regex101.com/r/kB5kA4/1

    The Group 1 umbrella capturing group compiles everything
    that should be preserved (if anything).
    """
    pattern = r"//.*|/\*[\s\S]*?\*/|(\"(\\.|[^\"])*\"|'(\\.|[^\'])*')"
    regex = re.compile(pattern)
    return regex.sub(lambda m: m.group(1), string)


class PanelCodeRenderer(mistune.Renderer):
    """Render full markdown document with fenced panelcode blocks"""
    def block_code(self, code, lang=None):
        html_str = ''
        if lang == 'panelcode':
            try:
                graph = ''.join(decomment(code))
                html_str = parse_graph_to_html(graph, mode='replace',
                    reveal='', consoles=True, colorize=True)
            except parser.pp.ParseException:
                html_str = '\n<pre><code>%s</code></pre>\n' % code
                # mistune.escape(code)
        else:
            html_str = '\n<pre><code>%s</code></pre>\n' % code
        return html_str
        # return sys.stdout.write(code)


def mdhtml_to_html(data_str):
    """Complete markdown rendering after panelcode embedded code blocks
    are rendered."""
    mdrenderer = mistune.Renderer()
    markdown = mistune.Markdown(renderer=mdrenderer)
    return markdown(data_str)


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def pc_md_to_html(data_list):
    """Render markdown with embedded panelcode to html."""
    pcrenderer = PanelCodeRenderer()
    markdown = mistune.Markdown(renderer=pcrenderer)
    label = '<p style="font-size:x-small"><em>panelcode: markdown processor (mistune)</em></p>\n'
    return markdown("\n".join(data_list) + label)


def img_render(kve, lopt_str, sopt_str, gopt_str, popt_str, glopt_str, img_path):
    """Render image preview strings based on settings."""
    i_before = ''
    i_layer = ''
    i_after = ''
    i_label_str_html = ''
    if 'img' in kve:
        img_paths = [x.strip() for x in kve['img'].split(':')]
        for opt_str in glopt_str, popt_str, gopt_str, sopt_str, lopt_str:
            if 'autoilabel' in opt_str:
                i_label_str = os.path.splitext(os.path.basename(img_paths[0]))[0]
                i_label_str_html = '      <div class="label bottom">' \
                    + i_label_str + '</div>'
        if 'ilabel' in kve:
            i_label_str = kve['ilabel']
            i_label_str_html = '      <div class="label bottom">' \
                + i_label_str + '</div>'
        img_tag_str = ''
        for idx, path in enumerate(img_paths):
            img_tag_str = img_tag_str + '<img src="' + img_path + img_paths[idx] + '"/>'
        for opt_str in [glopt_str, popt_str, gopt_str, sopt_str, lopt_str]:
            if 'ibefore' in opt_str:
                i_before = '    <div class="layout ' + lopt_str \
                         + '"><div class="img">' + img_tag_str + '</div>' \
                         + i_label_str_html + '</div>'
            if 'iafter' in opt_str:
                i_after = '    <div class="layout ' + lopt_str \
                        + '"><div class="img">' + img_tag_str + '</div>' \
                        + i_label_str_html + '</div>'
        if not (i_before or i_after):
            i_layer = '    <div class="img">' + img_tag_str + '</div>'
        return i_before, i_layer, i_after
    return '', '', ''


def opts_load(opts):
    """Retrieve lists of option types from an option ParseResult."""
    attr_words = []
    kv_words = []
    kv_exprs = {}
    for opt in opts:
        if isinstance(opt, basestring):  # attr_word
            attr_words.append(opt)
        elif isinstance(opt, list):
            if len(opt) == 1:  # attr_word
                attr_words.append(unicode(opt[0]))
            elif len(opt) == 2 and not opt[1]:  # attr_word
                attr_words.append(unicode(opt[0]))
            elif (len(opt) == 2 and
                  len(opt[0]) == 1 and
                  unicode(opt[0]).isalpha() and
                  unicode(opt[1]).isdigit()
                  ):  # kv_word
                kv_words.append(unicode(opt[0]) + unicode(opt[1]))
            else:  # kv_expr
                kv_exprs[unicode(opt[0])] = " ".join(opt[1:])
    return attr_words, kv_words, kv_exprs


def opts_render(opts, get_aw=True, get_kw=True, get_ke=False):
    """Render options for html."""
    attr_words, kv_words, kv_exprs = opts_load(opts)
    result = []
    if get_aw and attr_words:
        result.extend(attr_words)
    if get_kw and kv_words:
        result.extend(kv_words)
    if get_ke and kv_exprs:
        kve_strs = []
        for item in kv_exprs.items():
            kve_strs.append(unicode(item[0]) + "=" + "'" + unicode(item[1]) + "'")
        result.append(" ".join(kve_strs))
    return " ".join(result)


def pobj_counts(pcode_obj):
    """ simple statistics on a pcode object """
    pcode = (pcode_obj.asDict())['pcode'][0]  # no multiple pcode blocks - no delimiter
    counts = {'galleries': 0, 'spreads': 0, 'layouts': 0, 'panelgroups': 0}
    # , 'panels': 0, 'skips': 0 }
    galleries = pcode.pop('gallery', '')
    counts['galleries'] = len(galleries)
    for gallery in galleries:
        spreads = gallery.pop('spread', '')
        counts['spreads'] += len(spreads)
        for spread in spreads:
            layouts = spread.pop('layout', '')
            counts['layouts'] += len(layouts)
            for layout in layouts:
                panelgroups = layout.pop('panelgroup', '')
                counts['panelgroups'] += len(panelgroups)
    return counts


def pobj_globals(pcode_obj):
    """ convert a parsed panelcode object into html for html5 + css3-grid rendering"""
    html_str = []
    pcode = (pcode_obj.asDict())['pcode'][0]  # no multiple pcode blocks - no delimiter
    pcodeopts = pcode.pop('pcodeopts', [['']])  # {:::: } # pcodeopts = pcode['pcodeopts']


def pobj_to_html5_ccs3_grid(pcode_obj, global_opts):
    """ convert a parsed panelcode object into html for html5 + css3-grid rendering"""
    html_str = []
    pkve = opts_load(global_opts[0])[2]
    pcode = (pcode_obj.asDict())['pcode'][0]  # no multiple pcode blocks - no delimiter
    pcodeopts = pcode.pop('pcodeopts', [['']])  # {:::: } # pcodeopts = pcode['pcodeopts']

    galleries = pcode.pop('gallery', '')
    for gallery in galleries:
        galleryopts = gallery.pop('galleryopts', [['']])  # {::: }
        gkve = opts_load(galleryopts[0])[2]  # aw, kvw, kvw =
        try:
            imgpath = gkve['imgpath']
        except KeyError:
            try:
                imgpath = pkve['imgpath']
            except KeyError:
                imgpath = ''
        html_str.append('<div class="gallery ' + opts_render(global_opts[0]) + ' ' + opts_render(galleryopts[0]) + '">' + '\n')

        spreads = gallery.pop('spread', '')
        g_layout_counter = 0
        for spread in spreads:
            spreadopts = spread.pop('spreadopts', [['']])  # {:: }
            html_str.append('  <div class="spread ' + opts_render(spreadopts[0]) + '">' + '\n')

            layouts = spread.pop('layout', '')
            for layout in layouts:
                g_layout_counter += 1
                panelcounter = 0
                panelskip = 0  # for blank x z panels
                layoutopts = layout.pop('layoutopts', [['']])  # {: }
                kve = opts_load(layoutopts[0])[2]  # aw, kvw, kvw =
                i_before, i_str, i_after = img_render(
                    kve, opts_render(layoutopts[0]),
                    opts_render(spreadopts[0]),
                    opts_render(galleryopts[0]),
                    opts_render(pcodeopts[0]),
                    opts_render(global_opts[0]),
                    imgpath
                    )
                html_str.append(i_before)
                if 'url' in kve:
                    if 'http' not in kve['url']:
                        html_str.append('    <a href="http://' + kve['url'] + '">' + '\n')
                    else:
                        html_str.append('    <a href="' + kve['url'] + '">' + '\n')
                html_str.append('    <div class="layout ' + opts_render(layoutopts[0]) + '">' + '\n')
                label_str_html = ''

                panelgroups = layout.pop('panelgroup', '')
                for panelgroup in panelgroups:
                    panelgroupopts = panelgroup.pop('panelgroupopts', [['']])  # {}
                    terms = panelgroup.pop('terms', [['']])
                    # build row list -- grouped by commas and skipping +
                    row_list = [[]]
                    for term in terms[0]:
                        # , adds row sublist
                        if term == [',']:
                            row_list.append([])
                        # skip +
                        elif term == ['+']:
                            continue
                        # missing counts = 1, e.g. ['']['r2'] = ['1']['r2']
                        elif term[0] == '':
                            term[0] = '1'
                            row_list[-1].append(term)
                        # 0 indicates a blank / spacer panel
                        elif term[0] == '0':
                            term[0] = '1'
                            term.append('x')  # or z? based on setting?
                            row_list[-1].append(term)
                            # setting panels to x or z will impact panel numbering and total count
                        # just append anything else
                        else:
                            row_list[-1].append(term)

                    # Find the panelgroup width. This is either:
                    # 1. Defined above, in the pcode, gallery, spread, or layout level.
                    #    For example, newspaper comics might be defined at the spread
                    #       or layout level for reflow.
                    # 2. ...or else: Defined in panelgroupopts.
                    # 3. ...or else: Calculated  from the longest row.
                    #    (i.e. discovered via comma placement)
                    #
                    # In the css3 renderer width must be specified in the panelgroup class.
                    allopts = [pcodeopts[0], galleryopts[0],
                               spreadopts[0], layoutopts[0], panelgroupopts[0]]
                    pgroup_width = 0
                    while allopts and pgroup_width == 0:
                        opts = allopts.pop(0)
                        for opt in opts:
                            if isinstance(opt, basestring) and opt.startswith('w'):
                                pgroup_width = int(opt[1:])
                                break
                    if pgroup_width == 0:
                        # Find the length in panel spans of the longest row.
                        # e.g. c3 + 2 = 5
                        # This could be the first row, but not necessarily.
                        # Rows are *not* the same length in groups with rowspans.
                        # Rows could also be ragged. (in theory) although this
                        # isn't explicitly supported.
                        row_lengths = []
                        for row in row_list:
                            row_len = 0
                            for panel in row:
                                # check for 'c2' style column span arugment
                                # ...there should be only one c arg, but the
                                # max is taken if there are many, 1 if no arg.
                                c_args = [int(arg[1:]) for arg in panel
                                          if isinstance(arg, basestring)
                                          and arg.startswith('c')
                                          and len(arg) > 1
                                          and arg[1:].isdigit()]
                                # # print(c_args)
                                try:
                                    c_max = max(c_args)
                                except ValueError:
                                    c_max = 1
                                # multiply panel width by panel count
                                panel_len = int(panel[0]) * c_max
                                # append panel length to total row length
                                row_len = row_len + panel_len
                            # append row length to list
                            row_lengths.append(row_len)
                        # set width to max
                        pgroup_width = max(row_lengths)
                    panelgroupopts[0][0] = panelgroupopts[0][0] + ' w' + unicode(pgroup_width)
                    html_str.append('      <div class="panelgroup ' + panelgroupopts[0][0] + '">' + '\n')

                    for row in row_list:
                        # load panel arguments
                        for panel in row:
                            arg_add = []
                            for idx, arg in enumerate(panel):
                                # intercept generic u for CSS styling and add count
                                if arg.startswith('u') and isinstance(arg, basestring):
                                    if len(arg) == 1:
                                        arg_add.append('u1')
                                    elif len(arg) > 1 and arg[1:].isdigit():
                                        arg_add.append('u')
                                    # note that the edge case e.g. u.u3 is not handled
                                    # this will be fine for renderer (u_max=3, correct label)
                                    # but will become u u1 u2 in css -- works but unclear
                            panel = panel + arg_add
                            panel_args = ' ' + ' '.join(panel[1:])
                            panel_count = int(panel[0])
                            # print panels, assigning counts and id labels
                            for idx in range(0, panel_count):
                                pas = panel_args.strip()
                                # blank panels
                                if 'x' in panel_args or 'z' in panel_args:
                                    panelcounter += 1
                                    panelskip += 1
                                    html_str.append(
                                        '        <div class="panel '
                                        + pas + '">*</div>' + '\n'
                                        )
                                # unencoded (multi)panels -- mutually exclusive with blanks
                                elif 'u' in panel_args:
                                    # ignore generic u and check for u# count
                                    u_args = [int(arg[1:]) for arg in panel
                                              if (arg.startswith('u')
                                                  and len(arg) > 1)
                                              and arg[1:].isdigit()
                                              ]
                                    # after loading u_args, add generic u in-place for CSS styling
                                    try:
                                        u_max = max(u_args)
                                    except ValueError:
                                        u_max = 1
                                    if u_max == 0:
                                        panelcounter += 1
                                        panelskip += 1
                                        html_str.append(
                                            '        <div class="panel '
                                            + pas + '">*</div>' + '\n'
                                            )
                                    elif u_max == 1:
                                        panelcounter += 1
                                        label = unicode(panelcounter - panelskip)
                                        html_str.append(
                                            '        <div class="panel '
                                            + pas + '">' + label + '</div>' + '\n'
                                            )
                                    else:
                                        label = unicode(panelcounter + 1 - panelskip) + '-' + unicode(panelcounter + (u_max) - panelskip)
                                        html_str.append(
                                            '        <div class="panel '
                                            + pas + '">' + label + '</div>' + '\n'
                                            )
                                        panelcounter += u_max
                                # regular panels
                                else:
                                    panelcounter += 1
                                    label = unicode(panelcounter - panelskip)
                                    html_str.append(
                                        '        <div class="panel '
                                        + pas + '">' + label + '</div>' + '\n'
                                        )

                    html_str.append('      </div>' + '\n')

                html_str.append(i_str)
                try:
                    label_str_html = ''
                    for opt_str in [opts_render(layoutopts[0]),
                                    opts_render(spreadopts[0]),
                                    opts_render(galleryopts[0]),
                                    opts_render(pcodeopts[0])
                                    ]:
                        if 'autolabel' in opt_str:
                            try:
                                label_str = os.path.splitext(os.path.basename(kve['img']))[0]
                            except:
                                label_str = unicode(g_layout_counter)
                            label_str_html = '      <div class="label bottom">' \
                                + label_str + '</div>' + '\n'
                    if 'label' in kve:
                        label_str = kve['label']
                        label_str_html = '      <div class="label bottom"><div>' + label_str + '</div></div>' + '\n'
                    if label_str_html:
                        html_str.append('      ' + label_str_html)
                except TypeError:
                    pass
                html_str.append('    </div>' + '\n')
                if 'url' in kve:
                    html_str.append('    </a>' + '\n')
                html_str.append(i_after)
            html_str.append('  </div>' + '\n')
        html_str.append('</div>' + '\n')

    return html_str
