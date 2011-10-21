import sys
sys.path.append('C:\\Users\\Michael\\Documents\\My Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
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
    
    maps = [file('../newmaps/map1.txt').read(), 
        file('../newmaps/map2.txt').read(), 
        file('../newmaps/map3.txt').read(),
        file('../newmaps/map4.txt').read(),
        file('../newmaps/map5.txt').read(),
        file('../newmaps/map6.txt').read()]
    Batch.batch_challenge(subjects, bots, maps, '../experiments/config-7/map-all/%s.log')