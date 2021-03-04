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
class Problem:
    def __init__(self, name, flag, instances):
        self.instanceTemplates = instances
        self.name = name 
        self.flag = flag 

    #produces the flags needed by the aglorithm to use the problem 
    def toFlags(self):
        return self.flag

    #get n instances chosen uniformly at random from existing instances (with replacement) 
    def sampleInstances(self, n):
        pass 
    
    #generate a concrete instance from the template 
    #if the instance is a static set of flags, it is returned as is, otherwise any keywords are replaced as needed. ex $RANDOM is replaced with a seed 
    def _parseTemplate(self, template):
        pass 
"""
Represents a specific instance of a problem 
"""
class Instance:
    def __init__(self, problem, instanceData):
        self.problem = problem 
        self.flags = instanceData 

    def toFlags(self):
        return "{0} {1}".format(self.problem.toFlags(), self.flags)