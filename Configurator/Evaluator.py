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

    def evaluate(self, configDB:ConfigurationDB) -> None :
        #TODO: need to prune clearly bad configs
        self._topX(configDB, self.x) 

        if self.reRun:
            self._alwaysReRun(self.maxRunsPerConfig, configDB)
        else: 
            self._neverReRun(configDB)

    #TODO: when performance matters we'll need to do a random sample of configurations, and estimate quantiles from that 
    #classifies a run as desirable if it's quality falls with the top x percent for that problem 
    #x should be a float in [0,1] where 0 will only use the best configuration for each problem, and 1 will use all configurations
    def _topX(self, configDB:ConfigurationDB, x:float) -> None:
        for prob in configDB.records:
            records = []
            for rcrd in configDB.records[prob]:
                record = configDB.records[prob][rcrd]
                runs = record.getRuns() 
                quality = mean([x.configurations[-1].rawResult["solutions"][-1]["quality"] for x in runs])
                records.append((quality, record))
            records.sort() 
            cutOff = records[int(len(records)*x)][0] 

            for record in records:
                if record[0] <= cutOff:
                    record[1].desirable(True)
                else:
                    record[1].desirable(False)  


    #these two methods represent the two extremes for when to or not to re-run a configuration 

    #never runs more than the minimum request runs for any config 
    def _neverReRun(self, configDB:ConfigurationDB) -> None:
        pass 

    #always asks for more runs of a desirable configuration, until the maximum number of runs per configuration is reached 
    def _alwaysReRun(self, maxRunsPerConfig:int, configDB:ConfigurationDB) -> None:
        for prob in configDB.records:
            for rcrd in configDB.records[prob]:
                record = configDB.records[prob][rcrd]
                if record.desirable():
                    if len(record.getRuns()) < maxRunsPerConfig:
                        record.reRun(True)
                    else:
                        record.reRun(False)