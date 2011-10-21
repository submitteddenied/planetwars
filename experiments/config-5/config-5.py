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
	
	maps = [file('../newmaps/map12.txt').read(),
					file('../newmaps/map13.txt').read(),
					file('../newmaps/map14.txt').read(),
					file('../newmaps/map15.txt').read(),
					file('../newmaps/map16.txt').read(),
					file('../newmaps/map17.txt').read(),
					file('../newmaps/map18.txt').read(),
					file('../newmaps/map19.txt').read(),
					file('../newmaps/map20.txt').read(),
					file('../newmaps/map21.txt').read()]
	logging.basicConfig(filename='../experiments/config-5/map-all/results.log', level=logging.INFO)
	Batch.batch_run(bots, maps)