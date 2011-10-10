'''
Template Player Class

@author: <You!>
'''
from BasePlayer import BasePlayer

class TemplatePlayer(BasePlayer):
    '''
    Describe your bot here!
    '''
    MINIMUM_SHIPS = 75
    
    def __init__(self):
        '''
        Default constructor. You can probably leave this unless you want to 
        add stuff
        '''
        super(TemplatePlayer, self).__init__()
        #Your initialisation here!
    
    def pick_target(self, pw, source):
        weakest = None
        w_strength = 9999999
        for planet in pw.NotMyPlanets():
            if planet.NumShips() < w_strength:
                weakest = planet
                w_strength = planet.NumShips()
            elif planet.NumShips() == w_strength:
                if source.DistanceTo(planet) < source.DistanceTo(weakest):
                    weakest = planet
                
        return weakest
    
    def DoTurn(self, pw):
        for planet in pw.MyPlanets():
            if planet.NumShips() > self.MINIMUM_SHIPS:
                pw.IssueOrder(planet, self.pick_target(pw, planet), planet.NumShips() -1)