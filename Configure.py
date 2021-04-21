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


#TODO: collect runs to compare random vs adaptive
#maybe delete some more extrenious info about runs?

"""
The main file. This file can be run to configure your algorithm after valid LAAC settings files have been defined. See parameters.py 
"""
import multiprocessing
from Configurator.Evaluator import SimpleEvaluator
from Configurator.ConfigurationDB import sqlite3ConfigurationDB
from Configurator.Run import Run
from Configurator.Runner import RandomInstanceRunner
from Configurator.Characterizer import Characterizer
from Configurator.ConfigurationGenerator import AdaptiveGenerator, RandomGenerator
from Configurator.ProblemSuite import ProblemSuite
from Configurator.ConfigurationDefinition import ConfigurationDefinition
from Configurator.Algorithm import Algorithm
from Configurator.TerminationCondition import FELimit
import json
import argparse
from random import Random, randint
from typing import List 
from pathlib import Path
import pickle
from os import path
from shutil import rmtree



#Counts the total FEs consumed by a list of runs 
def countFEs(runs:List[Run]) -> int:
    total = 0 
    for run in runs:
        for conf in run.configurations:
            total += conf.rawResult["evaluationsConsumed"]

    return total 


if __name__ == "__main__":
    #needed for torch, since torch is stateful
    multiprocessing.set_start_method("spawn")

    #READ THE SCENARIO

    #Notice that very few command line arguments are supported. The primary means of configuration SHOULD be through scenario, problem, and parameter JSONs. Furthermore, LAAC will not fill in default values for fields missing from the JSONs, all fields must be filled in. This is by choice, it means that in order to run LAAC you must explicitly document all settings/values you use, so as long as you save your JSONs, you know exactly what tests/experiments you've run. 
    parser = argparse.ArgumentParser(description='A tool for adaptive landscape aware online algorithm configuration.')
    parser.add_argument("-seed", action="store", nargs='?', default=None,  help="The seed for random number generation.", dest="seed") 
    parser.add_argument("-scenario", action="store", nargs=1, default=None , help="The scenario file to read from.", dest="scenario")
    parser.add_argument("-outDir", action="store", nargs='?', default=None, help="A directory to write results to.", dest="outDir")
    
    args = parser.parse_args()

    scenarioFile = "scenario.json" 
    if args.scenario is not None:
        scenarioFile = args.scenario[0] 

    with open(scenarioFile, 'r') as inF:
        scenario = json.loads(inF.read())["scenario"]

    with open(scenario["problemDefs"], 'r') as inF:
        problems = json.loads(inF.read())

    with open(scenario["parameterDefs"], 'r') as inF:
        parameters = json.loads(inF.read())

    #TODO: validate all 3 JSONS, and report any missing parameters

    #INITIALIZATIONS
    if args.seed is not None:
        if args.seed == "RANDOM":
            seed = randint(0,4000000000)
        else:
            seed = int(args.seed)
    else:
        seed = scenario["seed"]

    if args.outDir is not None:
        RESULTSPATH = args.outDir 
    else:
        RESULTSPATH = scenario["resultsStoragePath"]
    
    DBFILE = scenario["dbfile"]
    DBFILE = f"{RESULTSPATH}/{DBFILE}/"
    WORKINMEMORY = scenario["workInMemory"]
    MODELHISTORYFILE = scenario["modelHistory"]
    MODELHISTORYFILE = f"{RESULTSPATH}/{MODELHISTORYFILE}/"
    MODELSTORAGEPATH = scenario["modelStoragePath"]
    MODELSTORAGEPATH = f"{RESULTSPATH}/{MODELSTORAGEPATH}/"
    ALGORITHMSTORAGEPATH = f"{RESULTSPATH}/algorithm/"
    VALIDATE = scenario["validate"]
    COUNTVALIDATIONFES = scenario["countValidationFEs"]
    MODELTYPE = scenario["modelType"] 
    MININFORMEDPERCENT = scenario["minInformedPercent"]
    MAXINFORMEDPERCENT = scenario["maxInformedPercent"]
    INFOMREDPERCENTVARIANCE = scenario["informedPercentVariance"]

    #If the results path exists, remove it and all contained files 
    if path.exists(RESULTSPATH):
        rmtree(RESULTSPATH)

    #create the results path 
    Path(RESULTSPATH).mkdir(parents=True, exist_ok=True)

    #ensure the model storage location exists 
    Path(MODELSTORAGEPATH).mkdir(parents=True, exist_ok=True)

    #create a location for algorithm output 
    Path(ALGORITHMSTORAGEPATH).mkdir(parents=True, exist_ok=True)

    rng = Random(seed)

    alg = Algorithm(scenario["targetAlgorithm"], scenario["staticArgs"], scenario["strictConstraints"]==False, ALGORITHMSTORAGEPATH) 

    termination = FELimit(scenario["runFELimit"])
    
    configurationDefinition = ConfigurationDefinition(parameters) 

    suite = ProblemSuite(problems, rng.randint(0,4000000000)) 
    validationSuite = ProblemSuite({"problems":problems["validation"]}, rng.randint(0,4000000000))

    characterizer = Characterizer()
    
    if MODELTYPE == "Adaptive":
        generatorType = AdaptiveGenerator
        model = AdaptiveGenerator(204, configurationDefinition, seed=rng.randint(0,4000000000), minInformedPercent=MININFORMEDPERCENT, maxInformedPercent=MAXINFORMEDPERCENT, informedPercentVariance=INFOMREDPERCENTVARIANCE)
    elif MODELTYPE == "Random":
        generatorType = RandomGenerator 
        model = RandomGenerator(configurationDefinition, rng.randint(0,4000000000))
    else:
        raise Exception("Model type not recognized.")
    
    #TODO: figre out how Configure should be made aware of the problem dimensionality 
    #also, what about configuring for problems of different dimensionality simutaneously?
    #perhaps we should test on functions of a single size, and plan to use an auto-encoder/feature reduction in the future to normalize input sizes?
    #a much better idea is probably to give the model multiple heads, one for each size
    #so dimensionality becomes a required parameter of a problem, walk the suite to grab all dimensionalities, initialize a separate head for each one 
    # Each head could be a layer or two, and during training will be updated appropriately for feature vectors of that size  
    
    #model = RandomGenerator(configurationDefinition, rng.randint(0,4000000000))
    
    runner = RandomInstanceRunner(suite, characterizer, termination, rng.randint(0,4000000000), alg, scenario["threads"]) 
    validationRunner = RandomInstanceRunner(validationSuite, characterizer, termination, rng.randint(0,4000000000), alg, scenario["threads"])

    if WORKINMEMORY:
        configDB = sqlite3ConfigurationDB(path=":memory:", initialize=True,seed=rng.randint(0,4000000000))
        validationConfigDB = sqlite3ConfigurationDB(path=":memory:", initialize=True) 
    else:
        configDB = sqlite3ConfigurationDB(path=f"{DBFILE}.training.sqlite3", initialize=True)
        validationConfigDB = sqlite3ConfigurationDB(path=f"{DBFILE}.validation.sqlite3", initialize=True,seed=rng.randint(0,4000000000)) 

    

    #TODO: eventually evaluator parameter need to be in the scenario file
    evaluator = SimpleEvaluator(0.25, False, scenario["maxRunsPerConfig"])

    #MAIN LOOP
    FELIMIT = scenario["totalFELimit"]
    configsPerIteration = scenario["configsPerIteration"] 
    minRunsPerConfig = scenario["minRunsPerConfig"]     

    newRuns = runner.schedule(configsPerIteration, minRunsPerConfig, model) 
    totalFEsConsumed = countFEs(newRuns)
    for run in newRuns:
        run.performedOnIteration = 0
        configDB.addRun(run)


    iteration = 1
    best = dict() 
    while totalFEsConsumed < FELIMIT:
        # for getting some stats about memory usage 
        # from guppy import hpy
        # h = hpy()
        # print(h.heap())
        
        print("Progress: {}/{}".format(totalFEsConsumed,FELIMIT))

        evaluator.evaluate(configDB)

        model.update(configDB)

        #TODO: limit the total runs per iteration, and/or the total new configs vs the total reuns? adapt the limits according to criteria or iteration?
        toReRun = configDB.getReRuns() 
        newRuns = runner.schedule(configsPerIteration, minRunsPerConfig, model)
        totalFEsConsumed += countFEs(newRuns)
        for run in newRuns:
            run.performedOnIteration = iteration
            configDB.addRun(run)

        summary = model.history()["history"][-1] 
        print(summary)

        #Write the models current state to disk
        with open(f"{MODELSTORAGEPATH}/model_{iteration}.bin", 'wb') as outF:
            outF.write(pickle.dumps(model.getState()))

        if VALIDATE:
            validationRuns = validationRunner.schedule(configsPerIteration, minRunsPerConfig, model)
            if COUNTVALIDATIONFES:
                totalFEsConsumed += countFEs(validationRuns) 
            for run in validationRuns:
                run.performedOnIteration = iteration
                validationConfigDB.addRun(run) 
        
        iteration += 1

    print("FE LIMIT PASSED")

    if WORKINMEMORY: #We need to write the db from memory out to disk 
        configDB.backup(f"{DBFILE}.training.sqlite3")
        validationConfigDB.backup(f"{DBFILE}.validation.sqlite3")

    with open(MODELHISTORYFILE, 'w') as outF:
        outF.write(json.dumps(model.history(),indent=2))


