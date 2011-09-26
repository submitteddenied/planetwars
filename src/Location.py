'''
Created on 01/07/2011

@author: Michael
'''
from math import ceil, sqrt

class Location(object):
    '''
    Location simply specifies and X and Y position in space.
    '''

    def __init__(self, x, y):
        self._x = x
        self._y = y
        
    def X(self):
        return self._x
    
    def Y(self):
        return self._y
    
    def DistanceTo(self, other):
        dx = self.X() - other.X()
        dy = self.Y() - other.Y()
        return int(ceil(sqrt(dx * dx + dy * dy)))