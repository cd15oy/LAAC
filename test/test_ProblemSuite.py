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

import unittest
from Configurator.ProblemSuite import ProblemSuite
from Configurator.Problem import Problem, Instance 

"""
Sanity checks for ProblemSuite, Problem and Instance.
"""
#TODO: can we really have too few tests?

class TestProblemSuite(unittest.TestCase):

    def setUp(self):
        from parameters import write
        write()
        import json 
        with open("optFiles/problems.json", 'r') as inF:
            self.problemDefs = json.loads(inF.read())
        self.suite = ProblemSuite(self.problemDefs, 12345) 

    def tearDown(self):
        pass

    def testProblemSuite(self):
        
        ret = self.suite.generateN(10) 
        total = 0 
        for prob in self.suite.problems:
            total += len(prob.instances) 
        
        self.assertEqual(len(self.suite.problems), 2, "Problem suite initialized an incorrect number of problems")
        self.assertEqual(total, 10, "Problem suite generated an incorrect number of instances")
        self.assertEqual(len(ret), 10, "Problem suite returned an incorrect number of instances")

        problems = dict() 
        for p in self.suite.problems:
            problems[p.name] = p 

        self.assertTrue(problems["f1"].name == "f1", "Incorrectly imported f1")
        self.assertTrue(problems["f1"].flag == "-p f1","Incorrectly imported f1")
        self.assertTrue(problems["f1"].instanceTemplates[0] == "-pSeed $RANDOM", "Incorrectly imported f1")

        self.assertTrue(problems["f2"].name == "f2", "Incorrectly imported f2")
        self.assertTrue(problems["f2"].flag == "-p f2","Incorrectly imported f2")
        self.assertTrue(problems["f2"].instanceTemplates[0] == "-pSeed $RANDOM", "Incorrectly imported f1")


    def testProblem(self):

        problems = dict() 
        for p in self.suite.problems:
            problems[p.name] = p 

        p = Problem(problems["f1"].name, problems["f1"].flag, problems["f1"].instanceTemplates, 12345) 

        self.assertTrue(p.toFlags() == "-p f1", "Incorrect toFlags() on Problem")

        try:
            p.sampleInstances(10)
            self.assertTrue(False, "Problem should have thrown IndexError when attempting to sample non-existent instances")
        except IndexError:
            pass

        instanceString = p._parseTemplate(p.instanceTemplates[0])
        seed = instanceString.split(" ")[1] 
        self.assertTrue(seed != "$RANDOM", "$RANDOM keyword should have been replaced") 
        try:
            numericSeed = int(seed)
            
        except ValueError:
            self.assertTrue(False, "$RANDOM keyword should have been replaced with a valid int")

        self.assertLessEqual(numericSeed, 4000000000, "seeds should be in [0,4000000000]")
        self.assertGreaterEqual(numericSeed, 0, "seeds should be in [0,4000000000]")

        inst = p.generateInstance()

        self.assertTrue(len(p.instances) == 1, "p should have one instance")

    def testInstance(self):
        problems = dict() 
        for p in self.suite.problems:
            problems[p.name] = p 

        p = Problem(problems["f1"].name, problems["f1"].flag, problems["f1"].instanceTemplates, 12345) 

        instanceString1 = p._parseTemplate(p.instanceTemplates[0]) 
        instanceString2 = p._parseTemplate(p.instanceTemplates[0])

        instance1 = Instance(p, instanceString1)
        instance2 = Instance(p, instanceString2) 

        self.assertFalse(instance1 == instance2, "Instances should not be equal")
        self.assertFalse(instance1.toFlags() == instance2.toFlags(), "Instance flags should not be equal")

        instance1Clone = Instance(p, instanceString1)
        self.assertEqual(instance1, instance1Clone, "These instances should be equal")