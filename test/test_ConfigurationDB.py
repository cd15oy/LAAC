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

from Configurator.ConfigurationDB import Record
from random import Random
from test.initializer import getPopulatedConfigDB
import unittest

"""
Sanity checks for ConfigurationDB
"""
#TODO: These tests will need to be updated after we update/finalize the configuration DB
class TestConfiguratioDB(unittest.TestCase):

    def setUp(self):
        self.seed = 12345
        self.runs,self.db = getPopulatedConfigDB(self.seed)

    def tearDown(self):
        pass

    def testDB(self):
        self.assertTrue(len(self.db.records) == 2, "Should be two problems in DB")

        for prob in self.db.records:
            self.assertTrue(len(self.db.records[prob]) == 1, "Should be one record for each problem.")

            for id in self.db.records[prob]:
                rcrd:Record = self.db.records[prob][id]

                self.assertTrue(len(rcrd.getRuns()) == 100, "Should be 100 runs in this record.")
                
                updatedAt = rcrd.updatedAt()

                self.assertFalse(rcrd.desirable(), "Should not be desirable.")
                rcrd.desirable(True)
                updatedAt2 = rcrd.updatedAt()
                self.assertTrue(rcrd.desirable(), "Should be desirable.")
                self.assertTrue(updatedAt < updatedAt2, "Updated at should have updated.")

                updatedAt = rcrd.updatedAt()
                self.assertFalse(rcrd.reRun(), "Should not need a reRun.")
                rcrd.reRun(True)
                updatedAt2 = rcrd.updatedAt()
                self.assertTrue(rcrd.reRun(), "Should need a reRun.")
                self.assertTrue(updatedAt < updatedAt2, "Updated at should have updated.")

                

