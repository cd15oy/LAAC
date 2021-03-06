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
from Configurator.ConfigurationDefinition import ConfigurationDefinition, Constraint, Real, Integer, Categorical, ConcreteParameter
from Configurator.Configuration import Configuration,MissingParameterError 

"""
Sanity checks for ConfigurationDefinition, Configuration, and the supporting classes 
Everything contained in ConfigurationDefinition.py and Configuration.py 
"""
#TODO: can we really have too many tests?

class TestConfigurations(unittest.TestCase):

    def setUp(self):
        from parameters import write
        write()
        import json 
        with open("optFiles/parameters.json", 'r') as inF:
            self.confDefs = json.loads(inF.read())
        self.configurationDefinition = ConfigurationDefinition(self.confDefs) 

    def tearDown(self):
        pass

    def testReal(self):
        try:
            r = Real("v1", "real", "-v1", 1.0, 0.0, 2.0)
        except ValueError as e:
            self.assertTrue(False, "Value error ({0}) incorrectly thrown".format(e))

        try:
            r = Real("v1", "real", "-v1", 1.0, 2.0, 0.0)
            self.assertTrue(False, "Value error should be thrown for lower > upper")
        except ValueError as e:
            pass
    
        try:
            r = Real("v1", "real", "-v1", "wrong", 0.0, 2.0)
            self.assertTrue(False, "Value error should be thrown for a non-float default ")
        except ValueError as e:
            pass

        try:
            r = Real("v1", "real", "-v1", 5.0, 0.0, 2.0)
            self.assertTrue(False, "Value error should be thrown for a default outside lower and upper ")
        except ValueError as e:
            pass

        self.assertTrue(r.validate(0.25), "0.25 should be a valid value") 

        self.assertFalse(r.validate(-0.25), "-0.25 should not be a valid value") 

    def testInteger(self):
        try:
            r = Integer("v1", "integer", "-v1", 1, 0, 2)
        except ValueError as e:
            self.assertTrue(False, "Value error ({0}) incorrectly thrown".format(e))

        try:
            r = Integer("v1", "real", "-v1", 1, 2, 0)
            self.assertTrue(False, "Value error should be thrown for lower > upper")
        except ValueError as e:
            pass
    
        try:
            r = Integer("v1", "real", "-v1", "wrong", 0, 2)
            self.assertTrue(False, "Value error should be thrown for a non-int default")
        except ValueError as e:
            pass

        try:
            r = Integer("v1", "real", "-v1", 5, 0, 2)
            self.assertTrue(False, "Value error should be thrown for a default outside lower and upper ")
        except ValueError as e:
            pass

        self.assertTrue(r.validate(1), "0.25 should be a valid value") 

        self.assertFalse(r.validate(-1), "-0.25 should not be a valid value") 

    def testCategorical(self):
        try:
            r = Categorical("v1", "categorical", "-v1", "default", ["a", "b", "c", "default"])
        except ValueError as e:
            self.assertTrue(False, "Value error ({0}) incorrectly thrown".format(e))
    
        try:
            r = Categorical("v1", "real", "-v1", 23432,["a", "b", "c", "default"])
            self.assertTrue(False, "Value error should be thrown for a non-string default")
        except ValueError as e:
            pass

        try:
            r = Categorical("v1", "real", "-v1", "q",["a", "b", "c", "default"])
            self.assertTrue(False, "Value error should be thrown for a default not in options")
        except ValueError as e:
            pass

        self.assertTrue(r.validate("a"), "a should be a valid value") 

        self.assertFalse(r.validate("x"), "x should not be a valid value") 

    def testConcreteParameter(self):
        t = Categorical("v1", "categorical", "-v1", "default", ["a", "b", "c", "default"])

        try:
            c = ConcreteParameter(t, "a")
        except ValueError:
            self.assertTrue(False, "Value error should not be thrown for valid value")

        try:
            c = ConcreteParameter(t, "w")
            self.assertTrue(False, "Value error should have been thrown for invalid value")
        except ValueError:
            pass


        t = Integer("v1", "integer", "-v1", 1, 0, 2)

        try:
            c = ConcreteParameter(t, 0)
        except ValueError:
            self.assertTrue(False, "Value error should not be thrown for valid value")

        try:
            c = ConcreteParameter(t, "d")
            self.assertTrue(False, "Value error should have been thrown for invalid value")
        except ValueError:
            pass


        t = Real("v1", "real", "-v1", 1.0, 0.0, 2.0)

        try:
            c = ConcreteParameter(t, 0.0)
        except ValueError:
            self.assertTrue(False, "Value error should not be thrown for valid value")

        try:
            c = ConcreteParameter(t, "d")
            self.assertTrue(False, "Value error should have been thrown for invalid value")
        except ValueError:
            pass

        self.assertTrue(c.toFlags() == "-v1 0.0", "Flags not constructed correctly")


    def testConfigurationDefinition(self):
        self.assertTrue(len(self.configurationDefinition.parameters) == 13, "ConfigurationDefinition created the wrong number of parameters") 
        self.assertTrue(len(self.configurationDefinition.constraints) == 4, "ConfigurationDefinition created the wrong number of constraints.")
        
        p = None 
        for param in self.configurationDefinition.parameters:
            if param.name == "greedy":
                p = param 

        self.assertTrue(p != None, "the 'greedy' parameter is missing from ConfigurationDefinition")

        #Test our constraints 
        
        #valid values for the defined parameters
        vals =  {
                    "iterations":50,
                    "samples":4,
                    "mean1":0.0,
                    "std1":1.0,
                    "mean2":0.0,
                    "std2":1.0,
                    "mean3":0.0,
                    "std3":1.0,
                    "mean4":0.0,
                    "std4":1.0,
                    "mean5":0.0,
                    "std5":1.0,
                    "greedy":"True"
                }

        confDef = self.configurationDefinition
        try:
            conf = Configuration(confDef, vals)
        except MissingParameterError as e:
            self.assertTrue(False, "No parameter was expected to be missing")

        self.assertFalse(conf.valid, "mean1 cannot equal mean2")

        vals =  {
                    "iterations":50,
                    "samples":4,
                    "mean1":0.0,
                    "std1":1.0,
                    "mean2":0.5,
                    "std2":1.0,
                    "mean3":0.0,
                    "std3":1.0,
                    "mean4":0.0,
                    "std4":1.0,
                    "mean5":0.0,
                    "std5":1.0,
                    "greedy":"True"
                }

        conf = Configuration(confDef, vals)
        self.assertTrue(conf.valid, "vals should meet the example constraints ")

    def testConfiguration(self):
        confDef = self.configurationDefinition
        vals =  {
                    "iterations":50,
                    "samples":4,
                    "mean1":0.0,
                    "std1":1.0,
                    "mean2":0.5,
                    "std2":1.0,
                    "mean3":0.0,
                    "std3":1.0,
                    "mean4":0.0,
                    "std4":1.0,
                    "mean5":0.0,
                    "std5":1.0,
                    "greedy":"True"
                }

        conf = Configuration(confDef, vals)

        self.assertTrue(conf.valid, "vals should represent a valid configuration")

        expectedFlags = "-g True -i 50 -m1 0.0 -m2 0.5 -m3 0.0 -m4 0.0 -m5 0.0 -s 4 -s1 1.0 -s2 1.0 -s3 1.0 -s4 1.0 -s5 1.0" 
        self.assertTrue(expectedFlags == conf.toFlags(), "the configuration did not produce the expected flags. Actual {0} Expected {1}".format(conf.toFlags(), expectedFlags))

        vals =  {
                    "iterations":50,
                    "samples":4,
                    "mean1":0.0,
                    "std1":1.0,
                    "mean2":0.0,
                    "std2":1.0,
                    "mean3":0.0,
                    "std3":1.0,
                    "mean4":0.0,
                    "std4":1.0,
                    "mean5":0.0,
                    "std5":1.0,
                    "greedy":"True"
                }

        conf = Configuration(confDef, vals)

        self.assertFalse(conf.valid, "vals should not represent a valid configuration")

        vals =  {
                    "iterations":50,
                    "samples":4,
                    "mean1":0.0,
                    "std1":1.0,
                    "mean2":0.0,
                    "std2":1.0,
                    "mean3":0.0,
                    "std3":1.0,
                    "mean4":0.0,
                    "std4":1.0,
                    "mean5":0.0,
                    "std5":1.0
                }

        try:
            conf = Configuration(confDef, vals)
            self.assertFalse(True, "vals should be detected as missing a parameter")
        except MissingParameterError:
            pass

        

        







