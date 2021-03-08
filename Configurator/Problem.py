"""
Landscape Aware Algorithm Configurator
Copyright (C) 2021 Cody Dennis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
A class representing a general problem
"""

from random import Random 
from typing import List

"""
Represents a specific instance of a problem 
"""
class Problem:
    def __init__(self, name:str, flag:str, instances:List[str], seed:int):
        self.rng = Random(seed)
        self.instanceTemplates = instances
        self.name = name 
        self.flag = flag 
        self.instances = set()

    #produces the flags needed by the aglorithm to use the problem 
    def toFlags(self)->str:
        return self.flag

    #get n instances chosen uniformly at random from existing instances (with replacement) 
    def sampleInstances(self, n:int)->List["Instance"]:
        #TODO: choices(list(set)) is inefficent, consider doing something less stupid
        return self.rng.choices(list(self.instances), k=n)
    
    #generate a concrete instance from the template 
    #if the instance is a static set of flags, it is returned as is, otherwise any keywords are replaced as needed. ex $RANDOM is replaced with a random seed 
    def _parseTemplate(self, template:str) -> str:
        #nothing fancy, just a replace for each possible keyword 
        ret = template.replace("$RANDOM", str(self.rng.randint(0,4000000000)))
        return ret  

    #Generate a new instances from a random template
    #The new instance is added to the set of instances 
    def generateInstance(self) -> "Instance":
        rndTemplate = self.rng.choice(self.instanceTemplates)
        instanceString = self._parseTemplate(rndTemplate) 
        instance = Instance(self, instanceString) 
        self.instances.add(instance) 
        return instance 

class Instance:
    def __init__(self, problem:Problem, instanceData:str):
        self.problem = problem 
        self.flags = instanceData 

    def toFlags(self)->str:
        return "{0} {1}".format(self.problem.toFlags(), self.flags)

    def __hash__(self)->int:
        return self.toFlags().__hash__()

    def __eq__(self, other:"Instance") -> bool:
        return self.__hash__() == other.__hash__()

    def __ne__(self, other:"Instance") -> bool:
        return self.__eq__(other) == False 
