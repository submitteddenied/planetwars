import sys
sys.path.append('C:\\Users\\Michael\\Documents\\My Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
import Batch
import logging
from Players import *
from PlanetWarsProxy import PlanetWarsProxy

if __name__ == "__main__":
	min_ships = lambda id, pw: 100
	bots = []
	for i in range(100):
		bots.append(VariableAggressionPlayer(i/100., min_ships))
	
	maps = [file('../newmaps/map1.txt').read()]
	logging.basicConfig(filename='../experiments/config-3/map-1/results.log', level=logging.INFO)
	Batch.batch_run(bots, maps)