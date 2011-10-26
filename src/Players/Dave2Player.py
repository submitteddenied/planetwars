'''
Davebot mk.II

@author: David Howden
'''
from BasePlayer import BasePlayer
from Location import Location

#import copy
#x = copy.copy(y)        # make a shallow copy of y
#x = copy.deepcopy(y)    # make a deep copy of y

class Dave2Player(BasePlayer):
    '''
    Less hack than bot 1
    Has an extended front line instead of a single planet
    Attacks from multiple points instead of 1
    Sends defence to planets under attack
    Still no scouting
    '''
    
    def __init__(self, id):
        #Default constructor.
        super(Dave2Player, self).__init__(id)
        
        #Initialisation
        self.myCore = Location(0,0)
        self.theirCore =  Location(0,0)
        self.workingSet = 0
        self.turn = 0
        self._pw = None
    
    def DoTurn(self, pw):
        self._pw = pw
        self.turn += 1
        pw.log("%d" % self.turn)
        if len(pw.MyPlanets()) == 0:
            return
         
        #if no enemy planets left in sight, take neutrals then terminate turn
        if len(pw.EnemyPlanets()) == 0:
            for neutral in pw.NeutralPlanets():
                for planet in pw.MyPlanets():  
                    if not self.IncomingFriendlyFleet(pw, neutral):
                        if planet.NumShips() >= neutral.NumShips()+1:                                                
                            pw.IssueOrder(planet, neutral, neutral.NumShips()+1)
            return
        
        #check neutrals        
        neutrals = sorted(pw.NeutralPlanets(), key = self.SortByDist)        
        for neutral in pw.NeutralPlanets():
            closestFriendly = self.SubFrontLine(pw.MyPlanets(), neutral)
            closestEnemy = self.NearestEnemy(pw, neutral)
            for planet in pw.MyPlanets():                
                if (closestEnemy.DistanceTo(neutral) + 10) * neutral.GrowthRate() > neutral.NumShips():              
                    if not self.IncomingFriendlyFleet(pw, neutral):
                        if planet.NumShips() >= neutral.NumShips()+1:                                                
                            pw.IssueOrder(planet, neutral, neutral.NumShips()+1)
                
        #active defence
        for planet in pw.MyPlanets():
            defenceRequired = self.DefenceRequired(pw,planet)
            if defenceRequired > 0:
                #sort by planets by distance to planet needing defence                
                self.keySort_defendingPlanet = planet
                friendlyPlanets = sorted(pw.MyPlanets(), key = self.distToDefender)
                for f in pw.MyPlanets():
                    if defenceRequired <= 0:
                        break                    
                    if not f == planet:
                        #Better to check how much the planet can spare, rather than not sending at all if it's under attack
                        #Will be gamed by a opponent that constantly sends out scouts of 1
                        if not self.IncomingEnemyFleet(pw, f):
                            if f.NumShips() > defenceRequired:
                                pw.IssueOrder( f, self.ForwardPlanet(f, pw.MyPlanets(), planet), defenceRequired )
                                defenceRequired = 0;                              
                            elif f.NumShips() > 0:
                                pw.IssueOrder(f, planet, f.NumShips()) 
                                defenceRequired -= f.NumShips()
                        
        #passive reinforcment           
        for planet in pw.MyPlanets():
            if not self.IncomingEnemyFleet(pw, planet):
                closestEnemy = self.NearestEnemy(pw, planet)
                closestFriendly = self.SubFrontLine(pw.MyPlanets(), closestEnemy)            
                if not planet == closestFriendly and planet.NumShips() > 0:
                    pw.IssueOrder(planet, self.ForwardPlanet(planet, pw.MyPlanets(), closestFriendly), planet.NumShips())
        
        #attack from front line
        for planet in pw.EnemyPlanets():
            closestFriendly = self.SubFrontLine(pw.MyPlanets(), planet)  
            forceRequired = self.ForceRequired(pw, closestFriendly, planet)
            if forceRequired < closestFriendly.NumShips() and forceRequired > 0:
                pw.IssueOrder(closestFriendly, planet, forceRequired)
                
    
    def SortByDist(self,x):
        return x.DistanceTo(self.SubFrontLine(self._pw.MyPlanets(), x))
    
    #simple one planet nuke
    def ForceRequired(self, pw, base, target):
        strength = target.NumShips() + self.IncomingEnemyFleetStrength(pw, target) - self.IncomingFriendlyFleetStrength(pw, target) 
                
        strength += base.DistanceTo(target) * target.GrowthRate()
        
        strength += 1
        
        if strength < 0:
            return 0
        return strength
        
    #planetDefence
    #only called when enemy fleet is incoming
    #if no enemy fleet, growth rate will be multiplied by the default 9999 returned from arrival time
    def DefenceRequired(self, pw, base):
        #removing growth rate so that defence is over esitmated.  Easier than doing individual fleet arrival calulations for the moment
        strength = base.NumShips() #+= (self.EnemyFleetArrival(pw, base) * base.GrowthRate())
        
        strength -= self.IncomingEnemyFleetStrength(pw, base)
        strength += self.IncomingFriendlyFleetStrength(pw, base) 
        
        strength += (self.EnemyFleetArrival(pw, base) * base.GrowthRate())
        
        strength *= -1
        
        if strength < 0:
            return 0
        return strength
    
    #true if a friendly fleet is incoming
    def IncomingFriendlyFleet(self, pw, planet):
        for fleet in pw.MyFleets():
            if fleet.DestinationPlanet().ID() == planet.ID():
                return True
                
        return False
    
    #true if an enemy fleet is incoming    
    def IncomingEnemyFleet(self, pw, planet):
        for fleet in pw.EnemyFleets():
            if fleet.DestinationPlanet().ID() == planet.ID():
                return True
                
        return False
    
    #earliest enemy arrival time
    def EnemyFleetArrival(self, pw, planet):
        earliest = 9999
        for fleet in pw.EnemyFleets():
            if fleet.DestinationPlanet().ID() == planet.ID():
                if fleet.TurnsRemaining() < earliest:
                    earliest = fleet.TurnsRemaining()
                
        return earliest
    
    #earliest friendly arrival time
    def IncomingFriendlyFleetStrength(self, pw, planet):
        strength = 0
        for fleet in pw.MyFleets():
            if fleet.DestinationPlanet().ID() == planet.ID():
                strength += fleet.NumShips()                
        return strength
        
    #sum of all incoming enemy fleets    
    def IncomingEnemyFleetStrength(self, pw, planet):
        strength = 0
        for fleet in pw.EnemyFleets():
            if fleet.DestinationPlanet().ID() == planet.ID():
                strength += fleet.NumShips()                
        return strength
    
    def distToDefender(self, x):
        return self.keySort_defendingPlanet.DistanceTo(x)
        
    #find closest friendly planet to selected enemy planet
    def SubFrontLine(self, friendly, target):
        minDist = 9999
        friendlyFront = 0      
              
        for f in friendly:
            if f.DistanceTo(target) < minDist:
                minDist = f.DistanceTo(target)
                friendlyFront = f
        
        return friendlyFront
        
    #friendly planet closer to frontline
    def ForwardPlanet(self, base, planets, front):
        closestPlanet = front
        closestPlanetDist = base.DistanceTo(front)
        
        for planet in planets:
            
            if not planet == base:
                
                #if the prospective planet is closer to the frontline than the base planet
                if planet.DistanceTo(front) <  base.DistanceTo(front):
                
                    #and if the prospective planet is closer to the base planet than the best found so far
                    if planet.DistanceTo(base) < closestPlanetDist:
                    
                        closestPlanetDist = planet.DistanceTo(base)
                        closestPlanet = planet
   
        return closestPlanet
        
    #closest enemy planet
    def NearestEnemy(self, pw, base):
        nearestDist = 9999
        nearestPlanet = None
        for planet in pw.EnemyPlanets():
            if base.DistanceTo(planet) < nearestDist:
                nearestPlanet = planet
                nearestDist = base.DistanceTo(planet)
                
        return nearestPlanet
        
        
    