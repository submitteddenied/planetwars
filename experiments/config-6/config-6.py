import sys
sys.path.append('C:\\Users\\Michael\\Documents\\My Dropbox\\Projects\\Python Workspace\\PlanetWars\\src')
import Batch
import logging
from Players import *
from PlanetWarsProxy import PlanetWarsProxy

if __name__ == "__main__":
	min_ships = lambda id, pw: 100
	bots = []
	for i in range(50):
		bots.append(VariableAggressionPlayer(i/50., min_ships))
	
	maps = [file('../newmaps/map3.txt').read()]
	logging.basicConfig(filename='../experiments/config-6/map-all/results.log', level=logging.INFO)
	Batch.batch_run(bots, maps)