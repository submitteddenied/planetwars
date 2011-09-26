'''
Created on 19/09/2011

@author: Michael
'''

import sys
import re

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

def make_data(file_name):
  infile = file(file_name, 'r')
  
  idreg = "id=([0-9]+).*id=([0-9]+).*map ([0-9]+)"
  victoryreg = "([12]) victory at turn ([0-9]+) - 1: ([0-9]+), 2: ([0-9]+)"
  line = infile.readline()
  data_by_map = {}
  matchups = {}
  
  while line != "":
    research = re.search(idreg, line)
    coord = research.groups()[:-1]
    map = research.groups()[-1]
    line = infile.readline()
    g = re.search(victoryreg, line)
    if g.groups()[0] == "1":
      winner = coord[0]
      loser = coord[1]
    else:
      winner = coord[1]
      loser = coord[0]
    
    if not data_by_map.has_key(map):
      data_by_map[map] = []
    data = {'bots': (coord[0], coord[1]), coord[0]: g.groups()[2], coord[1]: g.groups()[3], 'winner': winner, 'time': int(g.groups()[1])}
    data_by_map[map].append(data)
    lower = min(int(coord[0]), int(coord[1]))
    higher = max(int(coord[0]), int(coord[1]))
    
    if not matchups.has_key(lower):
      matchups[lower] = {}
    if not matchups[lower].has_key(higher):
      matchups[lower][higher] = 0
    
    if data['winner'] == str(lower):
      matchups[lower][higher] += 1
    else:
      matchups[lower][higher] -= 1
    
    
    line = infile.readline()
  return (data_by_map, matchups)

def histogram(data, labels):

  fig = plt.figure()
  ax = fig.add_subplot(111)

  # the histogram of the data
  n, bins, patches = ax.hist(data, 50, normed=1, facecolor='green', alpha=0.75)

  # hist uses np.histogram under the hood to create 'n' and 'bins'.
  # np.histogram returns the bin edges, so there will be 50 probability
  # density values in n, 51 bin edges in bins and 50 patches.  To get
  # everything lined up, we'll compute the bin centers
  bincenters = 0.5*(bins[1:]+bins[:-1])

  ax.set_xlabel(labels[0])
  ax.set_ylabel(labels[1])
  ax.grid(True)
  
  #probably save this?
  return plt
  
def histogram_all(data_map, filename_format, labels=('Game length', 'Number of games')):
  '''
  Takes the data per map as output by make_data and saves a histogram of game
  lengths for each map by calling histogram.
  The filename_format string must contain exactly one %s token to be replaced by
  the map id when saving the file.
  eg: ../experiments/config-4/figures/map%s length.pdf
  '''
  map_times = {}
  for id, map_data in data_map.items():
    map_times[id] = []
    for datum in map_data:
      map_times[id].append(datum['time'])
    
  for id, times in map_times.items():
    plot = histogram(times, labels)
    plot.savefig(filename_format % id)
  
def matchup_pyplot(matchups):
  data = []
  for i in range(len(matchups)):
    r = []
    for j in range(i + 1, len(matchups) + 1):
      val = matchups[i + 1][j + 1]
      r.append(val)
      #instead of the score, append the color!
      #red = 127 * val / 10.0 + 127
      #blue = 127 * -val / 10.0 + 127
      #r.append(red/255.0, 0, blue/255.0, 1)
    while len(r) < 50:
      #r.append([0,0,0,0]) #completely transparent point
      r.append(0)
    data.append(r)
  
  #now, plot data using imshow!
  fig = plt.figure()
  ax = fig.add_subplot(111)
  cax = ax.imshow(data)
  ax.set_title('Win/loss over 10 matches')
  
  cbar = fig.colorbar(cax, ticks=[-10, 0, 10])
  #cbar.ax.set_yticklabels(['10 losses', '5 wins, 5 losses', '10 wins'])
  #plt.savefig(filename)
  return plt
  
  
if __name__ == '__main__':
  #let's make some data!
  data, match = make_data(argv[1])
  
  plt.savefig(sys.argv[2])
  