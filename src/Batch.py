'''
Created on 15/09/2011

@author: Michael
'''

import Game
from Logger import Logger
from Players import *
import logging
from PlanetWars import PlanetWars
from PlanetWarsProxy import PlanetWarsProxy

def parse_config(config_file):
    pass
    
def batch_challenge(subjects, bots, maps, log_path, start_id=1, end_id=None):
    '''
    Takes two lists (subjects and bots) of bot_specs (see below) and compares each on the first list
    to each on the other on each of the given maps. Logs out to log_path, starting
    at experiment start_id and stopping at end_id, if specified.
    
    Note, this method prints to std_out, so that you have some idea of its 
    progress.
    
    bot_spec is a dict of:
        'type': bot class
        'params': dict of parameter names and values that will be used to
                  instantiate the bot for each game.
    '''
    game_id = 1
    log = Logger(log_path)
    if end_id is None:
        end_id = len(bots) * len(subjects) * len(maps)
    if end_id < start_id:
        raise ValueError("start_id must be less than the total number of experiments!")
    print "Starting batch. Running games %d to %d." % (start_id, end_id)
    for m in range(len(maps)):
        map_id = PlanetWarsProxy(maps[m])._gameid
        for i in range(len(subjects)):
            for j in range(len(bots)):
                if game_id >= start_id and game_id <= end_id:
                    bot1 = subjects[i]['type'](**subjects[i]['params'])
                    bot2 = bots[j]['type'](**bots[j]['params'])
                    status_str = "Starting game %d, %s vs %s on map %d" % (game_id, bot1, bot2, map_id)
                    log.result(status_str)
                    print status_str
                    Game.do_game(game_id, log, bot1, bot2, PlanetWars(maps[m]))
                    
                    log.flush()
                if game_id > end_id:
                    return
                game_id += 1

def batch_run(bots, maps):
    game_id = 1
    log = logging.getLogger("pw")
    for m in range(len(maps)):
        map_id = PlanetWarsProxy(maps[m])._gameid
        for i in range(len(bots)):
            for j in range(i + 1, len(bots)):
                log.info("Starting game %d, %s vs %s on map %d" % (game_id, bots[i], bots[j], map_id))
                Game.do_game(game_id, logging.getLogger("pw.game-%d" % game_id),
                             bots[i], bots[j], PlanetWars(maps[m]))
                game_id += 1

if __name__ == '__main__':
    #config_file = file(sys.argv[1], 'r')
    #parse_config(config_file)
    min_ships = lambda id, pw: 100
    bots = []
    for i in range(10):
        bots.append(VariableAggressionPlayer(i/10.0, min_ships))
    
    maps = [file('../newmaps/map1.txt', 'r').read(), file('../newmaps/map2.txt', 'r').read()]
    logging.basicConfig(filename='results10.log', level=logging.INFO)
    batch_run(bots, maps)
    