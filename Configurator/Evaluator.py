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

from statistics import mean 
from Configurator.ConfigurationDB import ConfigurationDB
from time import time
from bisect import bisect

"""
Responsible for examining and providing a relative evaluation of the configurations in a ConfigurationDB. Configurations representing desirable performance will be flagged. Some configurations may also be flagged to indicate more information is required. 

A Record in a ConfigurationDB has two main flags that an Evaluator needs to care about. desirable, and reRun. desirable indicates that the configuration is desirable, that it would be good if newly generated configurations had similar or better performance. reRun is set to True if the evaluator would like to have more runs of the configuration 
"""

#TODO tests 

#All we need is an evaluate method which will process the ConfigurationDB, and update the records 
class Evaluator:
    def evaluate(self, configDB:ConfigurationDB) -> None :
        raise NotImplementedError

#Simple, inefficent, evaluator implementation which provides static rules for when/when not to re-run, and for which configurations are desirable 
class SimpleEvaluator(Evaluator):

    def __init__(self, x:float=0.25, reRun:bool=False, maxRunsPerConfig:int=30):
        self.x = x 
        self.reRun = reRun
        self.maxRunsPerConfig = maxRunsPerConfig
        self._qualities = dict()
        self._updatedAt = 0

    def evaluate(self, configDB:ConfigurationDB) -> None :
        self._topX(configDB, self.x) 

        if self.reRun:
            self._alwaysReRun(self.maxRunsPerConfig, configDB)
        else: 
            self._neverReRun(configDB)

    #classifies a run as desirable if it's quality falls with the top x percent for that problem 
    #x should be a float in [0,1] where 0 will only use the best configuration for each problem, and 1 will use all configurations
    def _topX(self, configDB:ConfigurationDB, x:float) -> None:

        tme = self._updatedAt 
        rcrds = configDB.getNew(self._updatedAt)
        for rcrd in rcrds:
            
            #keep track of the newest record observed 
            if rcrd.updatedAt() > tme:
                tme = rcrd.updatedAt() 

            #create the quality list if needed 
            prob = rcrd.problem()
            if prob not in self._qualities:
                self._qualities[prob] = ([],[])

            #grab the list and pre-compute a list  of keys 
            quals = self._qualities[prob][0]
            keys = self._qualities[prob][1]

            #check if the record is present, remove if needed 
            for i,val in enumerate(quals):
                if val["id"] == rcrd.id():
                    del quals[i] 
                    del keys[i]

            #create an updated dict for the record, and insert 
            # val = {"id":rcrd.id(),"quality":mean([x.quality() for x in rcrd.getRuns()])}
            val = {"id":rcrd.id(),"quality":mean(rcrd.qualities())}

            #find position to insert to 
            idx = bisect(keys, val["quality"]) 

            #insert back into the list 
            keys.insert(idx, val["quality"])
            quals.insert(idx, val)

            if idx/len(keys) <= self.x:
                rcrd.desirable(True)
            else:
                rcrd.desirable(False)
        
        #finally, record the time of the newest observed record 
        self._updatedAt = tme 


            

        # for problem in configDB.problemGenerator():
        #     records = []
        #     for record in problem:
        #         runs = record.getRuns() 
        #         quality = mean([x.quality() for x in runs])
        #         records.append((quality, record))
        #     records.sort(key=lambda x : x[0]) 
        #     cutOff = records[int(len(records)*x)][0] 

        #     for record in records:
        #         if record[0] <= cutOff:
        #             record[1].desirable(True)
        #         else:
        #             record[1].desirable(False)  


    #these two methods represent the two extremes for when to or not to re-run a configuration 

    #never runs more than the minimum request runs for any config 
    def _neverReRun(self, configDB:ConfigurationDB) -> None:
        pass 

    #always asks for more runs of a desirable configuration, until the maximum number of runs per configuration is reached 
    def _alwaysReRun(self, maxRunsPerConfig:int, configDB:ConfigurationDB) -> None:
        #TODO: this can be much cheaper
        for problem in configDB.problemGenerator():
            for record in problem:
                if record.desirable():
                    if len(record.getRuns()) < maxRunsPerConfig:
                        record.reRun(True)
                    else:
                        record.reRun(False)

#TODO: need a new/better evaluator
#new version should only consider the runs associated with a particular initial config 
#the top X percent runs of that inital config should be considered desirable 
#ie the goal of the model is, given some set of features, predict a new config which continues the search in the best possible manner
#so even if the initial config was bad, we hope the model can make the best of it 
#this has several benefits, the main one will be that the bottle neck during the evaluation step is removed. The evaluator only needs to consider new records, and any records that have changed, rather than walk EVERY run of EVERY problem in the DB. 
#This approach also should help relieve any issues resulting from minimal data,
####ie the top X records per problem really only provides usefull information when you have a few hundred records per problem, which means theres a huge overhead, delay while waiting for the inital data, a very long wait before seeing any results at all 
######## ex if the inital collection of data is too small, ie 1 or 2 records per problem, then the training data is small, the model may over fit really early
####with this approach 5 runs of a handful of configs for each problem leads to a large early collection of data so training can begin with less risk of overfitting 
#This dovetails well with the model (no feature) config selection mechanism, which randomly selects a previously used desirable initial config 
####The model initial config selection code can be updated to prefer configs/records whose average performanc is strong, which will over time bias the search toward strong solutions
########Which should balance out the potential downfall of this evaluator appprach 
########ie it could be argued that this approach attempts to train the model to make the best of what it's given (which may be bad anyway), whereas the old approach was focused on obtain good performance when good inputs were provided 
########### the thing is, the seed configs were still mostly random in the old appraoch, with some bias toward the good configs found 
########### so technically the data we were training the model on, was not very representative of the data it was being given in pratice 
############### anywho, neither approach is perfect, but the new one resolves some of the exists issues/bottle necks, and we can make a convincing argument that it makes sense.
