'''
Created on 02/10/2011

@author: Michael
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from math import ceil, sqrt

def read_map(data):
    '''
    Returns (game_id, a list of (x, y, owner)) - the planets on the map
    '''
    result = []
    
    for line in data:
        tokens = line.split(" ")
        if tokens[0] == "P":
            result.append((float(tokens[1]), float(tokens[2]), float(tokens[6]), tokens[4]))
        elif tokens[0] == "M":
            mapid = int(tokens[1])
    return (mapid, result)
    
def read_map_from_file(map_name):
    mapfile = open(map_name, 'r')
    game_data = mapfile.read().split("\n")
    mapfile.close()
    return read_map(game_data)

def read_maps(base_path='../newmaps/', max_map=100):
    '''
    Takes a path and will load all maps from 1 to max_map (inclusive)
    '''
    result = {}
    for i in range(1, max_map + 1):
        map_data = read_map_from_file(base_path + "map%d.txt" % i)
        result[map_data[0]] = map_data[1]
        
    return result

def draw_map(id, map):
    '''
    Takes a list of planet (x, y, growth, owner) data and draws it onto a matplotlib
    plot. Returns the plot.
    '''
    fig = plt.figure()
    
    x = []
    y = []
    s = []
    c = []
    for planet in map:
        x.append(planet[0])
        y.append(planet[1])
        s.append((10 + planet[2] * 2) ** 2)
        if planet[3] == "0":
            c.append([0.25, 0.25, 0.25])
        elif planet[3] == "1":
            c.append([0, 0, 1])
        else:
            c.append([1, 0, 0])
    ax = fig.add_subplot(111)
    ax.scatter(x, y, c=c, s=s)
    ax.set_title("Layout of map %d" % id)
    
    return fig

def draw_map_graphs(maps, file_pattern, func=draw_map, output_latex=None, latex_caption="Map %d"):
    '''
    takes a dict of mapid: maps, draws all the map layouts
    Also takes a file_pattern, which must contain one %d for map name and should
    end in .pdf
    '''
    if output_latex:
        outfile = open(output_latex, 'w')
        outfile.write("\\begin{figure}\n\t\\centering")
        i = 0
    else:
        outfile = None
    
    for id, mapdata in maps.items():
        plot = func(id, mapdata)
        plot.savefig(file_pattern % id)
        if outfile:
            outfile.write("\t\\subfloat[%s]{\\includegraphics[width=6cm]{%s}}" % (latex_caption % id, file_pattern % id))
            i += 1
            if i % 9 == 0:
                outfile.write("""\label{LABEL}
\end{figure}
\begin{figure}
    \ContinuedFloat
    \centering""")
            elif i % 3 == 0:
                outfile.write("\\\\")
            
            outfile.write("\n")

def dist(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return int(ceil(sqrt(dx ** 2 + dy ** 2)))

def draw_map_histogram(id, map, from_perspective="1", bins=25):
    #read the map and make a list of distances
    distances = []
    
    for p in map:
        if p[3] == from_perspective:
            source = p
            break
    
    for p in map:
        if p == source: continue
        distances.append(dist(source, p))
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.xlim(0, 35)
    plt.ylim(0, 0.35)
    n, bins, patches = ax.hist(distances, bins, normed=1, facecolor='green', alpha=0.75)
    
    return fig

if __name__ == '__main__':
    id, map = read_map_from_file('../../newmaps/map1.txt')
    fig = draw_map(id, map)
    fig.savefig('../test-map1.pdf')