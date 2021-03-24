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

from Configurator.Model import LatinHyperCube, Model, NeuralNetwork
from random import Random

import numpy as np
from test.initializer import getConfigDef, getPopulatedConfigDB
import unittest


"""
Sanity checks for the Models
"""
#TODO: can we really have too many tests?
class TestModel(unittest.TestCase):

    def setUp(self):
        self.seed = 12345 
        self.rng = Random(self.seed)
        np.random.seed(self.seed)

        _, self.configDef = getConfigDef()

        _, self.configDB = getPopulatedConfigDB(self.seed)

        for prob in self.configDB.records:
            for k in self.configDB.records[prob]:
                rcrd = self.configDB.records[prob][k]
                rcrd.desirable(True)

    def _isRepeatable(self, inputSize:int, model1:Model, model2:Model):
        features = np.random.random((1,inputSize))

        conf1 = model1.generate(features) 
        conf2 = model2.generate(features)

        self.assertEqual(conf1, conf2, "Both model instances should produce the same configuration from the same features.") 

        model1.update(self.configDB)
        model2.update(self.configDB) 

        conf1 = model1.generate(features) 
        conf2 = model2.generate(features)

        self.assertEqual(conf1, conf2, "Both model instances should produce the same configuration from the same features after training.") 

    def tearDown(self):
        pass

    def testLatinHyperCube(self):
        model1 = LatinHyperCube(1000, self.configDef, self.seed)
        model2 = LatinHyperCube(1000, self.configDef, self.seed)

        self._isRepeatable(100, model1, model2)

        #TODO: test uniformity of distribution?


    def testNeuralNetwork(self):
        model1 = NeuralNetwork(159, self.configDef, self.seed, True) 
        model2 = NeuralNetwork(159, self.configDef, self.seed, True)

        self._isRepeatable(159, model1, model2)
  