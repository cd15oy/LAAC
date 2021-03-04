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
problems =  {"problems":[                           #here we just need a list of problems, under the key "problems"
                    {   "name":"f1",
                        "flag":"-p f1",
                        #here we need  a list of instances which can be used
                        #This can be a finite list of instances. The $RANDOM keyword can be used to indicate that LAAC should generate a random seed 
                        #when that particular instance is used 

                        "instances": [
                            "-pSeed $RANDOM"     
                        ]
                    },
                    {   "name":"f2",
                        "flag":"-p f2",
                        "instances": [                
                            "-pSeed $RANDOM"                   
                        ]
                    }
                ]   
            }

#Configurations

#Scenario
scenario =  {
                "scenario":{
                                "problemDefs":"optFiles/problems.json" #The location of the problem definition file 
                            }
            }

#TODO: configuration validator 

with open("optFiles/problems.json", 'w') as outF:
    outF.write(json.dumps(problems,indent=2))