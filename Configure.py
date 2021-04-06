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

#TODO: Final Prototype:
#### Update the config DB to avoid the need to rewalk the entire DB over and over and over again
####    also to drop unneeded inforation, ex the solutions/states and save space
#### Update the config DB to use sqlite3, and store results on disk  
#### validation/applicaitons mode ->  ability to run more configs/sequences using a previously trainied model WITHOUT any addition training. Basically, we need the ability to skip the training steps, and the desirable/rerun flagging. Just want to give the system problems + a trained model and watch it do runs 
#### Add logging, which writes run stats to the ConfigDB sqlite3 file
####    or possible a more portable JSON
#### update PSO implementation to produce needed output 
#### collect runs to compare random vs adaptive

#see the copy of Models.py on frank for some different tested NN params

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
from multiprocessing.managers import BaseManager 

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

    class CustomManager(BaseManager):
        pass 

    #TODO: scenario should have a flag to choose between the adaptive and random generators

    rng = Random(seed)

    alg = Algorithm(scenario["targetAlgorithm"], scenario["staticArgs"], scenario["strictConstraints"]==False) 

    termination = FELimit(scenario["runFELimit"])
    
    configurationDefinition = ConfigurationDefinition(parameters) 

    suite = ProblemSuite(problems, rng.randint(0,4000000000)) 

    characterizer = Characterizer()
    

    generatorType = AdaptiveGenerator 

    #TODO: figre out how Configure should be made aware of the problem dimensionality 
    #also, what about configuring for problems of different dimensionality simutaneously?
    model = generatorType(159, configurationDefinition, seed=rng.randint(0,4000000000))
    #model = RandomGenerator(configurationDefinition, rng.randint(0,4000000000))
    
    runner = RandomInstanceRunner(suite, characterizer, termination, rng.randint(0,4000000000), alg, scenario["threads"]) 

    configDB = sqlite3ConfigurationDB(initialize=True) 

    #TODO: eventually evaluator parameter need to be in the scenario file
    evaluator = SimpleEvaluator(0.25, False, scenario["maxRunsPerConfig"])

    #MAIN LOOP
    FELIMIT = scenario["totalFELimit"]
    configsPerIteration = scenario["configsPerIteration"] 
    minRunsPerConfig = scenario["minRunsPerConfig"]     

    newRuns = runner.schedule(configsPerIteration, minRunsPerConfig, model.getState()) 
    totalFEsConsumed = countFEs(newRuns)


    best = dict() 
    while totalFEsConsumed < FELIMIT:
        # for getting some stats about memory usage 
        # from guppy import hpy
        # h = hpy()
        # print(h.heap())
        
        print("Progress: {}/{}".format(totalFEsConsumed,FELIMIT))

        for run in newRuns:
            configDB.addRun(run)

        evaluator.evaluate(configDB)

        model.update(configDB)

        #TODO: limit the total runs per iteration, and/or the total new configs vs the total reuns? adapt the limits according to criteria or iteration?
        toReRun = configDB.getReRuns() 
        newRuns = runner.schedule(configsPerIteration, minRunsPerConfig, model.getState())
        totalFEsConsumed += countFEs(newRuns)

        for problem in configDB.problemGenerator():
            for record in problem:
                prob = record.problem 

                if prob not in best:
                    best[prob] = float('inf')
                if record.desirable():
                    quality = []
                    for run in record.getRuns():
                        quality.append(run.configurations[-1].rawResult["solutions"][-1]["quality"]) 
                    from statistics import mean
                    quality = mean(quality)
                    if quality < best[prob]:
                        best[prob] = quality 
        print(best)

    print("FE LIMIT PASSED")
    #TODO output results in some format

