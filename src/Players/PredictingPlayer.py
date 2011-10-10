'''
Predicting Player Class

@author: Michael Jensen
'''
from BasePlayer import BasePlayer
from collections import namedtuple

class PredictingPlayer(BasePlayer):
    '''
    Predicting player keeps track of what it thinks the enemy would do...
    '''
    
    Model = namedtuple('Model', ['planets', 'fleets'])
    SCOUT_FLEET_SIZE = 1
    
    def __init__(self):
        super(PredictingPlayer, self).__init__()
        self.model = self.Model({}, {})
        self.scout = None
        
    
    def update_model(self, pw):
        for planet in pw.Planets():
            if planet.IsInVision():
                self.model.planets[planet.ID()] = planet
            else:
                if self.model.planets.has_key(planet.ID()):
                    #update the planet in the model
                    model_planet = self.model.planets[planet.ID()]
                    if model_planet.Owner() != '0':
                        model_planet.AddShips(model_planet.GrowthRate())
                else:
                    self.model.planets[planet.ID()] = planet
                    
        #update the fleets that are out of range
        fleets_in_view = pw.EnemyFleets()
        for fleet in self.model.fleets.values():
            if not fleet in fleets_in_view:
                fleet.Tick()
                if fleet.TurnsRemaining() == 0:
                    dest = self.model.planets[fleet.DestinationPlanet().ID()]
                    remaining = dest.NumShips() - fleet.NumShips()
                    if(remaining < 0):
                        dest.NumShips(-remaining)
                        dest.Owner(fleet.Owner())
                        verb = "captured"
                    else:
                        dest.RemoveShips(fleet.NumShips())
                        verb = "arrived at"
                    pw.log("I think fleet %s just %s planet %s" % (fleet.ID(), verb, fleet.DestinationPlanet()))
                    del self.model.fleets[fleet.ID()]
        
        for fleet in pw.EnemyFleets():
            #fleet is guaranteed to be in vision
            self.model.fleets[fleet.ID()] = fleet
    
    def best_source(self, target, pw, desired_ships=1):
        #find the best source that has at least desired_ships + 1 on it
        #let's just assume best = closest
        closest = None
        closest_dist = 999999
        for planet in pw.MyPlanets():
            dist = planet.DistanceTo(target)
            if dist < closest_dist and planet.NumShips() > desired_ships:
                closest = planet
                closest_dist = dist
        return closest
    
    def get_scout_target(self, pw):
        target = None
        for planet in pw.EnemyPlanets():
            if not target:
                target = planet
            else:
                if target.VisionAge() < planet.VisionAge():
                    target = planet
        return target
    
    def send_scout(self, pw):
        target = self.get_scout_target(pw)
        
        if target:
            source = self.best_source(target, pw, self.SCOUT_FLEET_SIZE)
            if source:
                self.scout = pw.IssueOrder(source, target, self.SCOUT_FLEET_SIZE)
                
    def update_scout(self, pw):
        scout = pw.GetFleet(self.scout)
        if len(pw.MyPlanets()) == 0:
            self.scout = pw.IssueOrder(scout, scout.DestinationPlanet(), scout.NumShips())
            return
        if scout.TurnsRemaining() == 1:
            target = self.get_scout_target(pw)
            self.scout = pw.IssueOrder(scout, target, self.SCOUT_FLEET_SIZE)
    
    def DoTurn(self, pw):
        #update my model
        self.update_model(pw)
        if self.scout == None or pw.GetFleet(self.scout) == None:
            self.send_scout(pw)
        else:
            self.update_scout(pw)
        