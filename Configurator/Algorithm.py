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
This class represents the target algorithm. 
"""

from Configurator.ConfigurationGenerator import ConfigurationGenerator
from Configurator.Model import Model
from Configurator.ConfigurationDefinition import Configuration  
from Configurator.Run import Run 
from Configurator.Problem import Instance
from Configurator.TerminationCondition import TerminationCondition
from Configurator.Characterizer import Characterizer
from subprocess import Popen, PIPE
import json
from random import Random
import numpy as np
import copy

#TODO: LAAC should have an "evaluate invalid configurations" option, if False, invalids get an impossibly bad quality, otherwise run them and get a quality

class Algorithm:

    def __init__(self, wrapperCall: str, staticArgs: str, evaluateInvalid:bool=False) -> None:
        self.wrapperCall = wrapperCall 
        self.staticArgs = staticArgs
        self.evaluateInvalid = evaluateInvalid
    
    #Re-run the sequence of configurations contained in run using instance, and produce a new run 
    def rerun(self,instance:Instance, run:Run, characterizer: Characterizer, threadID:int, runSeed:int) -> Run:
        #READMEWEDNESDAY
        # So, I think I may be miss-representing a run here 
        # the purpose of doing multiple runs on multiple seeds is getting a decent estimate of performance
        #     since we don't know what seed/initial config the algorithm has when a user actually runs it, we want some picture of how a config does over multiple instances/seeds 

        # However, LAAC will use multiple/many configs a different points throughout the run 
        #     the results obtained from one config, directly influence the next config chosen 
        #         (if not random) 
        # In this situation statically rerunning a previous sequence of configs does not make sense
        #     doing so implicitly assumes that the initial config will deterministically lead to whatever the next config is 
        #         but that't not necessarily true 
        #     the initial config run on a different seed could produce different characteristics, and thus lead to a different second config 

        # re-running a static sequence of configs gives us information on how that static sequence performs on average
        #     but that information is useless, we don't intent to provide that static sequence as a solution 
        #     it will only be used again in practice if the model produces it again at run time for some other seed 

        # SO, if the model produces the same sequence of configs for multiple seeds (and the same initial confg) on a probelm, thats fine 
        #     re-running with different seeds actually tells us about the solutions the system will obtain 

        # BUT if the model does not reproduce the same sequence on its own 
        #     we need to know about the average performance of the sequences it produces for that initial config 
        #         not the average performance of some specific sequence that came from that inital config 

        #The point is, re-running is silly

    #note, termination condition needs to come from above, 
    #its possible that we will produce cases which stagnate for a while, then see improvement 
    #the specific conditions which indicate time to terminate will need to be adapted based on observation, and specific to different problems 
    #the initial condition will probably a total FE limit 
    def run(self, instance: Instance, initialConfig: Configuration, characterizer: Characterizer, model: ConfigurationGenerator, terminationCondition: TerminationCondition, threadID: int, runSeed: int) -> Run:
        
        rng = Random(runSeed)

        #A Run is simply a list of configurations 
        #Each individual configuration will contain the hyper parameters, and data collected about the algorithm
        theRun = Run(instance) 
        
        restore = "" 

        conf = copy.deepcopy(initialConfig)
       
        while not terminationCondition.terminate(theRun):

            #If the configuration is invalid, and LAAC should not evaluate invalid configs 
            if not conf.valid and not self.evaluateInvalid:
                #construct a dummy record with None features, solutions, etc 

                

                features = None  #no features 
                result =    {
                                "solutions":
                                    [],
                                "state":
                                    [],
                                "evaluationsConsumed":0,
                                "algorithmState":restore,
                                "time":0
                            }
                conf.rawResult = result
                conf.seed = 0
                conf.threadID = threadID 

                # #Store the finished configuration in the run 
                theRun.configurations.append(conf)

                # #Generate the next configuration
                conf = model.generate(features)

            else:

                seed = rng.randint(0,4000000000) #A seed for the execution of the target algorithm

                #construct our command 
                toRun = " ".join([self.wrapperCall, str(threadID), str(seed), self.staticArgs, instance.toFlags(), conf.toFlags(), restore])

                io = Popen(toRun.strip().split(" "), stdout=PIPE, stderr=PIPE)

                #wait for the process to finish 
                _stdout,_stderr = io.communicate() 
                output = _stdout.decode()

                #print(_stderr.decode()) #If you run into issues check out stderr, dont forget to print stderr in the target-algorithm too!

                #We expect everything after RESULTS FOLLOW to be the output for LAAC
                #The output should be properly formatted JSON 
                #TODO: More informative Errors/Exceptions
                #print(output)
                loc = output.find("RESULTS FOLLOW")
                result = json.loads(output[loc + 14:])
                
                #TODO: uncomment and fill in
                # #Finish populating the Configuration with data
                features = characterizer.characterize(result)
                # conf.features = features
                conf.rawResult = result
                conf.seed = seed 
                conf.threadID = threadID 

                # #Store the finished configuration in the run 
                theRun.configurations.append(conf)

                # #Generate the next configuration
                conf = model.generate(features)

            #ensure we pick up where the algorithm left off
            restore = result["algorithmState"]

        return theRun


