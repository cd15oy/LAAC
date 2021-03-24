from random import Random

import numpy as np
from Configurator.Run import Run
from Configurator.ConfigurationDB import ConfigurationDB
from typing import Tuple
from Configurator.ConfigurationDefinition import Configuration, ConfigurationDefinition
from Configurator.ProblemSuite import ProblemSuite
from copy import deepcopy

def getProblemSuite(seed:int) -> Tuple[dict,ProblemSuite]:
    import json 
    with open("test/problems.json", 'r') as inF:
        problemDefs = json.loads(inF.read())
        suite = ProblemSuite(problemDefs, seed) 

    return problemDefs, suite 

def getConfigDef() -> Tuple[dict,ConfigurationDefinition]:
    import json 
    with open("test/parameters.json", 'r') as inF:
        confDefs = json.loads(inF.read())
    configurationDefinition = ConfigurationDefinition(confDefs) 

    return confDefs,configurationDefinition

def getPopulatedConfigDB(seed:int) -> ConfigurationDB:
    _,suite = getProblemSuite(seed)
    instances1 = suite.generateN(100, suite.problems[0]) 
    instances2 = suite.generateN(100, suite.problems[1]) 

    vals = {} 
    for i in range(6):
        vals["mean{}".format(i)] = 0.0 
        vals["std{}".format(i)] = 1.0 
    vals["greedy"] = "True" 
    vals["iterations"] = 50 
    vals["samples"] = 10 

    _,configurationDefinition = getConfigDef()

    instances = instances1 + instances2
    
    conf = Configuration(configurationDefinition, vals)

    

    rng = Random(seed)
    runs = []
    for inst in instances:
        run = Run(inst)

        steps = rng.randint(1,10)

        for step in range(steps):
            c = conf.duplicateParams()
            iters = rng.randint(10,50)
            result =    {"solutions":
                            [{  "solution":[rng.random() for d in range(30)],
                                "quality":rng.random()} for s in range(iters)],
                        "state": [
                                [{  "solution":[rng.random() for d in range(30)],
                                "quality":rng.random()} for s in range(10)] for j in range(iters)
                            ],
                        "evaluationsConsumed":iters*100,
                        "algorithmState":"",
                        "time":rng.randint(1000,10000)
                        }

            c.features = np.asarray([rng.random() for x in range(159)])
            c.rawResult = result
            run.configurations.append(c) 
        
        runs.append(run)
        
    confDB = ConfigurationDB()
    for run in runs:
        confDB.addRun(run) 

    return runs, confDB 
