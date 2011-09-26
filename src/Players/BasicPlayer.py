'''
Created on 23/03/2011

@author: Michael
'''

from BasePlayer import BasePlayer

class BasicPlayer(BasePlayer):
    def __init__(self, id=None):
        super(BasicPlayer, self).__init__(id)

    """
    // The DoTurn function is where your code goes. The PlanetWars object contains
    // the state of the game, including information about all planets and fleets
    // that currently exist. Inside this function, you issue orders using the
    // pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
    // planet 8, you would say pw.IssueOrder(3, 8, 10).
    //
    // There is already a basic strategy in place here. You can use it as a
    // starting point, or you can throw it out entirely and replace it with your
    // own. Check out the tutorials and articles on the contest website at
    // http://www.ai-contest.com/resources.
    """
    def DoTurn(self, pw):
        # (1) If we currently have a fleet in flight, just do nothing.
        if len(pw.MyFleets()) >= 1:
            return
        # (2) Find my strongest planet.
        source = -1
        source_score = -999999.0
        source_num_ships = 0
        my_planets = pw.MyPlanets()
        for p in my_planets:
            score = float(p.NumShips())
            if score > source_score:
                source_score = score
                source = p.ID()
                source_num_ships = p.NumShips()
    
        # (3) Find the weakest enemy or neutral planet.
        dest = -1
        dest_score = -999999.0
        not_my_planets = pw.NotMyPlanets()
        for p in not_my_planets:
            score = 1.0 / (1 + p.NumShips())
            if score > dest_score:
                dest_score = score
                dest = p.ID()
    
        # (4) Send half the ships from my strongest planet to the weakest
        # planet that I do not own.
        if source >= 0 and dest >= 0:
            num_ships = source_num_ships / 2
            pw.IssueOrder(source, dest, num_ships)