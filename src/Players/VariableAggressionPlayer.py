'''
Created on 15/09/2011

@author: Michael
'''

from BasePlayer import BasePlayer

def min_100_ships(planet, pw):
    return 100

class VariableAggressionPlayer(BasePlayer):
    '''
    Each turn, each planet captures as many other planets as possible as long as it will be left with:
        min_ships_func(p.ID(), pw) * conservativeness
    ships afterwards
    '''
    
    def _default_min_ship_func(self, pid, pw):
        return 100
    
    def _default_planet_sort_func_func(self, pid, pw):
        '''
        Takes a planet id and the planetwars object and returns a function that
        takes a planet and returns a number that can be used to sort a list
        of planets
        '''
        source = pw.GetPlanet(pid)
        def result(planet):
            return source.DistanceTo(planet)
        
        return result
    
    def __init__(self, conservativeness, min_ships_func=None, \
                 planet_sort_func_func=None, id=None):
        super(VariableAggressionPlayer, self).__init__(id)
        self.conservativeness = conservativeness
        if min_ships_func is None:
            self.min_ships_func = self._default_min_ship_func
        else:
            self.min_ships_func = min_ships_func
        
        if planet_sort_func_func is None:
            self.planet_sort_func_func = self._default_planet_sort_func_func
        
    def __str__(self):
        return "<VariableAggressionBot id=%s conservativeness=%f>" % \
                (self.id, self.conservativeness)
    
    def do_planet_turn(self, planet, pw):
        min_ships = self.min_ships_func(planet.ID(), pw) * self.conservativeness
        self.attacking.sort(key=self.planet_sort_func_func(planet.ID(), pw))
        i = 0
        while planet.NumShips() > min_ships and i < len(self.attacking):
            target = self.attacking[i]
            if target.Owner() == pw.NEUTRAL_PLAYER:
                target_ships = target.NumShips() + 1
            else:
                target_ships = target.NumShips() + \
                (target.GrowthRate() * planet.DistanceTo(target)) + 1
            if planet.NumShips() - target_ships >= 0 and \
                planet.NumShips() - target_ships >= min_ships:
                pw.IssueOrder(planet, target, target_ships)
                self.attacking.remove(target)
            else:
                i += 1
        
    def DoTurn(self, pw):
        self.attacking = pw.NotMyPlanets()
        for planet in pw.MyPlanets():
            self.do_planet_turn(planet, pw)