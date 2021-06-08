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
from copy import deepcopy
from multiprocessing import Process, Manager

#A wrapper to capture the return value of alg
def _algWrapper(alg:Callable, args:tuple, out:list):
    out.append(alg(*args))

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
    def schedule(self, numNewConfigs:int, numInstances:int, confSampler:ConfigurationGenerator, configsToReRun:List[Run] = None) -> List[Run]:

        configs = [(numInstances, confSampler.generate()) for x in range(numNewConfigs)]

        #TODO: reruns should be update to be a list of configurations
        reRun = None
        if configsToReRun is not None:
            reRun = [(1,x) for x in configsToReRun] 

        todo = self._generateInstances(configs, reRun) 

        manager = Manager() 

        ret = [manager.list() for x in range(len(todo))] 

        samplerState = confSampler.getState()

        todo = [(inst, conf, self.characterizer, deepcopy(samplerState), self.terminationCondition, self.rng.randint(0,4000000000),i) for i,(inst,conf) in enumerate(todo)]

        todo = [Process(target=_algWrapper, args=(self.algorithm.run, x, ret[i])) for i,x in enumerate(todo)]
        running = []

        #My understanding is that a Pool uses a simple message queue to pass args into a new process, and retrieve results 
        #the message queue attempts to pickle everything to make transmission possible, unfortunately some of what we're passing around isn't picklable 
        #on the other hand, using Process directly just forks the current process, which should use copy on write semantics (at least on linux) avoiding the pickablility issue 
        #and still not wasting space (despite what top may report) 
        #I'm not confident that this will behave the same on windows however 
        #TODO: Test this on windows eventually 
        
        while len(todo) > 0 or len(running) > 0:
            stillRunning = []
            while len(running) < self.threads and len(todo) > 0:
                x = todo.pop(0) 
                running.append(x) 
                x.start() 

            for i,x in enumerate(running):
                if x.is_alive():
                    stillRunning.append(x) 
            
            running = stillRunning

        return [x.pop(0) for x in ret] 
 
    def close(self) -> None:
        self.workers.close()

class RandomInstanceRunner(Runner):
    
    #TODO: reruns should be update to be a list of configurations
    def _generateInstances(self, configurations:List[Tuple[int,Configuration]]=None, runs:List[Tuple[int,Run]]=None) -> List[Tuple[Instance,Configuration]]:
        ret = [] 
        if configurations is not None:
            for x in configurations:
                for y in range(x[0]):
                    ret.append((self.problems.generateN(1)[0], x[1].duplicateParams()))

        if runs is not None:
            for x in runs:
                for y in range(x[0]):
                    ret.append((self.problems.generateN(1, self.problems.getProblemFromFlags(x[1].instance.problem))[0], x[1].configurations[0].duplicateParams()))

        return ret 
       





