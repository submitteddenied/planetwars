'''
Created on 16/09/2011

@author: Michael
'''

import shutil
import sys

def read_old_game(gameid, gamestate):
    lines = gamestate.split("\n")
    output = []
    planet_id = 1
    output.append("M %s 0 0 0\n" % gameid)
    for line in lines:
        tokens = line.split(" ")
        if tokens[0].startswith("#"):
            continue
        if tokens[0] == "P":
            output.append("%s %s %s %d %s %s %s\n" % (tokens[0],
                                                     tokens[1],
                                                     tokens[2],
                                                     planet_id,
                                                     tokens[3],
                                                     tokens[4],
                                                     tokens[5]))
            planet_id += 1
        if tokens[0] == "F":
            raise "FLEET IN A MAP FILE!?"
            
    return output

def convert_map(oldmap, newmap, mapid=1):
    old_file = file(oldmap, 'r')
    gamelines = old_file.read()
    old_file.close()
    outfile = file(newmap, 'w')
    game = read_old_game(mapid, gamelines)
    outfile.writelines(game)

if __name__ == '__main__':
    convert_map(sys.argv[1], sys.argv[2], sys.argv[3])