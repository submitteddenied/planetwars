from Location import Location
from Entity import Entity

class Fleet(Entity):
    FLEET_RANGE = 2
    #the size of the fleet will add some vision range
    #with the formula: totalrange = FLEET_RANGE + (fleet.NumShips() * FLEET_FACTOR)
    FLEET_FACTOR = 0
    
    def __init__(self, fleet_id, owner_id, num_ships, source_x, source_y, \
                 destination_planet, progress=0):
        self._source = Location(source_x, source_y)
        self._destination_planet = destination_planet
        self._total_trip_length = self._source.DistanceTo(destination_planet)
        if(self._total_trip_length == 0):
            raise ValueError("Distance from source to destination is 0?")
        if(self._total_trip_length < progress):
            raise ValueError("More progress than distance!")
        
        self._turns_remaining = self._total_trip_length - progress
        super(Fleet, self).__init__(self.X(), self.Y(), fleet_id, num_ships, owner_id)
    
    def GetInRange(self, list, ignoredest=True):
        result = super(Fleet, self).GetInRange(list)
        if((self.TurnsRemaining() == 1) and (not result.has_key(self._destination_planet.ID()))
           and (not ignoredest)):
            result[self._destination_planet.ID()] = self._destination_planet
        
        return result
    
    def VisionRange(self):
        return self.FLEET_RANGE + (self.NumShips() * self.FLEET_FACTOR)
    
    def Source(self):
        return self._source
    
    def DestinationPlanet(self):
        return self._destination_planet
    
    def TotalTripLength(self):
        return self._total_trip_length
    
    def TurnsRemaining(self):
        return self._turns_remaining
    
    def Tick(self):
        self._turns_remaining -= 1
        self._location = Location(self.X(), self.Y())
    
    def X(self):
        source = self.Source()
        destination = self.DestinationPlanet();
        dx = destination.X() - source.X()
        dx *= 1 - (float(self.TurnsRemaining()) / float(self.TotalTripLength()))
        return source.X() + dx
    
    def Y(self):
        source = self.Source()
        destination = self.DestinationPlanet();
        dy = destination.Y() - source.Y()
        dy *= 1 - (float(self.TurnsRemaining()) / float(self.TotalTripLength()))
        return source.Y() + dy
    
    def Progress(self):
        return self.TotalTripLength() - self.TurnsRemaining()
    
    def Copy(self):
        return Fleet(self.ID(), self.Owner(), self.NumShips(), self.Source().X(), self.Source().Y(), self.DestinationPlanet().Copy(), self.Progress())