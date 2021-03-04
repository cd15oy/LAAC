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
This class represents a Configuration. That is, a set of hyper parameters used with the optimizer and all data collected about the optimizer and the use of those parameters. 
"""

class Configuration:
    def __init__(self):
        self.features = None 
        self.rawResult = None 
        self.seed = None #Note this is the algorithm seed, it is specific to this execution of the algorihtm. This is not the instance seed (if it exists)
        self.threadID = None
        pass

    #Produces a string of command line arguments which can be passed on to Algorithm
    def toFlags(self):
        pass 

