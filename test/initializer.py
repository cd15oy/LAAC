from random import Random
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

    result = {"solutions":[{"solution":None,"quality":None}]}

    rng = Random(seed)
    runs = []
    for inst in instances:
        run = Run(inst)
        c = conf.duplicateParams()
        result["solutions"][-1]["quality"] = rng.random()
        c.rawResult = deepcopy(result)
        run.configurations.append(c) 
        runs.append(run)
        
    confDB = ConfigurationDB()
    for run in runs:
        confDB.addRun(run) 

    return runs, confDB 
