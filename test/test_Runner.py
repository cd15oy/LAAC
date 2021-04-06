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

from multiprocessing.managers import BaseManager 
from test.helper import compareFeatures
from Configurator.ConfigurationGenerator import RandomGenerator
from Configurator.Runner import RandomInstanceRunner
from Configurator.Algorithm import Algorithm
from Configurator.TerminationCondition import FELimit
from Configure import FELimit
from Configurator.Characterizer import Characterizer
from random import Random
from test.initializer import getConfigDef, getProblemSuite
import unittest


"""
Sanity checks for Runners
"""
#TODO: can we really have too many tests?
class TestRunner(unittest.TestCase):

    def setUp(self):
        self.seed = 12345 
        self.rng = Random(self.seed)
        _,self.confDef = getConfigDef()

    def tearDown(self):
        pass

    def _initRunner(self, runnerClass):
        _,suite = getProblemSuite(self.seed)
        characterizer = Characterizer() 
        condition = FELimit(1000)
        alg = Algorithm("python3 target-algorithm.py", "-d 5", True) 

        rnr = runnerClass(suite, characterizer, condition, self.seed, alg, 1) 

        return rnr
        
    def testRandomInstance(self):

        rndInstRunner1 = self._initRunner(RandomInstanceRunner) 
        rndInstRunner2 = self._initRunner(RandomInstanceRunner)

        sampler1 = RandomGenerator(self.confDef, self.seed)  
        sampler2 = RandomGenerator(self.confDef, self.seed)
       
     

        runs1 = rndInstRunner1.schedule(10, 2, sampler1.getState(), None) 
        runs2 = rndInstRunner2.schedule(10, 2, sampler2.getState(), None)

        for r1, r2 in zip(runs1,runs2):
            for c1,c2 in zip(r1.configurations,r2.configurations):

                self.assertEqual(c1.valid, c2.valid, "Validity should be the same") 

                compareFeatures(self, c1.features, c2.features)

                #run time is semi-random since it is a measure of real time consumed during running 
                #we adjust results to make the run times match 
                c1.rawResult["time"] = 0 
                c2.rawResult["time"] = 0 
                self.assertEqual(c1.rawResult, c2.rawResult, "The raw results should match") 

                self.assertEqual(c1.seed, c2.seed, "The run seeds should match")

                self.assertEqual(c1.characterizeSeed, c2.characterizeSeed, "The characterize seeds should match.")

                self.assertEqual(c1.toFlags(), c2.toFlags(), "Both configs should have the same values.")





  