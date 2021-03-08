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
This file defines conditions for terminating a run. A termination condition is a class with a .terminate([Configuration]) method. This allows a termination condition to have an internal state. It may be favorable to adjust the conditions for termination based on our observations while attempting to configure the algorithm. For this to be possible a termination condition will require state. 
"""

from Configurator.Run import Run

#Not really needed with python, but I think including it makes things clearer 
class TerminationCondition:
    def terminate(self, runs: Run) -> bool:
        pass 

#Terminate the run once a set number of FEs are consumed
class FELimit(TerminationCondition):
    def __init__(self, limit: int) -> None:
        self.limit = limit 

    def terminate(self, run):
        
        total = 0 
        for conf in run.configurations:
            total += conf.rawResult["evaluationsConsumed"]

        if total >= self.limit:
            return True
        else:
            return False
