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

from Configurator.ConfigurationDefinition import ConfigurationDefinition
from Configurator.ConfigurationDB import ConfigurationDB
import threading
from numpy import ndarray
from random import Random

#TODO: all testing

""" 
This class defines a method for selecting the "next" configuration to be used with the algorithm
"""
class Model:

    #One model may be shared among multiple workers which are waiting on results from the target algorithm 
    #Since models may be statefull, we need to ensure that only one worker is able to use the model at a time, thus Locking is required
    def __init__(self):
        self.lock = threading.Lock()

    #This method should return a dictionary where the keys are the parameter names and the values are the parameter values
    def generate(self, features:ndarray) -> dict:
        self.lock.acquire() 
        config = self._generate(features) 
        self.lock.release() 
        return config

    #Model implementations must implement this method to be used by LAAC
    def _generate(self, features:ndarray) -> dict:
        raise NotImplementedError
    
    #LAAC will provide the configurationDb to the model
    #the ConfigurationDB will contain information about the tested configurations, the runs performed with them, and which configurations respresent desirable output 
    #update is responsible for selecting useful information from the DB, and updating the model to produce better predictions
    def update(self, configs:ConfigurationDB) -> None:
        raise NotImplementedError

#purely random configuration sampling
#TODO: tests
class LatinHyperCube(Model):
    def __init__(self, bufferSize:int, configDef:ConfigurationDefinition, seed:int):
        super(LatinHyperCube, self).__init__() 
        self.configs = [] 
        self.configDef = configDef 
        self.bufferSize = bufferSize
        self.rng = Random(seed) 

    #this is a purely random sampler, no updating is possible
    def update(self, configs:ConfigurationDB) -> None:
        pass 


    #Simple latin hyper-cube sampling
    def _generate(self, features:ndarray) -> dict:

        #If needed generate a new random sample 
        if len(self.configs) == 0:
            #generate a sample of bufferSize for each param
            paramSamples = []

            for param in self.configDef.parameters:
                if param.type == "real":
                    vals = self.__generateReals(self.bufferSize, param.lower, param.upper)
                elif param.type == "integer":
                    vals = self.__generateInts(self.bufferSize, param.lower, param.upper)
                elif param.type == "categorical":
                    vals = self.__generateCategorical(self.bufferSize, param.options)

                paramSamples.append([(param.name,x) for x in vals]) 

            #param samples is a list of lists of random samples for each parameter
            #each sublist was shuffled by the generate functions 

            #now we just zip them up to create new random configs
            tmpConfs = zip(*paramSamples) 
            for tmpConf in tmpConfs:
                conf = dict() 
                for param in tmpConf:
                    conf[param[0]] = param[1] 
                self.configs.append(conf) 
            
        return self.configs.pop()

    def __generateReals(self, n:int, lower:float, upper:float) -> list[float]:
        binWidth = (upper - lower)/n
        vals = [] 

        l = lower 
        for i in range(n):
            vals.append((self.rng.random()*binWidth) + l) 
            l += binWidth 

        self.rng.shuffle(vals) 
        return vals

    def __generateInts(self, n:int, lower:int, upper:int) -> list[int]:
        return [int(x) for x in self.__generateReals(n, lower, upper)]

    def __generateCategorical(self, n:int, choices:list[str]):
        vals = [choices[x%len(choices)] for x in range(n)]
        self.rng.shuffle(vals)

        return vals 


#TODO: NN backed model 