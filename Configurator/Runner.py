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



from Configurator.Algorithm import Algorithm
from Configurator.Problem import Instance
from Configurator.TerminationCondition import TerminationCondition
from Configurator.ConfigurationDefinition import Configuration
from Configurator.Run import Run
from Configurator.ConfigurationGenerator import ConfigurationGenerator
from random import Random
from Configurator.Characterizer import Characterizer
from Configurator.ProblemSuite import ProblemSuite
"""
Runners are responsible for collecting runs of the target algorithm. This involves performing additional runs of existing configurations, as well as obtaining/running new configurations from the model. Runners are responsible for generatin the specific problem instances a configuration is evaluated on and ensuring the data we collect about a configuration provides a reliable description of the configuration.
"""
#TODO: evaluate configurations over a limited pool of instances to reduce variance? 

class Runner:
    def __init__(self, problemSuite:ProblemSuite, characterizer:Characterizer, terminationCondition:TerminationCondition, seed:int, algorithm:Algorithm):
        self.problems = problemSuite 
        self.characterizer = characterizer 
        self.terminationCondition = terminationCondition
        self.rng = Random(seed) 
        self.algorithm = algorithm

    #configurations should be a list of tuples of (int,Configuration) where the int indicates how many instances should be run for the Configuration
    #runs should be a list of tuples (int,Run) Run is a previously existing Run object. Runner will perform <int> additional runs on new instances of the configuration sequence found in Run 
    #This method must produce a list of tuples (Instance, Configuration), corresponding to a problem instance and initial configuration to provide tothe algorithm 
    def _generateInstances(self, confSampler:ConfigurationGenerator, configurations:list[tuple[int,Configuration]]=None, runs:list[tuple[int,Run]]=None) -> list[tuple[Instance,Configuration]]:
        raise NotImplementedError

    #Performs numInstances runs each for numNewConfigs new configuration sequences and performance an additional run on a new instance for any runs in configsToReRun 
    def schedule(self, numNewConfigs:int, numInstances:int, confSampler:ConfigurationGenerator, configsToReRun:list[Run]):
        configs = [(numInstances, confSampler.generate()) for x in range(numNewConfigs)]
        reRun = [(1,x) for x in configsToReRun] 

        todo = self._generateInstances(configs, reRun) 

        runs = [] 
        #TODO: replace this with a thread pool
        for inst,conf in todo:
            run = self.algorithm.run(inst, conf, self.characterizer, confSampler, self.terminationCondition, 0, self.rng.randint(0,4000000000))
            runs.append(run) 

        return runs

        

class RandomInstanceRunner(Runner):
    def _generateInstances(self, configurations:list[tuple[int,Configuration]]=None, runs:list[tuple[int,Run]]=None) -> list[tuple[Instance,Configuration]]:
        ret = [] 
        for x in configurations:
            for y in range(x[0]):
                ret.append((self.problems.generateN(1), x[1].duplicate())

        #TODO: add (instance,config) pairs for the reruns
        #but remember, we just need the inital config from the run, see the comments in algorithm.rerun for why full reruns are silly




#TODO: uses Algorithm to perform runs, we want algorithm.run to be called in a separate thread 
#TODO: needs a ConfigurationSampler, and a LandscapeCharacterizer 
#both a required by algorithm to actually perform a run 

#runner just needs to collect all the required runs and pass the data up 


