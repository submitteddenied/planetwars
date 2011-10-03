'''
Created on 01/07/2011

@author: Michael
'''
from Location import Location

class Entity(object):
    '''
    An abstract class representing something in the game world.
    At the time of writing, this is either a fleet or a planet.
    '''

    def __init__(self, x, y, id, numships, owner_id):
        #super(Entity, self).__init__(x, y)
        self._location = Location(x, y)
        self._id = id
        self._numships = numships
        self._owner = owner_id
        self._vision_age = 99999
    
    def Location(self):
        return self._location
    
    def X(self):
        return self._location.X()
    
    def Y(self):
        return self._location.Y()
    
    def DistanceTo(self, other):
        return self._location.DistanceTo(other.Location())
    
    def ID(self):
        return self._id
    
    def NumShips(self, new_ship_count=None):
        if(new_ship_count != None):
            self._numships = new_ship_count
        return self._numships
    
    def RemoveShips(self, num_ships):
        if(num_ships < 0):
            raise ValueError("Cannot remove a negative number of ships...")
        if(self._numships < num_ships):
            raise ValueError("Asked to remove more ships than are present!")
        self._numships = self._numships - num_ships
        
    def AddShips(self, num_ships):
        if(num_ships < 0):
            raise ValueError("Cannot add a negative number of ships...")
        self._numships = self._numships + num_ships
    
    def Owner(self, new_owner_id=None):
        if(new_owner_id != None):
            self._owner = new_owner_id
        return self._owner
    
    def VisionRange(self):
        raise NotImplementedError("This method cannot be called on this 'abstract' class")
    
    def Tick(self):
        raise NotImplementedError("This method cannot be called on this 'abstract' class")
    
    def IsInVision(self):
        return self.VisionAge() == 0
    
    def VisionAge(self, age=None):
        if age != None:
            self._vision_age = age
        
        return self._vision_age
    
    def GetInRange(self, list):
        '''Returns a map of entities that are within vision range of this entity.
        Argument: list - A list of Entities
        Returns: {id : entity}'''
        inview = {}
        for p in list:
            #is p in range of my_planet?
            if (self.DistanceTo(p) <= self.VisionRange()):
                inview[p.ID()] = p
        
        return inview