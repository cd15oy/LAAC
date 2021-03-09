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

#TODO: LAAC should have an "evaluate invalid configurations" option, if False, invalids get an impossibly bad quality, otherwise run them and get a quality

class Algorithm:

    def __init__(self, wrapperCall: str, staticArgs: str, evaluateInvalid:bool=False) -> None:
        self.wrapperCall = wrapperCall 
        self.staticArgs = staticArgs
        self.evaluateInvalid = evaluateInvalid
        
   

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

        conf = initialConfig
       
        while not terminationCondition.terminate(theRun):

            #If the configuration is invalid, and LAAC should not evaluate invalid configs 
            if not conf.valid and not self.evaluateInvalid:
                #construct a dummy record with None features, solutions, etc 

                

                features = None  #no features 
                result =    {
                                "solutions":
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
                features = np.array([])#features = characterizer.characterize(result)
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


