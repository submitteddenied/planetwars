'''
Created on 12/09/2011

@author: Michael
'''

SAFETY_SHIPS = 5                #additional ships to be safe
ATTACK_SIZE = 100               #Minimum size of a planet before it will attack

ATTACK_FRACTION = 0.7           #when attacking, if you can't just cap it, how
                                #many of my ships do I send?
EXPAND_FRACTION = 0.7           #ditto above for expanding
ATTACK_EXTRA = 5                #the amount extra that you have to send
EXPAND_EXTRA = 5

from BasePlayer import BasePlayer

class AggressivePlayer(BasePlayer):
    '''
    The AggressivePlayer always attacks an enemy planet (the closest one) and 
    tries to capture a neutral planet near the enemy.
    '''
    
    def __init__(self, id=None):
        super(AggressivePlayer, self).__init__(id)
        self.attacker_id = None
        self.expander_id = None
    
    def NextAttack(self, pw):
        return self.NextOrder(pw, pw.MyPlanets(), pw.EnemyPlanets())
    
    def NextExpand(self, pw):
        temp = self.NextOrder(pw, pw.EnemyPlanets(), pw.NeutralPlanets())
        return self.NextOrder(pw, pw.MyPlanets(), [temp[1]])
    
    def NextOrder(self, pw, sources, dests):
        #find the closest planet of mine to the enemy
        lowestdist = 10000000
        source = None
        dest = None
        for mine in sources:
            for his in dests:
                thisdist = mine.DistanceTo(his)
                if thisdist < lowestdist:
                    lowestdist = thisdist
                    source = mine
                    dest = his
        
        return (source, dest)
    
    def LaunchFleet(self, pw, planets, fraction, extra, include_growth=True):
        source, dest = planets
        if (source == None) or (dest == None):
            return None
        dist = source.DistanceTo(dest)
        dest_strength = dest.NumShips() + extra
        if include_growth:
            dest_strength += dist * dest.GrowthRate()
        if(dest_strength < source.NumShips()):
            return pw.IssueOrder(source, dest, dest_strength)
        else:
            return pw.IssueOrder(source, dest, source.NumShips() * fraction)
    
    def LaunchAttack(self, pw, attackers):
        self.attacker_id = self.LaunchFleet(pw, attackers, ATTACK_FRACTION, 
                                ATTACK_EXTRA, True)
    
    def LaunchExpand(self, pw, expanders):
        self.expander_id = self.LaunchFleet(pw, expanders, EXPAND_FRACTION, 
                                EXPAND_EXTRA, False)
    
    def DoTurn(self, pw):
        if(self.attacker_id != None):
            atk_fleet = pw.GetFleet(self.attacker_id)
            if(atk_fleet.TurnsRemaining() == 1):
                self.attacker_id = None
            attack = False
        else:
            attack_planets = self.NextAttack(pw)
            attack = True
        
        if(self.expander_id != None):
            expo_fleet = pw.GetFleet(self.expander_id)
            if(expo_fleet.TurnsRemaining() == 1):
                self.expander_id = None
            expand = False
        else:
            expand_planets = self.NextExpand(pw)
            expand = True
        
        if attack:
            self.LaunchAttack(pw, attack_planets)
        if expand:
            self.LaunchExpand(pw, expand_planets)