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

from Configurator.TerminationCondition import FELimit
from Configurator.ConfigurationDefinition import Configuration
from test.initializer import getConfigDef, getProblemSuite
from Configurator.ProblemSuite import ProblemSuite
from Configurator.Problem import Instance
import unittest

from Configurator.Run import Run

"""
Sanity checks for TerminationConditions
"""
#TODO: can we really have too many tests?

class TestTerminationCondition(unittest.TestCase):


    def setUp(self):
        self.seed = 12345
        self.problemDefs,self.suite = getProblemSuite(self.seed)
        self.confDefs, self.configurationDefinition = getConfigDef()

    def tearDown(self):
        pass

    def testFELimit(self):
        prob = self.suite.problems[0] 
        instData = prob.generateInstance()
        inst = Instance(prob, instData)
        run = Run(inst)

        vals = {} 
        for i in range(6):
            vals["mean{}".format(i)] = 0.0 
            vals["std{}".format(i)] = 1.0 
        vals["greedy"] = "True" 
        vals["iterations"] = 50 
        vals["samples"] = 10 

        for i in range(5):
            conf = Configuration(self.configurationDefinition, vals) 
            conf.rawResult = {
                "evaluationsConsumed":100*i
            }
            run.configurations.append(conf) 

        condition = FELimit(1000) 

        self.assertTrue(condition.terminate(run), "The FE limit should be passed")

        condition = FELimit(3000) 

        self.assertFalse(condition.terminate(run), "The FE limit should not be passed")


