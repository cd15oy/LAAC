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

from random import Random
import unittest

from Configurator.RoC import fit

"""
Sanity checks for RoC
"""
#TODO: can we really have too many tests?
class TestRoC(unittest.TestCase):

    def setUp(self):
        self.seed = 12345 
        self.rng = Random(self.seed)

    def tearDown(self):
        pass

    def testOutput(self):
        vals = [self.rng.random()*x for x in range(1000)] 

        out1 = fit(vals)
        out2 = fit(vals)

        for x,y in zip(out1,out2):
            self.assertEqual(x,y, "Values should be the same for the same inputs.") 

        vals2 = [self.rng.random()*x*2 for x in range(1000)] 

        out3 = fit(vals2) 

        self.assertTrue(out3[0] > out1[0], "Second sequence should have a larger rate of change.")

  