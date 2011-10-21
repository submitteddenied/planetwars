import sys
sys.path.append('C:\\Users\\Michael\\Documents\\My Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
sys.path.append('C:\\Documents and Settings\\mjensen\\Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
import Batch
import logging
from Players.VariableAggressionPlayer import VariableAggressionPlayer
from Players.PredictingPlayer import PredictingPlayer
from PlanetWarsProxy import PlanetWarsProxy

if __name__ == "__main__":
    min_ships = lambda id, pw: 100
    bots = []
    for i in range(50):
        bots.append(VariableAggressionPlayer(i/50., min_ships))
        
    subjects = [PredictingPlayer(True), PredictingPlayer(False)]
    
    maps = []
    for i in range(100):
        maps.append(file('../newmaps/map%d.txt' % (i + 1)).read())
    
    Batch.batch_challenge(subjects, bots, maps, '../experiments/config-8/map-all/%s.log')