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
	
	maps = [file('../newmaps/map1.txt').read(),
					file('../newmaps/map2.txt').read(),
					file('../newmaps/map4.txt').read(),
					file('../newmaps/map5.txt').read(),
					file('../newmaps/map6.txt').read(),
					file('../newmaps/map7.txt').read(),
					file('../newmaps/map8.txt').read(),
					file('../newmaps/map9.txt').read(),
					file('../newmaps/map10.txt').read(),
					file('../newmaps/map11.txt').read()]
	logging.basicConfig(filename='../experiments/config-4/map-all/results.log', level=logging.INFO)
	Batch.batch_run(bots, maps)