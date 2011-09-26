from Fleet import Fleet
from PlanetWarsProxy import PlanetWarsProxy
import logging

class PlanetWars(PlanetWarsProxy):
    def __init__(self, gamestate=None, logger=None):
        super(PlanetWars, self).__init__(gamestate)
        if not logger == None:
            self.logger = logger
        else:
            self.logger = logging.getLogger("pw")
        
    def Tick(self):
        #phase 1, departure is handled by IssueOrder
        
        #phase 2, Advancement
        for p in self._planets:
            planet = self._planets[p]
            if planet.Owner() != "0":
                planet.AddShips(planet.GrowthRate())
        
        #map of Planet => [Fleets]
        arrivals = {}
        for f in self._fleets:
            fleet = self._fleets[f]
            fleet.Tick()
            
            #phase 3a
            if(fleet.TurnsRemaining() == 0):
                if(not arrivals.has_key(fleet.DestinationPlanet())):
                    arrivals[fleet.DestinationPlanet()] = [fleet]
                else:
                    arrivals[fleet.DestinationPlanet()].append(fleet)
        
        #phase 3b
        for p in arrivals:
            forces = {}
            for f in arrivals[p]:
                self._fleets.pop(f.ID())
                if forces.has_key(f.Owner()):
                    forces[f.Owner()] += f.NumShips()
                else:
                    forces[f.Owner()] = f.NumShips()
            #add the current occupier of the planet
            if forces.has_key(p.Owner()):
                forces[p.Owner()] += p.NumShips()
            else:
                forces[p.Owner()] = p.NumShips()
            
            max = 0
            second = 0
            owner = p.Owner()
            for f in forces:
                if(forces[f] > max):
                    second = max
                    max = forces[f]
                    owner = f
                elif(forces[f] > second):
                    second = forces[f]
            
            if(max == second):
                #p.Owner() stays the same
                self.logger.debug("{0:4d}: Player {1} defended planet {2}".format(
                            self._tick, owner, p.ID()))
            else:
                if(p.Owner() == owner):
                    self.logger.debug("{0:4d}: Player {1} defended planet {2}".format(
                            self._tick, owner, p.ID()))
                else:
                    p.Owner(owner)
                    self.logger.debug("{0:4d}: Player {1} now owns planet {2}".format(
                                self._tick, owner, p.ID()))
                p.NumShips(max - second)
                
        self._tick += 1
    
    def MyPlanets(self, player_id):
        r = []
        for p in self._planets:
            planet = self._planets[p]
            if planet.Owner() != player_id:
                continue
            r.append(planet)
        return r

    def EnemyPlanets(self, player_id):
        r = []
        for p in self._planets:
            planet = self._planets[p]
            if (planet.Owner() == player_id) or (planet.Owner() == 0):
                continue
            r.append(planet)
        return r

    def NotMyPlanets(self, player_id):
        r = []
        for p in self._planets:
            planet = self._planets[p]
            if planet.Owner() == player_id:
                continue
            r.append(planet)
        return r

    def MyFleets(self, player_id):
        r = []
        for f in self._fleets:
            fleet = self._fleets[f]
            if fleet.Owner() != player_id:
                continue
            r.append(fleet)
        return r

    def EnemyFleets(self, player_id):
        r = []
        for f in self._fleets:
            fleet = self._fleets[f]
            if (fleet.Owner() == player_id) or (fleet.Owner() == PlanetWarsProxy.NEUTRAL_PLAYER):
                continue
            r.append(fleet)
        return r

    def IsAlive(self, player_id):
        if(len(self.MyPlanets(player_id)) > 0 or 
            len(self.MyFleets(player_id)) > 0):
            return True
        return False
    
    def MakeProxy(self, player_id):
        result = PlanetWarsProxy()
        result._extent = self._extent
        result._Update(self, player_id, True)
        return result
    
    def ProcessOrders(self, player_id, orders):
        for order in orders:
            new_id = order[2]
            if(order[0] == 'fleet'):
                source = self.GetFleet(order[1])
            else:
                source = self.GetPlanet(order[1])
            dest = self.GetPlanet(order[4])
            numships = order[3]
            fleet = Fleet(new_id, player_id, numships, source.X(), source.Y(), dest)
            self.logger.debug("{0:4d}: Player {1} launched {2} (of {3}) ships from planet {4} to planet {5}".format(
                            self._tick, player_id, numships, source.NumShips(), source.ID(), dest.ID()))
            self._fleets[new_id] = fleet
            source.RemoveShips(numships)