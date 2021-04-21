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
This file describes and exposes the various LAAC options available to the user. Executing this file will produce the config files needed to run LAAC with the contained parameters. Alternatively, valid config files can be produced or updated manually. Unfortunately JSON doesn't support comments, but its convenient to work with and to write, assuming you don't need comments. This file is used to get around the issue of no comments in JSON 
"""

import json 

#The configuration information is simply written as a python dictionary, which we translate to valid json later 

#Algorithm

#Problems
#We need to explicitly define all of the problems which LAAC will be configuring your algorithm for. 
#For each of those problems we need a name, the flag to pass to the algorithm, and instance definitions 
problems =  {   "problems":
                [                           #here we just need a list of problems, under the key "problems"
                    {   
                        "name":"f1",
                        "flag":"-p f1",
                        #here we need  a list of instances which can be used
                        #This can be a finite list of instances. The $RANDOM keyword can be used to indicate that LAAC should generate a random seed 
                        #when that particular instance is used 

                        "instances": 
                        [
                            "-pSeed $RANDOM"     
                        ]
                    },
                    {   "name":"f2",
                        "flag":"-p f2",
                        "instances": 
                        [                
                            "-pSeed $RANDOM"                   
                        ]
                    }
                ],
                "validation": #A list of problems to use for validation, these problems will not be used to train the internal model
                # This could be the same problems as above, with different instances, or more interestingly a set of new but related problems 
                # Since this is just an example file, we repeat the definitions above 
                [
                    {   
                        "name":"f1",
                        "flag":"-p f1",
                        "instances": 
                        [
                            "-pSeed $RANDOM"     
                        ]
                    },
                    {   "name":"f2",
                        "flag":"-p f2",
                        "instances": 
                        [                
                            "-pSeed $RANDOM"                   
                        ]
                    }
                ]
            }

#Configurations 
parameters =    {   #Each parameter to tune needs a definition in the paremters list 
                    #All definitions need a name, type, flag, and default 
                    #real and integer parameters need a lower and upper 
                    #categorical parameters need a list of options
                    "parameters":    
                    [
                        {
                            "name":"iterations",
                            "type":"integer",
                            "flag":"-i",
                            "default":250,
                            "lower":150,
                            "upper":350
                        },
                        {
                            "name":"samples",
                            "type":"integer",
                            "flag":"-s",
                            "default":5,
                            "lower":1,
                            "upper":10
                        },
                        #For the random search the main parameters to tune are the mean and standard deviation of the sampling distributions of the step sizes for each dimension 
                        #We're going to test the random search on a 5 dimensional problem, so we need to define 10 real parameters ie the mean and standard deviation for each dimension
                        #Note that our random search algorithm does not support options m1, s1, m2, s2, etc target-algorithm.py will need to parse these and construct flags for the random search 
                        {                   
                            "name":"mean1",
                            "type":"real",
                            "flag":"-m1",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std1",
                            "type":"real",
                            "flag":"-s1",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean2",
                            "type":"real",
                            "flag":"-m2",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std2",
                            "type":"real",
                            "flag":"-s2",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean3",
                            "type":"real",
                            "flag":"-m3",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std3",
                            "type":"real",
                            "flag":"-s3",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean4",
                            "type":"real",
                            "flag":"-m4",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std4",
                            "type":"real",
                            "flag":"-s4",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean5",
                            "type":"real",
                            "flag":"-m5",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std5",
                            "type":"real",
                            "flag":"-s5",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean6",
                            "type":"real",
                            "flag":"-m6",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std6",
                            "type":"real",
                            "flag":"-s6",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean7",
                            "type":"real",
                            "flag":"-m7",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std7",
                            "type":"real",
                            "flag":"-s7",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean8",
                            "type":"real",
                            "flag":"-m8",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std8",
                            "type":"real",
                            "flag":"-s8",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean9",
                            "type":"real",
                            "flag":"-m9",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std9",
                            "type":"real",
                            "flag":"-s9",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean10",
                            "type":"real",
                            "flag":"-m10",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std10",
                            "type":"real",
                            "flag":"-s10",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean11",
                            "type":"real",
                            "flag":"-m11",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std11",
                            "type":"real",
                            "flag":"-s11",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean12",
                            "type":"real",
                            "flag":"-m12",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std12",
                            "type":"real",
                            "flag":"-s12",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean13",
                            "type":"real",
                            "flag":"-m13",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std13",
                            "type":"real",
                            "flag":"-s13",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean14",
                            "type":"real",
                            "flag":"-m14",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std14",
                            "type":"real",
                            "flag":"-s14",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean15",
                            "type":"real",
                            "flag":"-m15",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std15",
                            "type":"real",
                            "flag":"-s15",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean16",
                            "type":"real",
                            "flag":"-m16",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std16",
                            "type":"real",
                            "flag":"-s16",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean17",
                            "type":"real",
                            "flag":"-m17",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std17",
                            "type":"real",
                            "flag":"-s17",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean18",
                            "type":"real",
                            "flag":"-m18",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std18",
                            "type":"real",
                            "flag":"-s18",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean19",
                            "type":"real",
                            "flag":"-m19",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std19",
                            "type":"real",
                            "flag":"-s19",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {                   
                            "name":"mean20",
                            "type":"real",
                            "flag":"-m20",
                            "default":0,
                            "lower":-1,
                            "upper":1
                        },
                        {                   
                            "name":"std20",
                            "type":"real",
                            "flag":"-s20",
                            "default":1,
                            "lower":0.01,
                            "upper":2
                        },
                        {
                            "name":"greedy",
                            "type":"categorical",
                            "flag":"-g",
                            "default":"True",
                            "options":["True","False"]
                        }
                    ],
                    #Optionally, you can define constraints which valid configurations must satisfy 
                    #Constrains must evaluate to a boolean, ie True or False, and can use the following operators +,-,/,*,<,>,<=,>=,==,!=,and,or 
                    #& and | refer to logical and and logical or 
                    #Do not assume any particular order of operations. Precedence should be explicitly indicated through the use of open and close parentheses ex 3+4*2 should be written as 3+(4*2) to ensure the multiplication is evaluated first 
                    #Parameters can be refereed to via $name, for example $mean1 refers to the value of mean1 above 
                    #So as an example, you could require that mean1 not equal mean2 via: $mean1 != $mean2
                    #All we need here is a list of strings representing expersions which must evaluate to true for valid combinations of parameters 
                    #of course, these contrains mean nothing, they're just for testing
                    "constraints":
                    [
                        "$mean1 != $mean2",
                        "$std5*$mean4 <= $mean3 and $std4 > 0.1",
                        "($std3 + ($mean2*$mean2))/1.25 >= 1",
                        "($std3 + ($mean2*$mean2))/1.25 <= 5"
                    ]
                }

#Scenario
scenario =  {
                "scenario": {
                                "problemDefs":"optFiles/problems.json",         #The location of the problem definition file 
                                "parameterDefs":"optFiles/parameters.json",    #The location of the the parameter definitions 
                                "runFELimit": 5000,                            #The maximum number of function evaluations which can be consumed by a run of your algorithm
                                "totalFELimit": 1000000,                        #The maximum number of FEs which can be consumed by LAAC 
                                "minRunsPerConfig":1,                           #The minimum number of runs to consider when evaluating a configuration 
                                "maxRunsPerConfig":30,                          #The maximum number of runs to consider when evaluating a configuration 
                                "targetAlgorithm":"python3 target-algorithm.py", #The call to run the target algorithm 
                                "staticArgs":"-d 20",                            #Arguments to be provided to every algorithm call, constant settings  
                                "strictConstraints": False,                     #Influences how strictly constraint expressions in the parameter definition are enforced
                                "configsPerIteration":32,                       #The initial number of configurations to test per iteration of LAAC
                                "threads":4,                                    #Threads to use for algorithm evaluations
                                "dbfile":"resultsdb",                           #The file where tested configurations and their quality will be stored. 
                                "workInMemory":True,                            #If true results will be kept in memory at runtime, and written to disk at the end of the run
                                "modelHistory":"modelHistory.json",             #A summary of the underlying model's performance
                                "modelStoragePath":"models/",                   #A path at which to store model checkpoints
                                "resultsStoragePath":"results/",                #Output from LAAC will be written under this path, existing content will be deleted 
                                "validate":True,                                #Whether or not to perform validation 
                                "countValidationFEs":False,                     #Validation FEs are not counted towards the total since their result is independent of the training process 
                                "modelType":"Adaptive",                     #The type of underlying model used for predicting parametes. <Adaptive or Random>
                                "minInformedPercent":0.05,                  #Three parameters used by the adaptive model influencing how often it's predictions are made randomly
                                "maxInformedPercent":0.95,                  
                                "informedPercentVariance":0.1,
                                "seed":12345                                    #Seed for reproducibility
                            }
            }

#TODO: validate parameter definitions
#TODO: validate problem definitions 


def write():
    with open("optFiles/problems.json", 'w') as outF:
        outF.write(json.dumps(problems,indent=2))
    
    with open("optFiles/parameters.json", 'w') as outF:
        outF.write(json.dumps(parameters,indent=2))

    with open("optFiles/scenario.json", 'w') as outF:
        outF.write(json.dumps(scenario,indent=2))

if __name__ == "__main__":
    write()