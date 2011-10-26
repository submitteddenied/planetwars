#! python
import sys
sys.path.append('C:\\Users\\Michael\\Documents\\My Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
sys.path.append('C:\\Users\\Michael\\Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
sys.path.append('C:\\Documents and Settings\\mjensen\\Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
import Batch
import logging
from Players.PredictingPlayer import PredictingPlayer
from PlanetWarsProxy import PlanetWarsProxy
import optparse

DESC = """Plays Predicting Bot against itself, with scouting on and off on all 100 maps."""

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="Usage: %prog [options] logdir", description=DESC)
    parser.add_option('-s', '--start', dest='start', metavar='S', help='Game to start with (inclusive)', default=1)
    parser.add_option('-e', '--end', dest='end', metavar='E', help='Game to process up to (inclusive)', default=None)
    (options, args) = parser.parse_args()
    logfolder = args[0]
    if not logfolder[-1] == "/":
        logfolder += "/"
    logfolder += "%s.log"

    start = options.start
    if start:
        start = int(start)

    end = options.end
    if end:
        end = int(end)

    min_ships = lambda id, pw: 100
    botid = 1
    bots = []
    for i in [True, False]:
        bots.append({'type': PredictingPlayer, 'params': {'scout_enabled': i, 'id': botid}})
        botid += 1
    
    maps = []
    for i in range(100):
        maps.append(file('../../newmaps/map%d.txt' % (i + 1)).read())
    
    Batch.batch_run(bots, maps, logfolder, start, end)