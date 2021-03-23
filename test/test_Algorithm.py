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

import json
from json.decoder import JSONDecodeError
from math import isfinite
from subprocess import PIPE, Popen
from Configurator.ConfigurationGenerator import RandomGenerator
from Configurator.TerminationCondition import FELimit
from Configurator.ConfigurationDefinition import Configuration
from Configurator.Characterizer import Characterizer
from random import Random
from test.initializer import getConfigDef, getProblemSuite
import unittest

from Configurator.Algorithm import Algorithm

"""
Sanity checks for Algorithm
"""
#TODO: can we really have too many tests?
class TestAlgorithm(unittest.TestCase):

    def setUp(self):
        self.seed = 12345
        self.problemDefs,self.suite = getProblemSuite(self.seed)
        self.confDefs, self.configurationDefinition = getConfigDef()
        self.rng = Random(self.seed)
        self.characterizer = Characterizer() 
        prob = self.suite.problems[0] 
        self.instance = prob.generateInstance()

        vals = {} 
        for i in range(6):
            vals["mean{}".format(i)] = 0.0 
            vals["std{}".format(i)] = 1.0 
        vals["greedy"] = "True" 
        vals["iterations"] = 50 
        vals["samples"] = 10 
        self.vals = vals

        self.condition = FELimit(1000) 


    def tearDown(self):
        pass

    def testAlgorithm(self):
        alg = Algorithm("python3 target-algorithm.py","-d 5", True) 

        conf1 = Configuration(self.configurationDefinition, self.vals)
        conf2 = Configuration(self.configurationDefinition, self.vals)

        model1 = RandomGenerator(self.configurationDefinition, self.seed)
        model2 = RandomGenerator(self.configurationDefinition, self.seed)

        out1 = alg.run(self.instance, conf1, self.characterizer, model1, self.condition, self.seed) 
        out2 = alg.run(self.instance, conf2, self.characterizer, model2, self.condition, self.seed) 

        self.assertEqual(out1.instance.toFlags(), out2.instance.toFlags(), "Results should have the same instance") 

        self.assertEqual(out1.runConfigID(), out2.runConfigID(), "Should have the same resulting ID")

        self.assertNotEqual(out1.performedAt, out2.performedAt, "Were not performed at the same time") 

        #Verify that we can repeat each execution of the target algorithm and get the same results
        for i,conf in enumerate(out1.configurations[1:]):
            cmd = "{} {} {} {} {} {} {}".format("python3 target-algorithm.py", 0, conf.seed, "-d 5", self.instance.toFlags(), conf.toFlags(), out1.configurations[i].rawResult["algorithmState"])
            
            io = Popen(cmd.strip().split(" "), stdout=PIPE, stderr=PIPE)
            _stdout,_stderr = io.communicate() 
            output = _stdout.decode()
            loc = output.find("RESULTS FOLLOW")
            try:
                result = json.loads(output[loc + 14:])
            except JSONDecodeError:
                print(output)
                raise ValueError

            features = self.characterizer.characterize(result, conf.characterizeSeed)

            for i,(v1,v2) in enumerate(zip(conf.features,features)):
                if not isfinite(v1):
                    v1 = 0
                if not isfinite(v2):
                    v2 = 0
                self.assertEqual(v1,v2, "Feature {} should be the same.")

            for i,(sol1,sol2) in enumerate(zip(conf.rawResult["solutions"],result["solutions"])):
                for j,(v1,v2) in enumerate(zip(sol1["solution"], sol2["solution"])):
                    self.assertEqual(v1,v2, "Values {} of solutions {} of sequence of generated solutions should be the same.".format(j,i))


  