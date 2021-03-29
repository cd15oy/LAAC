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



#from threading import Thread
from typing import Callable, List, Tuple
from Configurator.Algorithm import Algorithm
from Configurator.Problem import Instance
from Configurator.TerminationCondition import TerminationCondition
from Configurator.ConfigurationDefinition import Configuration
from Configurator.Run import Run
from Configurator.ConfigurationGenerator import ConfigurationGenerator
from random import Random
from Configurator.Characterizer import Characterizer
from Configurator.ProblemSuite import ProblemSuite

from multiprocessing import Process

"""
Runners are responsible for collecting runs of the target algorithm. This involves performing additional runs of existing configurations, as well as obtaining/running new configurations from the model. Runners are responsible for generatin the specific problem instances a configuration is evaluated on and ensuring the data we collect about a configuration provides a reliable description of the configuration.
"""
#TODO: evaluate configurations over a limited pool of instances to reduce variance? 

class Runner:
    def __init__(self, problemSuite:ProblemSuite, characterizer:Characterizer, terminationCondition:TerminationCondition, seed:int, algorithm:Algorithm, threads:int=1):
        self.problems = problemSuite 
        self.characterizer = characterizer 
        self.terminationCondition = terminationCondition
        self.rng = Random(seed) 
        self.algorithm = algorithm
        self.threads = threads

    #configurations should be a list of tuples of (int,Configuration) where the int indicates how many instances should be run for the Configuration
    #runs should be a list of tuples (int,Run) Run is a previously existing Run object. Runner will perform <int> additional runs on new instances of the configuration sequence found in Run 
    #This method must produce a list of tuples (Instance, Configuration), corresponding to a problem instance and initial configuration to provide tothe algorithm 
    def _generateInstances(self, confSampler:ConfigurationGenerator, configurations:List[Tuple[int,Configuration]]=None, runs:List[Tuple[int,Run]]=None) -> List[Tuple[Instance,Configuration]]:
        raise NotImplementedError

    #Performs numInstances runs each for numNewConfigs new configuration sequences and performance an additional run on a new instance for any runs in configsToReRun 
    def schedule(self, manager, numNewConfigs:int, numInstances:int, confSampler:ConfigurationGenerator, configsToReRun:List[Run] = None) -> List[Run]:
        configs = [(numInstances, confSampler.generate()) for x in range(numNewConfigs)]

        reRun = None
        if configsToReRun is not None:
            reRun = [(1,x) for x in configsToReRun] 

        todo = self._generateInstances(configs, reRun) 

        ret = [manager.Array() for x in range(len(todo))] 

        todo = [(inst, conf, self.characterizer, confSampler, self.terminationCondition, self.rng.randint(0,4000000000)) for inst,conf in todo]

        #It seems that the ThreadPool in multiprocessing must attempt to copy arguments or something in memory that should be shared between threads 
        #If we use it, torch throws a segfault, so we just make the threads manually 

        #A wrapper to capture the return value of alg
        def _algWrapper(alg:Callable, args:tuple, out:list):
            out.append(alg(*args))

        threadPool = [Process(target=_algWrapper, args=(self.algorithm.run, x, ret[i])) for i,x in enumerate(todo)]
        for x in range(self.threads):
            threadPool[x].start() 
        for x in range(len(threadPool)):
            threadPool[x].join() 
            nxt = x + self.threads 
            if nxt < len(threadPool):
                threadPool[nxt].start() 

        return [x.pop(0) for x in ret] 
 
    def close(self) -> None:
        self.workers.close()

class RandomInstanceRunner(Runner):
    
    def _generateInstances(self, configurations:List[Tuple[int,Configuration]]=None, runs:List[Tuple[int,Run]]=None) -> List[Tuple[Instance,Configuration]]:
        ret = [] 
        if configurations is not None:
            for x in configurations:
                for y in range(x[0]):
                    ret.append((self.problems.generateN(1)[0], x[1].duplicateParams()))

        if runs is not None:
            for x in runs:
                for y in range(x[0]):
                    ret.append((self.problems.generateN(1, x[1].instance.problem)[0], x[1].configurations[0].duplicateParams()))

        return ret 
       





