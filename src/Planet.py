from Entity import Entity

class Planet(Entity):
    PLANET_RANGE = 5
    #the size of the planet will add some vision range
    #with the formula: totalrange = PLANET_RANGE + (planet.GrowthRate() * PLANET_FACTOR)
    PLANET_FACTOR = 0
    
    def __init__(self, x, y, planet_id, owner_id, num_ships, growth_rate):
        super(Planet, self).__init__(x, y, planet_id, num_ships, owner_id)
        self._growth_rate = growth_rate
    
    def VisionRange(self):
        return self.PLANET_RANGE + (self.GrowthRate() * self.PLANET_FACTOR)

    def GrowthRate(self):
        return self._growth_rate
    
    def Copy(self):
        result = Planet(self.X(), self.Y(), self.ID(), self.Owner(), self.NumShips(), self.GrowthRate())
        return result;