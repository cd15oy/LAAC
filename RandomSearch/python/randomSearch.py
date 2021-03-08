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
This file implements a simple random search algorithm to be used for demonstrating LAAC. In practice there is no need for the target-algorithm to be in python and the example target-algorithm.py wrapper is written for general use. 
"""

from random import random,seed,gauss,randint
import argparse
from time import time 
import json 

RANGE = 10

#shifts the optima and rotates the function to make it a little more difficult 
def shiftAndRotate(x, shift, rotation):
    x1 = [x[i] - shift[i] for i,v in enumerate(x)] 
    x2 = [0 for i in range(len(x))] 

    #dot product of x and rotation 
    for c in range(len(x)):
        for r in range(len(x)):
            x2[c] += x1[r]*rotation[r][c]

    return x2 

#A simple function to optimize 
def f1(x, shift, rotation):
    x2 = shiftAndRotate(x, shift, rotation)
    tot = 0 
    for v in x2:
        tot += abs(v) 
    return tot 
     
#Another simple function to optimize 
def f2(x, shift, rotation):
    x2 = shiftAndRotate(x, shift, rotation)
    tot = 1
    for v in x2:
        tot *= v 
    return tot 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a simple random search.')
    parser.add_argument("-stepSizes", action="store", nargs='+', default=None , help="Distribution parameters used to generate steps for each problem dimension", dest="stepSizes")
    parser.add_argument("-d", action="store", nargs='?', default=5, type=int, help="The number of dimensions to run on.", dest="dimensionality")
    parser.add_argument("-i", action="store", nargs='?', default=1000, type=int, help="The number of iterations to run.", dest="iterations")
    parser.add_argument("-s", action="store", nargs='?', default=10, type=int, help="The number of samples per iteration.", dest="samples")
    parser.add_argument("-pSeed", action="store", nargs='?', default=12345, type=int, help="The seed for initializing the problems.", dest="pSeed")
    parser.add_argument("-aSeed", action="store", nargs='?', default=randint(0,4000000000) , type=int, help="The seed for random number generation during the search", dest="aSeed") #This should be random so separate runs still have different trajectories by default 
    parser.add_argument("-restore", action="store", nargs='+', default=None , help="Continue the search from the provided solution.", dest="restore")
    parser.add_argument("-p", action="store", nargs='?', default="f1", type=str, help="The problem to optimize", dest="problem", choices=["f1","f2"])
    parser.add_argument("-shift", action="store", nargs='?', default=True, type=bool, help="Shift the function?", dest="shift", choices=[True,False])
    parser.add_argument("-rotate", action="store", nargs='?', default=True, type=bool, help="Rotate the function?", dest="rotate", choices=[True,False])
    parser.add_argument("-g", action="store", nargs='?', default=True, type=bool, help="Only update the current solution if the new one is better?", dest="greedy", choices=[True, False])

    args = parser.parse_args() 

    STEPS = [[0,1] for x in range(args.dimensionality)]
    if args.stepSizes is not None:
        vals = [float(x) for x in args.stepSizes] 
        for x in range(0, 2*args.dimensionality,2):
            STEPS[int(x/2)][0] = vals[x]
            STEPS[int(x/2)][1] = vals[x+1]  



    
    SHIFT = [0 for x in range(args.dimensionality)] 
    ROTATE = [[0 for x in range(args.dimensionality)] for y in range(args.dimensionality)] 
    for x in range(args.dimensionality):
        ROTATE[x][x] = 1 

    #If requested generate random shift and rotation matrices 
    #We use the problem seed, so we can easily ensure that the same instance is used in different executions 
    seed(args.pSeed)
    if args.shift:
        for x in range(args.dimensionality):
            SHIFT[x] = (random()*2*RANGE) - RANGE

    #It's just a random matrix, really we just want to add some dependence between the variables to make the problem a little harder 
    if args.rotate:
        for x in range(args.dimensionality):
            for y in range(args.dimensionality):
                ROTATE[x][y] = (random()*2)-1

    if args.problem == "f1":
        prob = f1 
    else:
        prob = f2 

    #Now we use the algorithm seed, so the search can proceed differently on different runs of the same instance 
    seed(args.aSeed)

    solutions = [] 
    evals = 0 

    startTime = time() 

    #restore a previous found solution as the starting point if needed 
    if args.restore:
        solution = [float(x) for x in args.restore]
        fitness = prob(solution, SHIFT, ROTATE)
    else:
        solution = [((random()*2)-1)*RANGE for x in range(args.dimensionality)]
        fitness = prob(solution, SHIFT, ROTATE)
    
    evals += 1 #one evaluation consumed above 

    solutions.append({"quality":fitness,"solution":solution})

    #run the search 
    for iter in range(args.iterations):

        #take samples random steps away from the current solution 
        nextSols = [] 
        for sample in range(args.samples):
            sol = [solution[x] + gauss(STEPS[x][0], STEPS[x][1]) for x in range(args.dimensionality)] 
            nextSols.append(sol) 

        bestStep = None
        bestStepFit = float('inf')
        #update our solution with the best found result 
        for sol in nextSols:
            f = prob(sol, SHIFT, ROTATE) 
            evals += 1 
            if f < bestStepFit:
                bestStepFit = f 
                bestStep = sol 

        if args.greedy:
            if bestStepFit < fitness:
                fitness = bestStepFit 
                solution = bestStep 
        else:
            fitness = bestStepFit 
            solution = bestStep 

        solutions.append({"quality":fitness,"solution":solution})

    totalTime = time() - startTime 

    result = dict() 
    #solutions is just a list of dicts defining each produced solution and it's quality
    result["solutions"] = solutions
    #the total number of function evaluations consumed in this execution 
    result["evaluationsConsumed"] = evals 

    #algorithm state should be a string that can be passed as flags to the algorithm to "pick up" where this run left off 
    #problem/instance information does not need to be included LAAC will provide that on its own 
    state = "" 
    for v in solution:
        state += str(v) + " "
    result["algorithmState"] = "-restore {0}".format(state)

    #time used by the run
    result["time"] = totalTime

    print(json.dumps(result))