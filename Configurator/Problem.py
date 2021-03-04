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
    def __init__(self, name, flag):
        self.name = name 
        self.flag = flag 

    def toFlags(self):
        return self.flag

"""
Represents a specific instance of a problem 
"""
class Instance:
    def __init__(self, problem, instanceData):
        self.problem = problem 
        self.instanceData = instanceData 

    def toFlags(self):
        return "{0} {1}".format(self.problem.toFlags(), self.instanceData)