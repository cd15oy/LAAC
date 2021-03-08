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

from random import Random
from typing import List 
from Configurator.Problem import Instance, Problem 

"""
A class tracking the problems which LAAC is attempting to tune for 
"""
class ProblemSuite:

    #problemDef is a dict generated from the problem definition JSON 
    def __init__(self, problemDef:dict, seed:int):

        self.rng = Random(seed) 


        #construct a list of the available problems
        self.problems = [] 
 
        for prob in problemDef["problems"]:
            p = Problem(prob["name"], prob["flag"], prob["instances"], self.rng.randint(0,4000000000))
            self.problems.append(p) 
    
    #Generates n new instances from randomly selected problems 
    def generateN(self, n:int) -> List[Instance]:
        sampleProblems = self.rng.choices(self.problems, k=n) 
        instances = [x.generateInstance() for x in sampleProblems] 
        return instances 

    #Samples n random instances from randomly selected problems 
    def sampleN(self, n:int) -> List[Instance]:
        sampleProblems = self.rng.choices(self.problems, k=n) 
        instances = [x.sampleInstances(1) for x in sampleProblems] 
        return instances 
