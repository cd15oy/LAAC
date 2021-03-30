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
from typing import Iterator, List
from Configurator.Run import Run

#TODO: We want to store up to N runs from the top X percent of observed runs. Basically we hope that through the first random, but progressively more targeted sampling we do, we'll end up with a variety of configurations which produced strong performance and obviously, as time goes on we should collect more and more runs. We want to limit the total amount of data we hold on to though, so instead we need to store the quality of the Xth best run for each problem, then any runs with better (or maybe close) quality can be kept. Once the total number of stored runs reachs/exceeds N we can start also deleteing random/or the worse stored runs to make room for new examples.
#strat: store the total number of runs consider over all time, and store the actual position of the Xth best. Anything worse than the Xth best can just be dropped after we updated the total runs count 
#anything better than the xth best can be kept, but we need to update the total count, and the estimated position of the xth best relative to all considered runs
#ex, if we find a new run better than the xth best, then the position of the xth best should move down by 1 
#Once we have N stored runs, we can just assume our threshold value is sufficient/does not need to be updated 
#after that we can replace a random store run with any new run which is better than our threshold
#alternatively, we could replace the worst and update the threshold
#or just replace random runs among the 50% worse stored runs 
##this option means we're still storing the N/2 best runs we EVER observed, but also a random sampling of "good" runs, sounds like a nice balance between exploration and exploitation
#BEFORE you spend a lot of time on this, try deleting the stored solutions/states first, since we don't need them after calculating characteristics
#though regardless we still need to update this to avoid walking the entire DB of stored runs over and over

#TODO: finish fleshing out, need to store all configs and runs, flag un flag runs
#get passed to updator for updating flags 
#gets passed to model for data extracton 

#TODO: Once this is somewhat finalized re-write it for efficency
#need to store the config db on disk probably
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

        #Set rerun to false, since we're adding a new run 
        rcrdsForProblem[id].reRun(False)

    #produces a list of configurations which have been flagged for an additional run
    def getReRuns(self) -> List[Run]:
        ret = [] 
        for prob in self.records:
            for rcrd in self.records[prob]:
                if self.records[prob][rcrd].reRun():
                    ret.append(rcrd[0])

    def recordGenerator(self) -> Iterator["Record"]:
        for prob in self.records:
            for rcrd in self.records[prob]:
                yield self.records[prob][rcrd]
    #TODO: need to provide efficient ways for model, evaluator, etc to scan/retrieve relevent records

"""
Wraps the information we have about a particular sequence of configurations 
"""
class Record:
    def __init__(self):
        self._runs = [] #the runs that have been performed 
        self._reRun = False #whether or not more runs are required 
        self._desirable = False #whether or not this configuration is "good" compared to the others
        self._updatedAt = int(time.time()*1000000)

    #we use getters and setter shere to ensure that updatedAt is accurate 
    #models will likely be interested in finding records that have been updated since they last view the DB
    #so we need to make it easy to find 'new' records 

    def addRun(self, run: Run) -> None:
        self._runs.append(run)
        self._updatedAt = int(time.time()*1000000)

    def getRuns(self) -> List[Run]:
        return self._runs

    def reRun(self, val:bool=None) -> None:
        if val is None:
            return self._reRun 
        else:
            self._reRun = val 
            self._updatedAt = int(time.time()*1000000)


    def desirable(self, val:bool=None) -> None:
        if val is None:
            return self._desirable 
        else:
            self._desirable = val 
            self._updatedAt = int(time.time()*1000000)

    def updatedAt(self):
        return self._updatedAt