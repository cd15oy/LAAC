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

from test.helper import compareFeatures
import unittest
from random import Random

from Configurator.Characterizer import Characterizer

"""
Sanity checks for our Characterizer
"""
#TODO: can we really have too many tests?

class TestCharacterizer(unittest.TestCase):

    def rndSol(self):
        return{"solution":[self.rng.random() for x in range(self.dimensionality)],"quality":self.rng.random()}

    def setUp(self):
        self.seed = 12345 
        self.dimensionality = 5 
        self.rng = Random(self.seed)

    def tearDown(self):
        pass

    def testOutput(self):
        for i in range(100):
            result = dict() 
            result["solutions"] = [self.rndSol() for x in range(50)]

            result["state"] = [
                    [self.rndSol() for x in range(50)] for y in range(50)
                ]
                    
            #One of our landscape measures used in Characterize (the Pairwise class) uses multiple random samples of the solutions provided to estimate it's value. The measure is based on the pairwise distance between solutions, but obviously that gets expensive very quickly. We re-initialize the Characterizer here so the random samples will be the same in the first and second call, so the estimated values will be the same

            c = Characterizer() 

            a = c.characterize(result,self.seed)
            b = c.characterize(result,self.seed)

            compareFeatures(self, a, b)

            
