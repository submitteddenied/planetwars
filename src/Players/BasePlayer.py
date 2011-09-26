'''
Created on 15/09/2011

@author: Michael
'''

class BasePlayer(object):
    '''
    Abstract Class used by player bots
    '''
    nextId = 1

    def __init__(self, id=None):
        '''
        Default constructor. Subclasses should call it, passing in an ID or None
        for an automatically allocated ID
        '''
        if id:
            self.id = id
        else:
            self.id = str(BasePlayer.nextId)
            BasePlayer.nextId += 1
    
    def DoTurn(self, pw):
        pass