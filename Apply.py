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
This script performs runs of the target algorithm using a pre-trained model, and (possibly) user specified initial configurations. 
"""

import multiprocessing
from Configurator.Run import Run
from Configurator.ConfigurationDB import sqlite3ConfigurationDB
from Configurator.Runner import RandomInstanceRunner
import pickle
from Configurator.ConfigurationGenerator import initModel
from Configurator.Characterizer import Characterizer
from Configurator.ProblemSuite import ProblemSuite
from Configurator.ConfigurationDefinition import Configuration, ConfigurationDefinition
from Configurator.TerminationCondition import FELimit
from Configurator.Algorithm import Algorithm
import argparse
import json
from pathlib import Path
from random import Random, randint
from os import path 
from shutil import rmtree 

def main():
    #needed for torch, since torch is stateful
    multiprocessing.set_start_method("spawn")
    
    #Just like with Configure.py, all setting should be explicitly defined in a json. 
    parser = argparse.ArgumentParser(description='A tool for adaptive landscape aware online algorithm configuration.')
    parser.add_argument("-seed", action="store", nargs='?', default=None,  help="The seed for random number generation.", dest="seed") 
    parser.add_argument("-algorithm", action="store", nargs=1, default=None , help="The algorithm definition to read from.", dest="algorithm")
    parser.add_argument("-outDir", action="store", nargs='?', default=None, help="A directory to write results to.", dest="outDir")

    args = parser.parse_args()

    algorithmFile = "algorithm.json" 
    if args.algorithm is not None:
        algorithmFile = args.algorithm[0] 

    with open(algorithmFile, 'r') as inF:
        algorithmDef = json.loads(inF.read())

    with open(algorithmDef["problemDefs"], 'r') as inF:
        problems = json.loads(inF.read())

    with open(algorithmDef["parameterDefs"], 'r') as inF:
        parameters = json.loads(inF.read())

    with open(algorithmDef["configurations"], 'r') as inF:
        configurations = json.loads(inF.read())

    #TODO: validate all 4 JSONS, and report any missing parameters

    #INITIALIZATIONS
    if args.seed is not None:
        if args.seed == "RANDOM":
            seed = randint(0,4000000000)
        else:
            seed = int(args.seed)
    else:
        seed = algorithmDef["seed"]

    if args.outDir is not None:
        RESULTSPATH = args.outDir 
    else:
        RESULTSPATH = algorithmDef["resultsStoragePath"]

    DBFILE = algorithmDef["dbfile"]
    DBFILE = f"{RESULTSPATH}/{DBFILE}"
    WORKINMEMORY = algorithmDef["workInMemory"]
    ALGORITHMSTORAGEPATH = f"{RESULTSPATH}/algorithm/"
    FIXEDDIMENSIONALITY = algorithmDef["fixedDimensionality"]
    DIMENSIONALITY = algorithmDef["dimensionality"]
    RUNFELIMIT = algorithmDef["runFELimit"]
    REPETITIONSPERRUN = algorithmDef["repetitionsPerRun"] 
    BLINDRUNSPERPROBLEM = algorithmDef["blindRunsPerProblem"]
    TARGETALGORITHM = algorithmDef["targetAlgorithm"]
    STATICARGS = algorithmDef["staticArgs"]
    STRICTCONSTRAINTS = algorithmDef["strictConstraints"]
    THREADS = algorithmDef["threads"]
    PATHTOMODEL = algorithmDef["pathToModel"] 

    #If the results path exists, remove it and all contained files 
    if path.exists(RESULTSPATH):
        rmtree(RESULTSPATH)

    #create the results path 
    Path(RESULTSPATH).mkdir(parents=True, exist_ok=True)

    #create a location for algorithm output 
    Path(ALGORITHMSTORAGEPATH).mkdir(parents=True, exist_ok=True)

    rng = Random(seed)

    alg = Algorithm(TARGETALGORITHM, STATICARGS, STRICTCONSTRAINTS==False, ALGORITHMSTORAGEPATH) 

    termination = FELimit(RUNFELIMIT)
    
    configurationDefinition = ConfigurationDefinition(parameters)

    suite = ProblemSuite(problems, rng.randint(0,4000000000))
    
    characterizer = Characterizer(dimensionality=DIMENSIONALITY, fixedDimensionality=FIXEDDIMENSIONALITY)

    with open(PATHTOMODEL, 'rb') as inF:
        modelState = pickle.loads(inF.read())

    model = initModel(modelState, rng.randint(0,4000000000))

    runner = RandomInstanceRunner(suite, characterizer, termination, rng.randint(0,4000000000), alg, THREADS)

    if WORKINMEMORY:
        configDB = sqlite3ConfigurationDB(path=":memory:", initialize=True,seed=rng.randint(0,4000000000))
    else:
        configDB = sqlite3ConfigurationDB(path=f"{DBFILE}.sqlite3", initialize=True,seed=rng.randint(0,4000000000))

    #now we need to set up the list of configs/problem instances to run 
    todo = []

    #First, we need to generate BLINDRUNSPERPROBLEM configurations via the model for each problem and schedule REPITITONSPERRUN runs for each 
    for prob in suite.problems:
        for i in range(BLINDRUNSPERPROBLEM):
            conf = model.generate(None)
            for j in range(REPETITIONSPERRUN):
                r = Run(suite.generateN(1, prob)[0])
                r.configurations.append(conf.duplicateParams())
                todo.append(r)


    #Next, we need to parse the configurations file, and schedule the requested runs 

    #check for configs to use with all problems 

    if "*" in configurations:
        for confDict in configurations["*"]:
            for prob in suite.problems:
                for i in range(REPETITIONSPERRUN):
                    r = Run(suite.generateN(1, prob)[0])
                    c = Configuration(configurationDefinition, confDict) 
                    r.configurations.append(c) 
                    todo.append(r) 

    #and now any configurations for specific problems 
    for prob in suite.problems:
        if prob.name in configurations:
            for confDict in configurations[prob.name]:
                for i in range(REPETITIONSPERRUN):
                    r = Run(suite.generateN(1, prob)[0])
                    c = Configuration(configurationDefinition, confDict) 
                    r.configurations.append(c) 
                    todo.append(r) 

    #do the work, yawn 
    runs = runner.schedule(0, 0, model, todo)

    #save the results 
    for run in runs:
        run.performedOnIteration = 0 
        configDB.addRun(run) 

    if WORKINMEMORY: #We need to write the db from memory out to disk 
        configDB.backup(f"{DBFILE}.sqlite3")
   
if __name__ == "__main__":
    main() 