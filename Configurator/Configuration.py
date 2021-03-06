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
 
from Configurator.ConfigurationDefinition import ConcreteParameter
"""
Indicates a required parameter value is missing
"""
class MissingParameterError(Exception):
    pass

"""
This class represents a concrete Configuration. That is, a set of hyper parameters used with the optimizer and all data collected about the optimizer and the use of those parameters. 
"""

class Configuration:
    #configDef should be a ConfigurationDefinition object, initialized from the user provided JSON
    #values should be a dictionary define the value for each parameter. The keys should be the parameter names .
    def __init__(self, configDef, values):
        
        #the configuration definition acts like a specification, it is used to validate instances of Configuration 
        self.configurationDefinition = configDef
        
        #stores the concrete parameter, keyed by their names
        self.values = dict() 

        #First we need to construct a concrete parameter for each value 
        for param in self.configurationDefinition.parameters:
            if param.name not in values:
                raise MissingParameterError("A configuration is missing the parameter {0}".format(param.name))

            self.values[param.name] = ConcreteParameter(param, values[param.name])

        #now that all of the Concrete parameters are constructed, we need to validate this configuration 
        self.valid = True

        for constraint in self.configurationDefinition.constraints:
            if not constraint.test(self):
                self.valid=False 
                
        #This will be filled in later once the configuration is actually run 
        self.features = None 
        self.rawResult = None 
        self.seed = None #Note this is the algorithm seed, it is specific to this execution of the algorithm. This is not the instance seed (if it exists)
        self.threadID = None

    #Produces a string of command line arguments which can be passed on to Algorithm
    def toFlags(self):
        components = [self.values[x].toFlags() for x in self.values]
        components.sort() #make the order of flags consistent 

        return " ".join(components).strip() 

