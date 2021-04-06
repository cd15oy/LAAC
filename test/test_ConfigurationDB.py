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

from test.initializer import getPopulatedConfigDB
import unittest

"""
Sanity checks for ConfigurationDB
"""
#TODO: These tests will need to be updated after we update/finalize the configuration DB
class TestConfigurationDB(unittest.TestCase):

    def setUp(self):
        self.seed = 12345
        

    def tearDown(self):
        pass

    #TODO: update for the new config DB implementation
    def testDB(self):
        runs,db = getPopulatedConfigDB(self.seed)

        probGenerators = [x for x in db.problemGenerator()] 

        self.assertTrue(len(probGenerators) == 2, "Should be two problems in DB")

        for prob in probGenerators:
            records = [x for x in prob]
            self.assertTrue(len(records) == 1, "Should be one record for each problem.")

            for rcrd in records:

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

                

