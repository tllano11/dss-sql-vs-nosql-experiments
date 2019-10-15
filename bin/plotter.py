#!/bin/python3
import os
import re
import sys
import csv
import numpy as np
import argparse
import pandas as pd
import matplotlib.lines as mlines
import matplotlib.cm as cmx
import matplotlib.colors as clrs
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8})
from itertools import cycle
from cycler import cycler

#def plotLine():
    # https://stackoverflow.com/questions/12487060/matplotlib-color-according-to-class-labels
    # https://stackoverflow.com/questions/14777066/matplotlib-discrete-colorbar
def parse_options(argv):
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-ph", "--plot_histogram", help="plot histogram",
                        action="store_true")
    group.add_argument("-pgh", "--plot_global_histogram", help="plot histogram",
                        action="store_true")
    group.add_argument("-pl", "--plot_line", help="plot line chart",
                        action="store_true")
    group.add_argument("-ppd", "--plot_percentage_decrease", help="plot percentage decrease",
                       action="store_true")
    parser.add_argument("-f", "--file_names", nargs='+', required=True, 
                        help="file/s to get data from")
    parser.add_argument("-bq", "--base_queries", nargs='+')
    parser.add_argument("-pdb","--plot_percentage_dec_bars", action="store_true")
    parser.add_argument("-pdl","--plot_percentage_dec_lines", action="store_true")
    parser.add_argument("-pbs", "--plot_barchart_single_scale", action="store_true")
    parser.add_argument("-pbss", "--plot_barchart_sscale_separate", action="store_true")
    parser.add_argument("-pls", "--plot_linechart_separate", action="store_true")
    args = parser.parse_args(argv)
    return args

def read(fname):
    with open(fname) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ')
        content = []
        for row in csvreader:
            query = row[0]
            time = float(row[1])
            content.append([query, time])
    return content

def get_scale(fname):
    scale = os.path.splitext(fname)[0]
    return scale

def classify(query):
    #parts = re.split('v|_', query)
    parts = query.split('_')
    qver = ''
    tmp = parts[0].split('v')
    if len(tmp) > 1:
        qnumber = int(tmp[0].split('q')[1])
        qver = tmp[1]
    else:
        qnumber = int(parts[0].split('q')[1])
    
    qtype = parts[-1]
    # col should be used for colors and number for plots
    return qnumber, qtype, qver

def add_interval(ax, line_args, caps="  "):
    line = ax.add_line(mlines.Line2D(**line_args))
    return line

def get_lines():
    markers = ['v', '.', 'X', 'p', '<', '>', 'P', '+', '*', 'o', '^', 'x', 's', '1']
    linestyles = ['-', '--', '-.', ':']
    cc = (cycler('linestyle', linestyles) * cycler('marker', markers))
    return cc

def get_data(fnames):
    records = {}
    for i, fname in enumerate(fnames):
        scale = os.path.splitext(fname)[0]
        content = read(fname)
        for row in content:
            query = row[0]
            runtime = float(row[1]) / 1000 # Convert to secs
            qnum, qtype, qver = classify(query)
            if not query in records:
                records[query] = {
                    "qnum": qnum,
                    "qver": qver,
                    "qtype": qtype,
                    scale: runtime
                }
            else:
                records[query].update({scale: runtime})
    df = pd.DataFrame.from_dict(records, orient='index')
    return df

def plot_percentage_dec_bars(fnames):
    df = get_data(fnames)
    numScales = len(df.drop(columns=['qnum', 'qver', 'qtype']).T.index)
    ylim = numScales
    plt.style.use('seaborn-darkgrid')
    plt.rcParams.update({'font.size': 8})
    gdf = df.groupby("qnum")
    for key, item in gdf:
        fig, ax = plt.subplots()
        barWidth=0.5
        bottom = [0]
        group = gdf.get_group(key)
        baseline = group[group['qtype']=='psql'].drop(columns=['qnum', 'qver', 'qtype'])
        group = group[group['qtype'] != 'psql']
        xticklabels = group.index.to_list()
        ind = np.arange(len(xticklabels))
        # Start placing values at the right hand of bars
        for column in group.drop(columns=['qnum', 'qver', 'qtype']):
            base = list(baseline[column])[0]
            increase = np.array([(x-base)/x for x in list(group[column])])
            increase[np.isnan(increase)] = sys.maxsize
            bars = ax.bar(ind, increase, bottom=bottom, width=barWidth)
            bars.set_label(column)
            for i, v in enumerate(increase):
                try:
                    offset = bottom[i]
                except IndexError:
                    offset = 0
                if v == sys.maxsize:
                    ax.text(i, ylim - ylim/4, 'Inf', horizontalalignment='center', fontsize=10)
                else:
                    ax.text(i, v/2 + offset, '{:.3f}'.format(v), horizontalalignment='center')
            bottom += increase
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_ylim(top=ylim)
        ax.set_xticks(ind)
        ax.set_xticklabels(xticklabels, rotation=30)
        ax.set_ylabel('Percentage increase')
        ax.set_xlabel('Query')
        fig.subplots_adjust(left=0.05, right=1, top=0.98, bottom=0.1)
        plt.savefig("{}_increase.png".format(group['qnum'].unique()[0]), 
                    bbox_inches='tight', format='png')

def plot_barchart_single_scale(fname):
    plt.style.use('classic')
    plt.rcParams.update({'font.size': 8})
    df = get_data(fname)
    scale = list(df.drop(columns=['qnum', 'qver', 'qtype']).columns)[0]
    numQueries = len(df['qnum'].unique())
    gdf = df.groupby("qnum")
    fig = plt.figure(figsize=(11.69,8.27))
    spot=0
    for key, item in gdf:
        spot += 1
        group = gdf.get_group(key)
        queries= group.index.to_list()
        qnum = group['qnum'].head(1)[0]
        baseline = group[group['qtype']=='psql'].drop(columns=['qnum', 'qver', 'qtype'])
        group = group[group['qtype'] != 'psql']
        queries = group.index.to_list()
        xpos = np.arange(len(queries))
        ax = fig.add_subplot(round(numQueries/2), 2, spot)
        for column in group.drop(columns=['qnum', 'qver', 'qtype']):
            bar = ax.bar(xpos, group[column], width=0.5)
            bar.set_label(column)
        base = list(baseline[scale])[0]
        ax.axhline(y=base, color='r')
        ax.set_xticks(xpos)
        ax.set_xticklabels(queries, rotation=15)
        ax.yaxis.grid(True)
        ax.tick_params(
            top=False,
            right=False,
        )
        ax.set_ylabel('Running time (sec)')
        ax.set_title('Query {}'.format(qnum), loc='right', pad=-12, fontsize=12, fontweight='bold')
    plt.savefig("barchart_scale_{}.png".format(scale), 
                bbox_inches='tight', format='png')
            
def plot_barchart_sscale_separate(fname):
    plt.style.use('classic')
    plt.rcParams.update({'font.size': 15})
    df = get_data(fname)
    scale = list(df.drop(columns=['qnum', 'qver', 'qtype']).columns)[0]
    numQueries = len(df['qnum'].unique())
    gdf = df.groupby("qnum")
    for key, item in gdf:
        fig = plt.figure()
        group = gdf.get_group(key)
        queries= group.index.to_list()
        qnum = group['qnum'].head(1)[0]
        baseline = group[group['qtype']=='psql'].drop(columns=['qnum', 'qver', 'qtype'])
        group = group[group['qtype'] != 'psql']
        queries = group.index.to_list()
        xpos = np.arange(len(queries))
        ax = fig.subplots()
        for column in group.drop(columns=['qnum', 'qver', 'qtype']):
            bar = ax.bar(xpos, group[column], width=0.5)
            bar.set_label(column)
        base = list(baseline[scale])[0]
        ax.axhline(y=base, color='r')
        ax.set_xticks(xpos)
        ax.set_xticklabels(queries, rotation=15, ha='right')
        ax.yaxis.grid(True)
        ax.tick_params(
            top=False,
            right=False,
        )
        ax.set_ylabel('Running time (sec)')
        ax.set_title('Query {} at the {} scale factor'.format(qnum, scale), loc='center', fontsize=19, fontweight='bold')
        plt.savefig("barchart_s{}q{}.png".format(scale, qnum), 
                    bbox_inches='tight', format='png')

def plot_linechart_separate(fnames):
    df = get_data(fnames)
    scales = list(df.drop(columns=['qnum', 'qver', 'qtype']).columns)
    numQueries = len(df['qnum'].unique())

    plt.style.use('classic')
    fontsize = 15
    plt.rcParams.update({'font.size': fontsize, 'legend.numpoints': 1})

    queries = df.index.to_list()
    styles = {}
    palette = plt.get_cmap('tab10')
    cc = get_lines()
    cc = list(cc)
    for query in queries:
        if numQueries > 1:
            key = df.at[query, 'qtype'] + df.at[query, 'qver']
        else:
            key = query
        if not key in styles:
            if df.at[query,'qtype'] == 'psql':
                styles[key] = {'color': 'black', 'style': {'linestyle':'--', 'marker':'$P$'}}
            else:
                styles[key] = {'color': None, 'style': None}
    numStyles = len(styles)
    for i, key in enumerate(styles.keys()):
        if styles[key]['style'] is None:
            styles[key]['color'] = palette(1.*i/numStyles)
            styles[key]['style'] = cc[0]
            cc = cc[1:]
    gdf = df.groupby("qnum")
    for key, item in gdf:
        fig = plt.figure()
        ax = fig.subplots()
        group = gdf.get_group(key)
        queries= group.index.to_list()
        labeledData = group.drop(columns=['qnum', 'qver', 'qtype']).T
        for query in queries:
            qnum, qtype, qver = classify(query)
            if numQueries > 1:
                key = qtype+qver
            else:
                key = query
            ax.plot(scales, query, label=query, data=labeledData, 
                    color=styles[key]['color'],
                    linestyle=styles[key]['style']['linestyle'],
                    marker=styles[key]['style']['marker'],
                    markersize=7
            )
            ax.set_ylabel('Running time (sec)')
            ax.set_xlabel('TPC-H Scale Factor')
            #ax.legend(loc='upper left', fontsize='small')
            ax.legend(fontsize='small')
            #ax.set_yscale('log')
            ax.grid(True)
            ax.set_title('Query {}'.format(qnum), loc='center', fontsize=fontsize+4, fontweight='bold')
            fig.tight_layout()
            plt.savefig("line_chart_q{}.png".format(qnum), format='png')

def plot_percentage_dec_lines(fnames):
    df = get_data(fnames)
    scales = list(df.drop(columns=['qnum', 'qver', 'qtype']).columns)
    numQueries = len(df['qnum'].unique())

    plt.style.use('classic')
    fontsize = 10
    if numQueries <= 1:
        fontsize = 20
    plt.rcParams.update({'font.size': fontsize, 'legend.numpoints': 1})

    queries = df.index.to_list()
    styles = {}
    palette = plt.get_cmap('tab10')
    cc = get_lines()
    cc = list(cc)
    for query in queries:
        if numQueries > 1:
            key = df.at[query, 'qtype'] + df.at[query, 'qver']
        else:
            key = query
        if not key in styles:
            if df.at[query,'qtype'] == 'psql':
                styles[key] = {'color': 'black', 'style': {'linestyle':'--', 'marker':'$P$'}}
            else:
                styles[key] = {'color': None, 'style': None}
    numStyles = len(styles)
    for i, key in enumerate(styles.keys()):
        if styles[key]['style'] is None:
            styles[key]['color'] = palette(1.*i/numStyles)
            styles[key]['style'] = cc[0]
            cc = cc[1:]
    gdf = df.groupby("qnum")
    fig = plt.figure(figsize=(11.69,8.27))
    #fig = plt.figure(figsize=(16.53,11.69))
    fig.set_size_inches(10.5, 18.5)
    spot = 0
    for key, item in gdf:
        spot += 1
        group = gdf.get_group(key)
        queries= group.index.to_list()
        if numQueries > 1:
            ax = fig.add_subplot(round(numQueries/2), 2, spot)
        else:
            ax = fig.subplots()
        #ax.set_prop_cycle(cc)
        labeledData = group.drop(columns=['qnum', 'qver', 'qtype']).T
        for query in queries:
            qnum, qtype, qver = classify(query)
            if numQueries > 1:
                key = qtype+qver
            else:
                key = query
            ax.plot(scales, query, label=query, data=labeledData, 
                    color=styles[key]['color'],
                    linestyle=styles[key]['style']['linestyle'],
                    marker=styles[key]['style']['marker'],
                    markersize=15
            )
            ax.set_ylabel('Running time (sec)')
            ax.set_xlabel('TPC-H Scale Factor')
            ax.legend(loc='upper center', fontsize='small')
            #ax.set_yscale('log')
            ax.grid(True)
            ax.set_title('Query {}'.format(qnum), loc='center', fontsize=fontsize+4, fontweight='bold')
        #cc = cc[len(queries):]
    if numQueries > 1:
        fig.subplots_adjust(left=0.07, right=0.92, top=0.98, bottom=0.02)
    else:
        fig.tight_layout()
    plt.savefig("line_charts.png", format='png')


def plot_percentage_decrease(fnames, bQuery):
    """
    Parameters
    ----------
    fnames : string[]
        Files to read data from
    bQuery : string[]
        Queries from which to calculate the percentage change
    """
    if len(fnames) != len(bQuery):
        return 1
    
    records = {"query":[], "qnum":[], "qver":[], "qtype":[], "runtime":[]}
    for i, fname in enumerate(fnames):
        content = read(fname)
        for row in content:
            qnum, qtype, qver = classify(row[0])
            records["query"].append(row[0])
            records["qnum"].append(qnum)
            records["qver"].append(qver)
            records["qtype"].append(qtype)
            records["runtime"].append(row[1])
        df = pd.DataFrame.from_dict(records)
        gdf = df.groupby("qnum")
        for key, item in gdf:
            #print(gdf.get_group(key), "\n\n")
            group = gdf.get_group(key)
            baseRuntime = group["runtime"].min()
            fig, ax = plt.subplots()
            position = np.arange(len(group["runtime"]))
            barWidth=0.4
            ax.bar(position, group["runtime"], align='center', width=barWidth)
            ax.set_xticks(position)
            ax.set_xticklabels(group["query"], rotation=45)
            for i, runtime in enumerate(group["runtime"]):
                if runtime == baseRuntime:
                    continue
                percent_increase = 100 * (runtime - baseRuntime)/runtime
                add_interval(
                    ax,
                    {'xdata':2*[i+(3*barWidth/4)],
                     'ydata':[baseRuntime, runtime], 
                     'color':'r', 'marker':'_'},
                )
                ax.text(
                    i+(4*barWidth/5), 
                    baseRuntime + (runtime-baseRuntime)/2, 
                    "+{:.3f}%".format(percent_increase),
                    color='r'
                )
            ax.hlines(baseRuntime, position[0]+(3*barWidth/4), 
                      position[-1]-barWidth/2, color='r', linestyle='--')
            plt.show()            

def plot_hist_1col(fnames):
    groups = {}
    labels = []
    xticks = []
    order = {}
    i = 0
    for fname in fnames:
        scale = os.path.splitext(fname)[0]
        labels.append(scale)
        content = read(fname)
        for row in content:
            query = row[0]
            time = float(row[1])
            qnumber, qtype, qver = classify(query)
            if qtype == "1collection":
                try:
                    groups[query].append(time)
                except:
                    groups[query] = [time]

    # set position of bars on x axis
    fig = plt.figure()
    barWidth = 0.25
    r = [np.arrange(len(groups[xticks[0]]))]
    for i in range(1,len(xticks)):
        r.append([x + barWidth for x in r[i-1]])
    
def plot_line(data, scales, groupColors):
    df = pd.DataFrame.from_dict(data, orient='index')
    # Normalize colormap to get different color per
    # combination of qtype and qver
    norm = clrs.Normalize(vmin=0, vmax=len(groupColors))
    cmap = cmx.ScalarMappable(norm=norm, cmap='tab10')

    # Initialize the figure
    plt.style.use('seaborn-darkgrid')
    plt.figure()
    i = 0
    for query in data.keys():
        _,qtype,qver = classify(query)
        key = qtype + qver
        try:
            color = groupColors[key]['c']
        except:
            color = cmap.to_rgba(i/0.6)
            groupColors[key]['c'] = color
            i += 1

        plt.plot(scales, query, data=df.T, color=color, 
                 dashes=groupColors[key]['l'], 
                 marker=groupColors[key]['m'])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel('Scale')
    plt.ylabel('Time (ms)')
    #plt.show()

def create_lineplots(fnames):
    # define the colormap
    cmaps = ['YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
             'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
             'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds']
    linestyles = cycle([
        (5,2),
        (2,5),
        (4,10),
        (1, 1), # densely dotted
        (5, 10), # loosely dashed
        (1, 10), # loosely dotted
        (3, 5, 1, 5), # dashdotted
        (3, 10, 1, 10), # loosely dashdotted
        (1, 1), # densely dotted
        (5, 1), # densely dashed 
        (3, 1, 1, 1, 1, 1), # densely dashdotted
        () # solid
    ])
    markers = ['1', '.', 'X', 'p', '<', '>', 'P', '+', '*', 'o', '^', 'v', 's', 'x']
    groupColors = {}
    queries = []
    scales = []
    data = {}
    for fname in fnames:
        scale = os.path.splitext(fname)[0]
        scales.append(scale)
        content = read(fname)
        for row in content:
            query = row[0]
            time = float(row[1])
            qnumber, qtype, qver = classify(query)
            if qnumber in data:
                try:
                    data[qnumber][query].append(time)
                except KeyError as e:
                    data[qnumber][query] = [time]
            else:
                data[qnumber] = {query:[time]}
            key = qtype + qver
            try:
                groupColors[key]
            except KeyError as e:
                groupColors[key] = {'m':markers.pop(), 
                                    'l':next(linestyles)}

    #cmap = plt.cm.get_cmap('jet', len(groupColors))
    for qnumber in data.keys():        
        plot_line(data[qnumber], scales, groupColors)
        plt.savefig('{}.png'.format(qnumber), bbox_inches='tight', format='png')

def autolabel(rects, ax):
    # for i, v in enumerate(df[column]):
    #     ax.text(v, i, ' ' + '{0:.3e}'.format(v), va='center')

    # Get y-axis height to calculate label position from.
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom

    for rect in rects:
        height = rect.get_height()

        # Fraction of axis height taken up by this rectangle
        p_height = (height / y_height)

        # If we can fit the label above the column, do that;
        # otherwise, put it inside the column.
        if p_height > 0.95: # arbitrary; 95% looked good to me.
            label_position = height - (y_height * 0.05)
        else:
            label_position = height + (y_height * 0.01)
        try:
            ax.text(rect.get_x() + rect.get_width()/2., label_position,
                    '%d' % int(height),
                    ha='center', va='bottom')
        except ValueError:
            continue

def create_global_histogram(fnames):
    numScales = 0
    numQueries = 0
    data = {}
    for fname in fnames:
        numScales += 1
        scale = get_scale(fname)
        content = read(fname)
        for row in content:
            query = row[0]
            time = float(row[1])
            qnumber, qtype, qver = classify(query)
            if qtype == "json" or qtype == "psql":
                continue
            if qnumber in data:
                try:
                    data[qnumber][query].update({scale:time})
                except KeyError as e:
                    data[qnumber][query] = {scale:time}
            else:
                numQueries += 1
                data[qnumber] = {query:{scale:time}}

    fig = plt.figure(figsize=(11.69,8.27))
    spot = 0
    # create a color palette
    palette = plt.get_cmap('jet')
    for qnumber in data.keys():
        df = pd.DataFrame.from_dict(data[qnumber], orient='index')
        x = df.index.to_list()
        ind = np.arange(len(x))
        colors = []
        for i in range(len(x)):
            colors.append(palette(1.*i/len(x)))
        for column in df:
            spot += 1
            uLimit = df[column].max()
            ax = fig.add_subplot(numQueries, numScales, spot)
            container = ax.bar(ind, df[column].fillna(sys.maxsize), color=colors, tick_label=x)
            # Set labels for the legend
            for i, child in enumerate(container.get_children()):
                child.set_label(x[i])
            #autolabel(container, ax)
            # Set title on top of columns
            if spot in range(numScales+1):
                ax.set_title(column, loc='center', fontsize=12, fontweight=1)
            # Do not show bottom ticks
            ax.tick_params(
                which='both',
                bottom=False,
                left=False,
                labelbottom=False,
                labelleft=False
            )
            if spot in range(1, (numQueries*numScales), 2*numScales):
                #plt.tick_params(labelleft=True)
                ax.legend(bbox_to_anchor=(-0.05,0.5), loc="center right", borderaxespad=0)
            elif spot in range(2*numScales, (numQueries*numScales + 1), 2*numScales):
                ax.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
            # Set after ticks or https://github.com/matplotlib/matplotlib/issues/4131
            ax.set_ylim(top=uLimit*1.1)
            #ax.set_yscale('log')
            ax.set_yscale('symlog', basey=2)

    #plt.text(0.5, 0.02, 'Runtime', ha='center', va='center')
    #plt.text(0.06, 0.5, 'Scale', ha='center', va='center', rotation='vertical')
    fig.subplots_adjust(bottom=0.05, top=0.89, left=0.1, right=0.89)
    #plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
    fig.suptitle('Cost comparison of MongoDB queries', fontsize=16)
    plt.savefig('global_chart.png', bbox_inches = "tight")
    
def create_histogram(fname):
    content = read(fname)
    # Order results before showing them
    content.sort(key=lambda x:x[1], reverse=True)
    queries = [row[0] for row in content]
    # Convert to mins
    times = [row[1] for row in content]    
    # Build chart
    ind = np.arange(len(times))
    width = 0.75
    fig, ax = plt.subplots()
    ax.barh(ind, times, width)
    ax.set_yticks(ind + width/2)
    ax.set_yticklabels(queries)
    for i, v in enumerate(times):
        ax.text(v, i, ' ' + '{0:.3f}'.format(v), va='center')
    plt.savefig('{}.png'.format(fname[:-4]), bbox_inches = "tight")

def main(argv):
    args = parse_options(argv[1:])
    if args.plot_histogram:
        create_histogram(args.file_names[0])
    elif args.plot_line:
        create_lineplots(args.file_names)
    elif args.plot_global_histogram:
        create_global_histogram(args.file_names)
    elif args.plot_percentage_decrease:
        plot_percentage_decrease(args.file_names, args.base_queries)
    elif args.plot_percentage_dec_bars:
        plot_percentage_dec_bars(args.file_names)
    elif args.plot_percentage_dec_lines:
        plot_percentage_dec_lines(args.file_names)
    elif args.plot_barchart_single_scale:
        plot_barchart_single_scale(args.file_names)
    elif args.plot_barchart_sscale_separate:
        plot_barchart_sscale_separate(args.file_names)
    elif args.plot_linechart_separate:
        plot_linechart_separate(args.file_names)

if __name__ == '__main__':
    main(sys.argv)
