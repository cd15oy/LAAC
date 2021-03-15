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
Wraps the information defining a run 
"""

from Configurator.Problem import Instance
import time 

class Run:
    
    def __init__(self, instance: Instance) -> None:
        #The problem instance on which this run was performed 
        self.instance = instance

        #The configurations used in the run
        self.configurations = [] 

        self.performedAt = int(time.time()*1000000)

    #produces a unique identifier corresponding to the problem 
    def problem(self) -> int:
        return self.instance.problem.toFlags().__hash__()

    #produces a unique identifier corresponding to the sequence of parameter values used in this run 
    def runConfigID(self) -> int:
        configs = [x.toFlags() for x in self.configurations]
        return "".join(configs).__hash__()