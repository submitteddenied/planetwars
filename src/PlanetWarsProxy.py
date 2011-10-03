from Fleet import Fleet
from Planet import Planet
import uuid

class PlanetWarsProxy(object):
    NEUTRAL_PLAYER = "0"
    
    def __init__(self, gamestate=None):
        self._planets = {}
        self._fleets = {}
        self._extent = [0, 0, 0, 0]
        self._tick = 0
        self._playerid = None
        self._winner = 0
        self._gameid = None
        self._orders = []
        if(gamestate):
            self._ParseGameState(gamestate)
        
    def _ParseGameState(self, state):
        lines = state.split("\n")
        
        for line in lines:
            line = line.split("#")[0] # remove comments
            tokens = line.split(" ")
            if len(tokens) == 1:
                continue
            if tokens[0] == "P":
                if len(tokens) != 7:
                    return 0
                p = Planet( float(tokens[1]), #x
                            float(tokens[2]), #y
                            tokens[3], #planet id
                            tokens[4], #owner id
                            int(tokens[5]), #num_ships
                            int(tokens[6])) #growth_rate
                
                if(p.Y() + p.GrowthRate() > self._extent[0]):
                    self._extent[0] = p.Y() + p.GrowthRate()
                if(p.X() + p.GrowthRate() > self._extent[1]):
                    self._extent[1] = p.X() + p.GrowthRate()
                if(p.Y() - p.GrowthRate() < self._extent[2]):
                    self._extent[2] = p.Y() - p.GrowthRate()
                if(p.X() - p.GrowthRate() < self._extent[3]):
                    self._extent[3] = p.X() - p.GrowthRate() 
                
                self._planets[p.ID()] = p
            elif tokens[0] == "F":
                if len(tokens) != 8:
                    return 0
                f = Fleet(  int(tokens[1]), # Fleet ID
                            int(tokens[2]), # Owner
                            int(tokens[3]), # NumShips
                            int(tokens[4]), # Source X
                            int(tokens[5]), # Source Y
                            int(tokens[6]), # Destination
                            int(tokens[7])) # Progress
                self._fleets[f.FleetID()] = f
            elif tokens[0] == "M":
                self._gameid = int(tokens[1])
                self._playerid = int(tokens[2])
                self._tick = int(tokens[3])
                self._winner = int(tokens[4])
            else:
                return 0
        return 1
        
    def _Extent(self):
        return self._extent;
        
    
    def NumPlanets(self):
        return len(self._planets)
    
    def TotalShips(self):
        total = 0
        for planet in self.MyPlanets():
            total += planet.NumShips()
        for fleet in self.MyFleets():
            total += fleet.NumShips()
        
        return total

    def GetPlanet(self, planet_id):
        if(self._planets.has_key(planet_id)):
            return self._planets[planet_id]
        else:
            return None

    def NumFleets(self):
        return len(self._fleets)

    def GetFleet(self, fleet_id):
        if(self._fleets.has_key(fleet_id)):
            return self._fleets[fleet_id]
        else:
            return None

    def Planets(self):
        return self._planets.values()

    def MyPlanets(self):
        r = []
        for p in self._planets:
            planet = self._planets[p]
            if planet.Owner() == self._playerid:
                r.append(planet)
        return r

    def NeutralPlanets(self):
        r = []
        for p in self._planets:
            planet = self._planets[p]
            if planet.Owner() == PlanetWarsProxy.NEUTRAL_PLAYER:
                r.append(planet)
        return r

    def EnemyPlanets(self):
        r = []
        for p in self._planets:
            planet = self._planets[p]
            if ((planet.Owner() != self._playerid) and \
                (planet.Owner() != PlanetWarsProxy.NEUTRAL_PLAYER)):
                r.append(planet)
        return r

    def NotMyPlanets(self):
        r = []
        for p in self._planets:
            planet = self._planets[p]
            if planet.Owner() != self._playerid:
                r.append(planet)
        return r

    def Fleets(self):
        return self._fleets.values()

    def MyFleets(self):
        r = []
        for f in self._fleets:
            fleet = self._fleets[f]
            if fleet.Owner() == self._playerid:
                r.append(fleet)
        return r

    def EnemyFleets(self):
        r = []
        for f in self._fleets:
            fleet = self._fleets[f]
            #we assume there are no neutral fleets
            if fleet.Owner() != self.PlayerID():
                r.append(fleet)
        return r

    def _ToString(self):
        s = ''
        s+= "M %d %d %d %d\n" % \
            (self._gameid, self._playerid, self._tick, self._winnerid)
        for p in self._planets:
            s += "P %f %f %d %d %d\n" % \
             (p.X(), p.Y(), p.Owner(), p.NumShips(), p.GrowthRate())
        for f in self._fleets:
            s += "F %d %d %d %d %d %d\n" % \
             (f.Owner(), f.NumShips(), f.SourcePlanet(), f.DestinationPlanet(), \
                f.TotalTripLength(), f.TurnsRemaining())
        return s

    def Distance(self, source, destination):
        return source.DistanceTo(destination)

    def IssueOrder(self, source, destination_planet, num_ships):
        #is source a fleet or planet?
        num_ships = int(num_ships)
        if(type(destination_planet) == Planet):
            dest = destination_planet
        else:
            dest = self.GetPlanet(destination_planet)
        if(not dest):
            raise ValueError("You must pass a valid Planet as the destination!")
        if(type(source) == Fleet):
            f = source
        else:
            f = self.GetFleet(source);
        if(f):
            return self.FleetOrder(f, dest, num_ships)
        if(type(source) == Planet):
            p = source
        else:
            p = self.GetPlanet(source)
        if(p):
            return self.PlanetOrder(p, dest, num_ships)
        else:
            raise ValueError("You must pass a fleet or planet or an ID.")
    
    def FleetOrder(self, source_fleet, destination_planet, num_ships):
        source_fleet.RemoveShips(num_ships)
        fleetid = uuid.uuid4()
        self._orders.append(('fleet', source_fleet.ID(), fleetid, num_ships, destination_planet.ID()))
        return fleetid
    
    def PlanetOrder(self, source_planet, destination_planet, num_ships):
        source_planet.RemoveShips(num_ships)
        fleetid = uuid.uuid4()
        self._orders.append(('planet', source_planet.ID(), fleetid, num_ships, destination_planet.ID()))
        return fleetid
    
    def PlayerID(self):
        return self._playerid
        
    def _GetOrders(self):
        return self._orders
    
    def _ClearOrders(self):
        self._orders = []
        
    def _Update(self, pw, playerid=None, first_turn=False):
        if((playerid is not None) and (self._playerid is None)):
            self._playerid = playerid
        if(playerid is None and self._playerid is not None):
            playerid = self._playerid
        if(playerid is None):
            raise ValueError("No player id, can't determine what's in range!")
        planetsinview = {}
        fleetsinview = {}
        self._tick = pw.CurrentTick()
        
        if(first_turn):
            planets = pw.Planets()
            for planet in planets:
                planetsinview[planet.ID()] = planet
        
        for my_planet in pw.MyPlanets(self._playerid):
            planetsinview.update(my_planet.GetInRange(pw.Planets()))
            fleetsinview.update(my_planet.GetInRange(pw.Fleets()))
        
        for planet in self.MyPlanets():
            if(pw.GetPlanet(planet.ID()).Owner() != planet.Owner()):
                planetsinview[planet.ID()] = pw.GetPlanet(planet.ID())
        
        for my_fleet in pw.MyFleets(self._playerid):
            planetsinview.update(my_fleet.GetInRange(pw.Planets(), False))
            fleetsinview.update(my_fleet.GetInRange(pw.Fleets()))
            
        for planet in planetsinview.values():
            self._planets[planet.ID()] = planet.Copy()
            self._planets[planet.ID()].VisionAge(0)
        
        for id, planet in self._planets.items():
            if not planetsinview.has_key(id):
                planet.VisionAge(planet.VisionAge() + 1)
            
        #clear out the fleet list, if they aren't in view they disappear
        self._fleets = {}
        for fleet in fleetsinview.values():
            self._fleets[fleet.ID()] = fleet.Copy()
            self._fleets[fleet.ID()].VisionAge(0)
            
    def _EndGame(self, winnerid):
        self._winner = winnerid
    
    def CurrentTick(self):
        return self._tick
    