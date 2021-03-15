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
Stores the collection of configurations that have been tested. Organized by run, which allows us to know the sequence in which configs were used.
"""
import time
from Configurator.Run import Run

#TODO: finish fleshing out, need to store all configs and runs, flag un flag runs
#get passed to updator for updating flags 
#gets passed to model for data extracton 

class ConfigurationDB:
    def __init__(self):
        self.records = dict() 

    def addRun(self, run: Run) -> None:
        prob = run.problem()
        id = run.runConfigID()
        if prob not in self.records:
            self.records[prob] = dict() 

        rcrdsForProblem = self.records[prob]
        if id not in rcrdsForProblem:
            rcrd = Record() 
            rcrdsForProblem[id] = rcrd 
        
        rcrdsForProblem[id].addRun(run) 

    #each run should be identified by a unique id, which increases sequentially as runs are added 
    #that way it possible to find any new data by only grabbing runs with id greater than x

"""
Wraps the information we have about a particular sequence of configurations 
"""
class Record:
    def __init__(self):
        self._runs = [] #the runs that have been performed 
        self._reRun = False #whether or not more runs are required 
        self._desirable = False #whether or not this configuration is "good" compared to the others
        self._updatedAt = int(time.time()*1000000)

    #we use getters and setter shere to ensure that updatedAt is accurage 
    #models will likely be interested in finding records that have been updated since they last view the DB
    #so we need to make it easy to find 'new' records 

    def addRun(self, run: Run) -> None:
        self._runs.append(run)
        self._updatedAt = int(time.time()*1000000)

    def getRuns(self) -> list[Run]:
        return self._runs

    def reRun(self, val:bool) -> None:
        self._reRun = val 
        self._updatedAt = int(time.time()*1000000)

    def reRun(self) -> bool:
        return self._reRun 

    def desirable(self, val:bool) -> None:
        self._desirable = val 
        self._updatedAt = int(time.time()*1000000)

    def desirable(self) -> bool:
        return self._desirable 