def pobj_to_html5_ccs3_grid(pcode_obj):
    """ convert a parsed panelcode object into html for html5 + css3-grid rendering"""
    html_str = []
    pcode = (pcode_obj.asDict())['pcode'][0] # no multiple pcode blocks - no delimiter
    pcodeopts = pcode.pop('pcodeopts', [['']]) # {:::: } # pcodeopts = pcode['pcodeopts']

    galleries = pcode.pop('gallery', '')
    for gallery in galleries:
        galleryopts = gallery.pop('galleryopts', [['']]) # {::: }
        html_str.append( '<div class="gallery ' + galleryopts[0][0] +'">')

        spreads = gallery.pop('spread', '')
        for spread in spreads:
            spreadopts = spread.pop('spreadopts', [['']]) # {:: }
            html_str.append( '  <div class="spread ' + spreadopts[0][0] +'">')
            
            layouts = spread.pop('layout', '')
            for layout in layouts:
                panelcounter = 0;
                panelskip = 0; # for blank x z panels
                layoutopts = layout.pop('layoutopts', [['']]) # {: }
                html_str.append( '    <div class="layout ' + layoutopts[0][0] +'">')
                
                panelgroups = layout.pop('panelgroup', '')
                for panelgroup in panelgroups:
                    panelgroupopts = panelgroup.pop('panelgroupopts', [['']]) # {}
                    terms = panelgroup.pop('terms', [['']])
                    ## build row list -- grouped by commas and skipping +
                    row_list = [[]]
                    for i in terms[0]:
                        ## , adds row sublist
                        if i==[',']:
                            row_list.append([])
                        ## skip +
                        elif i==['+']:
                            continue
                        ## missing counts = 1, e.g. ['']['r2'] = ['1']['r2']
                        elif i[0]=='':
                            i[0]='1'
                            row_list[-1].append(i)
                        ## 0 indicates a blank / spacer panel
                        elif i[0]=='0':
                            i[0]='1'
                            i.append('x') # or z? based on setting?
                            row_list[-1].append(i)
                            ## setting panels to x or z will impact panel numbering and total count
                        ## just append anything else
                        else:
                            row_list[-1].append(i)

                    ## Find the panelgroup width. This is either:
                    ## 1. Defined above, in the pcode, gallery, spread, or layout level.
                    ##    For example, newspaper comics might be defined at the spread
                    ##       or layout level for reflow.
                    ## 2. ...or else: Defined in panelgroupopts.
                    ## 3. ...or else: Calculated  from the longest row.
                    ##    (i.e. discovered via comma placement)
                    ##
                    ## In the css3 renderer width must be specified in the panelgroup class.
                    pgroup_width = 0;
                    if any(opt.startswith('w') for opt in pcodeopts[0]):
                        for opt in pcodeopts[0]:
                            if opt.startswith('w'):
                                pgroup_width = int(opt[1:])
                    elif any(opt.startswith('w') for opt in galleryopts[0]):
                        for opt in galleryopts[0]:
                            if opt.startswith('w'):
                                pgroup_width = int(opt[1:])
                    elif any(opt.startswith('w') for opt in spreadopts[0]):
                        for opt in spreadopts[0]:
                            if opt.startswith('w'):
                                pgroup_width = int(opt[1:])
                    elif any(opt.startswith('w') for opt in layoutopts[0]):
                        for opt in layoutopts[0]:
                            if opt.startswith('w'):
                                pgroup_width = int(opt[1:])
                    elif any(opt.startswith('w') for opt in panelgroupopts[0]):
                        for opt in panelgroupopts[0]:
                            if opt.startswith('w'):
                                pgroup_width = int(opt[1:])
                    else:
                        ## Find the length in panel spans of the longest row.
                        ## e.g. c3 + 2 = 5
                        ## This could be the first row, but not necessarily.
                        ## Rows are *not* the same length in groups with rowspans.
                        ## Rows could also be ragged. (in theory) although this
                        ## isn't explicitly supported.
                        row_lengths = []
                        for row in row_list:
                            row_len = 0
                            for panel in row:
                                ## check for 'c2' style column span arugment
                                ## ...there should be only one c arg, but the
                                ## max is taken if there are many, 1 if no arg.
                                c_args = [int(arg[1:]) for arg in panel if (arg.startswith('c') and len(arg)>1 and arg[1:].isdigit())]
                                # print(c_args)
                                try:
                                    c_max = max(c_args)
                                except ValueError:
                                    c_max = 1
                                ## multiply panel width by panel count
                                panel_len = int(panel[0]) * c_max
                                ## append panel length to total row length
                                row_len = row_len + panel_len
                            ## append row length to list
                            row_lengths.append(row_len)
                        ## set width to max
                        pgroup_width = max(row_lengths)
                    panelgroupopts[0][0] = panelgroupopts[0][0] + ' w' + str(pgroup_width)
                    html_str.append( '      <div class="panelgroup ' + panelgroupopts[0][0] +'">')

                    for row in row_list:
                        ## load panel arguments
                        for panel in row:
                            arg_add = []
                            for i, arg in enumerate(panel):
                                ## intercept generic u for CSS styling and add count
                                if arg.startswith('u'):
                                    if len(arg)==1:
                                        arg_add.append('u1')
                                    elif len(arg)>1:
                                        arg_add.append('u')
                                    ## note that the edge case e.g. u.u3 is not handled
                                    ## this will be fine for renderer (u_max=3, correct label)
                                    ## but will become u u1 u2 in css -- not consequential, but unclear
                            panel = panel + arg_add
                            panel_args = ' ' + ' '.join(panel[1:])
                            panel_count = int(panel[0])
                            ## print panels, assigning counts and id labels
                            for i in range(0, panel_count):
                                ## blank panels
                                if 'x' in panel_args or 'z' in panel_args:
                                    panelcounter += 1
                                    panelskip +=1
                                    html_str.append( '        <div class="panel ' + panel_args.strip() +'">*</div>')
                                ## unencoded (multi)panels -- mutually exclusive with blanks
                                elif 'u' in panel_args:
                                    ## ignore generic u and check for u# count
                                    u_args = [int(arg[1:]) for arg in panel if (arg.startswith('u') and len(arg)>1 )]
                                    ## after loading u_args, add generic u in-place for CSS styling
                                    try:
                                        u_max = max(u_args)
                                    except ValueError:
                                        u_max = 1
                                    if u_max == 0:
                                        panelcounter += 1
                                        panelskip +=1
                                        html_str.append( '        <div class="panel ' + panel_args.strip() +'">*</div>')
                                    elif u_max == 1:
                                        panelcounter += 1
                                        html_str.append( '        <div class="panel ' + panel_args.strip() +'">' + str(panelcounter-panelskip) + '</div>')
                                    else:
                                        html_str.append( '        <div class="panel ' + panel_args.strip() +'">' + str(panelcounter+1-panelskip) + '-' + str(panelcounter+(u_max)-panelskip) + '</div>')
                                        panelcounter += u_max                                        
                                ## regular panels
                                else:
                                    panelcounter += 1
                                    html_str.append( '        <div class="panel ' + panel_args.strip() +'">' + str(panelcounter-panelskip) + '</div>') #  data-pid="' + str(panelcounter-panelskip) + '"

                    html_str.append('      </div>')
                html_str.append('    </div>')
            html_str.append('  </div>')
        html_str.append('</div>')

    return html_str
