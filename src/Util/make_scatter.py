'''
Created on 15/09/2011

@author: Michael
'''

import sys
import re
import matplotlib.pyplot as plt

if __name__ == '__main__':
    infile = file(sys.argv[1], 'r')
    
    points = [[], []]
    idreg = "id=([0-9]+).*id=([0-9]+)"
    victoryreg = "([12]) victory"
    str = infile.readline()
    while str != "":
        coord = re.search(idreg, str).groups()
        str = infile.readline()
        g = re.search(victoryreg, str)
        if g:
            if g.groups()[0] == '2':
                points[0].append(coord[1])
                points[1].append(coord[0])
            else:
                points[0].append(coord[0])
                points[1].append(coord[1])
        else:
            #tie
            pass
        str = infile.readline()
    
    #for each point, draw them on a bitmap
    plt.plot(points[0], points[1], 'r.')
    plt.savefig(sys.argv[2])
    