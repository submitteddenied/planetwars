'''
Predicting Player Class

@author: Michael Jensen
'''
from BasePlayer import BasePlayer
from collections import namedtuple, deque

class PredictingPlayer(BasePlayer):
    '''
    Predicting player keeps track of what it thinks the enemy would do...
    '''
    
    Model = namedtuple('Model', ['planets', 'fleets'])
    Plan = namedtuple('Plan', ['turn', 'plan_id', 'source', 'dest', 'num_ships'])
    SCOUT_FLEET_SIZE = 1
    MIN_SHIPS = 25
    
    
    def __init__(self):
        super(PredictingPlayer, self).__init__()
        self.model = self.Model({}, {})
        self.scout = None
        self.attacks = {}
        self.plans = deque()
        self._plan_id = 0
    
    def plan_id(self):
        self._plan_id += 1
        return self._plan_id
    
    def committed_ships(self, pw, planet):
        result = 0
        for plan in self.plans:
            if plan.source == planet.ID():
                result += plan.num_ships
        
        for fleet in self.model.fleets.values():
            if fleet.Owner() != pw.PlayerID():
                result += fleet.NumShips()
                
        return result
    
    def available_ships(self, pw, planet):
        result =  pw.GetPlanet(planet.ID()).NumShips() - self.committed_ships(pw, planet)
        if result < 0:
            return 0
        else:
            return result
    
    def invalidate_plans(self, pw, planfilter):
        '''
        Invalidates all the plans that match planfilter(plan)
        '''
        self.plans = deque(filter(lambda i: not planfilter(i), self.plans))
    
    def update_model(self, pw):
        for planet in pw.Planets():
            if planet.IsInVision():
                if self.model.planets.has_key(planet.ID()) and planet.Owner() != pw.PlayerID():
                    #if there are more planets there than I expected,
                    #invalidate any plans that had this planet as a target
                    model_planet = self.model.planets[planet.ID()]
                    growth = 0 if model_planet.Owner() == pw.NEUTRAL_PLAYER else model_planet.GrowthRate() 
                    if planet.NumShips() > model_planet.NumShips() + growth:
                        self.invalidate_plans(pw, lambda p: p.dest == planet.ID())
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
            if not self.model.fleets.has_key(fleet.ID()):
                #this is a newly spotted fleet! May need to invalidate plans...
                self.invalidate_plans(pw, lambda p: p.source == fleet.DestinationPlanet().ID()) 
            self.model.fleets[fleet.ID()] = fleet
            
        for target, fleet in self.attacks.items():
            if pw.GetFleet(fleet) is None:
                del self.attacks[target]
    
    def best_source(self, target, pw, desired_ships=1):
        #find the best source that has at least desired_ships + 1 on it
        #let's just assume best = closest
        closest = None
        closest_dist = 999999
        for planet in pw.MyPlanets():
            if planet == target:
                continue
            dist = planet.DistanceTo(target)
            if dist < closest_dist and self.available_ships(pw, planet) > desired_ships:
                closest = planet
                closest_dist = dist
        return closest
    
    def get_scout_target(self, pw):
        target = None
        if len(pw.EnemyPlanets()) == 0:
            return pw.MyPlanets()[0]
        for planet in pw.EnemyPlanets():
            if not target:
                target = planet
            else:
                if target.VisionAge() < planet.VisionAge():
                    target = planet
        return target
    
    def get_attack_target(self, pw):
        target = None
        target_strength = 99999
        for planet in pw.NotMyPlanets():
            if self.attacks.has_key(planet.ID()):
                continue
            strength = 0
            best_source = self.best_source(planet, pw)
            if best_source is None:
                continue
            if planet.Owner() != pw.NEUTRAL_PLAYER:
                strength = best_source.DistanceTo(planet) * planet.GrowthRate()
            strength += planet.NumShips()
            if strength < target_strength:
                target = planet
                target_strength = strength
            if strength == target_strength:
                other_source = self.best_source(target, pw)
                if other_source is None or best_source is None:
                    continue
                if other_source.DistanceTo(target) < best_source.DistanceTo(planet):
                    target = planet
                    target_strength = strength
        
        return (target, target_strength)
    
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
        if scout.DestinationPlanet().Owner() == pw.PlayerID():
            return
        if scout.TurnsRemaining() == 1:
            target = self.get_scout_target(pw)
            self.scout = pw.IssueOrder(scout, target, self.SCOUT_FLEET_SIZE)
            
    def make_attack_plan(self, target, pw):
        sources = pw.MyPlanets()
        sources.sort(key=lambda p: p.DistanceTo(target))
        required = target.NumShips()
        plan = []
        for planet in sources:
            if planet.NumShips() < self.MIN_SHIPS:
                continue
            attack_size = self.available_ships(pw, planet) / 2
            if attack_size <= 0:
                continue
            if required < attack_size:
                attack_size = required + 1
            required -= attack_size
            plan.append((planet, attack_size))
            if required <= 0:
                break
            
        if required > 0:
            return
        
        plan.reverse()
        #send the first one straight away, then schedule the rest
        first_step = pw.CurrentTick()
        max_dist = plan[0][0].DistanceTo(target)
        plan_id = self.plan_id()
        for step in plan:
            planet = step[0]
            wait = max_dist - planet.DistanceTo(target)
            self.plans.append(self.Plan(first_step + wait, plan_id, planet.ID(), target.ID(), step[1]))
        #we've modified self.plans, so we have to resort it
        self.plans = deque(sorted(self.plans, key=lambda i: i.turn))
    
    def send_attack(self, pw):
        target, target_strength = self.get_attack_target(pw)
        if target:
            source = self.best_source(target, pw, target_strength + 1)
            if source:
                #self.attacks[target.ID()] = pw.IssueOrder(source, target, target_strength + 1)
                self.plans.append(self.Plan(pw.CurrentTick(), self.plan_id(), source.ID(), target.ID(), target_strength + 1))
            else:
                #can't make the attack with one, try with > 1
                self.make_attack_plan(target, pw)
    
    def launch_planned_attacks(self, pw):
        while len(self.plans) > 0 and self.plans[0].turn <= pw.CurrentTick():
            #issue this planned order
            plan = self.plans.popleft()
            if pw.GetPlanet(plan.source).NumShips() >= plan.num_ships:
                self.attacks[plan.dest] = pw.IssueOrder(plan.source, plan.dest, plan.num_ships)
            
    
    def DoTurn(self, pw):
        #update my model
        self.update_model(pw)
        
        #do some scouting
        if self.scout == None or pw.GetFleet(self.scout) == None:
            self.send_scout(pw)
        else:
            self.update_scout(pw)
            
        
        #launch an attack
        self.send_attack(pw)
        
        #process any plans
        self.launch_planned_attacks(pw)