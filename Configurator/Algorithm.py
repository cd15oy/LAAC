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

from Configurator.Configuration import Configuration 
from Configurator.Run import Run 
from subprocess import Popen, PIPE
import json
from random import seed, randint as setSeed, randint
class Algorithm:

    def __init__(self, wrapperCall, staticArgs):
        self.wrapperCall = wrapperCall 
        self.staticArgs = staticArgs
        
   

    #note, termination condition needs to come from above, 
    #its possible that we will produce cases which stagnate for a while, then see improvement 
    #the specific conditions which indicate time to terminate will need to be adapted based on observation, and specific to different problems 
    #the initial condition will probabably a total FE limit 
    def run(self, instance, initialConfig, characterizer, sampler, terminationCondition, threadID, runSeed):
        
        setSeed(runSeed)

        #A Run is simply a list of configurations 
        #Each individual configuration will contain the hyper parameters, and data collected about the algorithm
        theRun = Run(instance) 
        
        restore = "" 

        conf = initialConfig
       
        while not terminationCondition.terminate(theRun):
            seed = randint(0,4000000000) #A seed for the first execution of the target algorihtm

            #construct our command 
            toRun = " ".join([self.wrapperCall, str(threadID), str(seed), self.staticArgs, instance.toFlags(), conf.toFlags(), restore])

            io = Popen(toRun.strip().split(" "), stdout=PIPE, stderr=PIPE)

            #wait for the process to finish 
            _stdout,_stderr = io.communicate() 
            output = _stdout.decode()

            #We expect everything after RESULTS FOLLOW to be the output for LAAC
            #The output should be properly formatted JSON 
            #TODO: More informative Errors/Exceptions
            loc = output.find("RESULTS FOLLOW")
            result = json.loads(output[loc + 14:])
            #print(_stderr.decode()) #If you run into issues check out stderr 

            #Finish populating the Configuration with data
            features = characterizer.characterize(result)
            conf.features = features
            conf.rawResult = result
            conf.seed = seed 
            conf.threadID = threadID 

            #Store the finished configuration in the run 
            theRun.configurations.append(initialConfig)

            #Generate the next configuration
            conf = sampler.generate(features)

            #ensure we pick up where the algorithm left off
            restore = result["algorithmState"]


