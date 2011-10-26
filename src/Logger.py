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
        self.log_data = []
        
    def flush(self):
        self.flush_file('results', self.results)
        self.flush_file('turns', self.turns)
        self.flush_file('player1', self.player1)
        self.flush_file('player2', self.player2)
        self.flush_file('data', self.log_data)
        
    def flush_file(self, filename, log):
        temp_file = open(self.pattern % filename, 'w')
        temp_file.writelines(log)
        temp_file.close()
        
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
        
    def data(self, message):
        self.append_message(self.log_data, message)