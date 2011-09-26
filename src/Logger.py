'''
Created on 26/09/2011

@author: Michael
'''

class Logger(object):
    '''
    The Logger class allows you to log PlanetWars data to a file
    '''
    
    def __init__(self, filename_pattern):
        '''
        Creates a log file at this file location.
        The pattern must contain one '%s' which will be replaced with the name
        of each log file.
        '''
        self.pattern = filename_pattern
        self.results = []
        self.turns = []
        self.player1 = []
        self.player2 = []
        
    def flush(self):
        res = open(self.pattern % 'results', 'w')
        res.writelines(self.results)
        res.close()
        
        turns = open(self.pattern % 'turns', 'w')
        turns.writelines(self.turns)
        turns.close()
        
        p1file = open(self.pattern % 'player1', 'w')
        p1file.writelines(self.player1)
        p1file.close()
        
        p2file = open(self.pattern % 'player2', 'w')
        p2file.writelines(self.player2)
        p2file.close()
        
    def append_message(self, log, message):
        if message[-1] != "\n":
            message = message + "\n"
            
        log.append(message)
        
    def result(self, message):
        self.append_message(self.results, message)
        
    def turn(self, message):
        self.append_message(self.turns, message)
    
    def p1log(self, message):
        self.append_message(self.player1, message)
        
    def p2log(self, message):
        self.append_message(self.player2, message)