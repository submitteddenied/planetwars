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

def batch_challenge(subjects, bots, maps, log_path):
    game_id = 1
    log = Logger(log_path)
    for m in range(len(maps)):
        map_id = PlanetWarsProxy(maps[m])._gameid
        for i in range(len(subjects)):
            for j in range(len(bots)):
                log.result("Starting game %d, %s vs %s on map %d" % (game_id, subjects[i], bots[j], map_id))
                Game.do_game(game_id, log, subjects[i], bots[j], PlanetWars(maps[m]))
                game_id += 1
                log.flush()

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
    