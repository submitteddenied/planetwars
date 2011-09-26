'''
Created on 21/06/2011

@author: Michael
'''

#These are used for:
# a) as constants
# b) determining the priority of fleet scheduling
COUNTER_ATTACK = 0
COUNTER_EXPAND = 1
REINFORCE = 2
EXPANSION = 3

SAFETY_SHIPS = 5                #additional ships to be safe
ATTACK_SIZE = 100               #Minimum size of a planet before it will attack
REALLY_BIG_NUMBER = 10000000    #Just a big number

from BasePlayer import BasePlayer

class ScoutPlayer(BasePlayer):
    def __init__(self, id=None):
        super(ScoutPlayer, self).__init__(id)
        self.attack_fleet = {}
        self.counter_fleet = {}
        self.schedule = {}
        self.pw = None
        pass
    
    def update(self, pw):
        self.pw = pw
    
    def setMyStrongest(self):
        source = -1
        source_score = -999999.0
        my_planets = self.pw.MyPlanets()
        for p in my_planets:
            score = float(p.NumShips())
            if score > source_score:
                source_score = score
                source = p
        self.strongest = source
        
    def setWeakestTarget(self):
        dest = -1
        dest_score = -999999.0
        not_my_planets = self.pw.NotMyPlanets()
        for p in not_my_planets:
            score = 1.0 / (1 + p.NumShips())
            if score > dest_score:
                dest_score = score
                dest = p
        self.weakestTarget = dest
        
    def counterFleet(self, fleet):
        if(self.counter_fleet.has_key(fleet.ID())):
            return
        #mark the fleet as spotted
        self.counter_fleet[fleet.ID()] = True
        #what kind of fleet is this?
        dest = fleet.DestinationPlanet()
        if(self.pw.MyPlanets().count(dest) == 1):
            #attacking fleet
            #schedule reinforcements immediately!
            #we will need fleet_size - (turns_remaining * growth) - planet_size
            # to defend.
            #(we'll also tack on some additional ships for safety)
            counter_size = fleet.NumShips() - (fleet.TurnsRemaining() * dest.GrowthRate()) - \
                            dest.NumShips() + SAFETY_SHIPS
            
            if(counter_size <= 0):
                return
            
            if(not self.schedule.has_key(0)): self.schedule[0] = []
            self.schedule[0].append((COUNTER_ATTACK, dest.ID(), counter_size))
            
            
        elif(self.pw.EnemyPlanets().count(dest) == 1):
            #reinforcements!
            pass
        else:
            #expansion fleet
            #we need abs(planet_size - fleet_size) + 1 to arrive on the same 
            #turn as the fleet
            
            pass
    
    def executeOrders(self, orders):
        pri_orders = sorted(orders, key=lambda o: o[0])
        add_to_sched = []
        for order in pri_orders:
            subs_order = self.executeOrder(order)
            if(subs_order):
                add_to_sched.append(subs_order)
        return add_to_sched
    
    def executeOrder(self, order):
        #send order[2] ships from the best available planet to order[1]
        #they must arrive as soon after order[3] turns as possible
        my_planets = self.pw.MyPlanets()
        min_time = 0
        if(len(order) >= 4):
            #the order specifies a minimum travel time
            min_time = order[3]
        best = None
        best_size = 0
        best_dist = REALLY_BIG_NUMBER
        dest = self.pw.GetPlanet(order[1])
        for planet in my_planets:
            size = planet.NumShips()
            if(size < order[2]):
                continue
            if(planet.ID() == dest.ID()):
                continue
            dist = self.pw.Distance(planet, dest)
            if(dist >= min_time):
                #this planet qualifies!
                if(not best or (dist < best_dist and size > best_size)):
                    #this is a better source
                    best = planet
                    best_dist = dist
                    best_size = size
        
        if(not best):
            if(len(order) >= 4): order[3] = order[3] - 1
            return (0, order)
        else:
            #actually do the order
            self.pw.IssueOrder(best.ID(), order[1], order[2])
            return None
        
    def setTargets(self):
        planets = self.pw.NotMyPlanets()
        self.targets = sorted(planets, key= lambda p: p.NumShips() + self.minDistToPlanet(p), reverse=True)
    
    def minDistToPlanet(self, planet):
        best_dist = REALLY_BIG_NUMBER
        for p in self.pw.MyPlanets():
            d = self.pw.Distance(p, planet)
            if(d < best_dist):
                best_dist = d
        
        return best_dist
    
    def DoTurn(self, pw):
        self.update(pw)
        self.setMyStrongest()
        self.setTargets()
        for p in self.pw.MyPlanets():
            if p.NumShips() >= ATTACK_SIZE: 
                #send a fleet out to the weakest planet
                if(not self.schedule.has_key(0)): self.schedule[0] = []
                if(len(self.targets) > 0):
                    targ = self.targets.pop()
                    f = (EXPANSION, targ.ID(), targ.NumShips() + SAFETY_SHIPS)
                    self.schedule[0].append(f)
        
        #sort the list of enemy fleets by (fleet size - target planet size) descending
        eFleets = sorted(pw.EnemyFleets(), key=lambda f:f.NumShips() - 
                         f.DestinationPlanet().NumShips(), reverse=True)
        for fleet in eFleets:
            self.counterFleet(fleet)
        new_orders = []
        for sched in self.schedule.keys():
            if(sched == 0):
                #do these scheduled items
                new_orders.append(self.executeOrders(self.schedule[sched]))
            else:
                self.schedule[sched - 1] = self.schedule[sched]
            del self.schedule[sched]  
        for orders in new_orders:
            for order in orders:
                if(not self.schedule.has_key(order[0])): self.schedule[order[0]] = []
                self.schedule[order[0]].append(order[1])