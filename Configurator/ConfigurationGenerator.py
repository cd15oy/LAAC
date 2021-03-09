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

from Configurator.ConfigurationDB import ConfigurationDB
from typing import List
from Configurator.ConfigurationDefinition import ConfigurationDefinition,Configuration
from Configurator.Model import LatinHyperCube
from numpy import ndarray

#TODO: all testing

#TODO: the method signatures here will likely change as we flesh out the system 
#ideally we want the Configuration generator to handle decisions about which underlying model to use
#testing/experimenting will help to work out what specific information the generator will need to make good decisions

"""
Responsible for acquiring configurations from a model or models, preprocessing/postprocessing, and validation of the config. 

In practice we will need two main methods, a way to generate initial configs, ie without features to predict from, and a way to select configs based on provided features. 
The underlying approaches will likely use combinations of predictions and random sampling, possibly applying constraints to either or both. Internally a ConfigurationGenerator
could be entirely random, could make use of/train multiple different models, etc. That logic should be contained in the ConfigurationGenerator, and the rest of LAAC should not need to be aware of the logic behind how configs are generated.
"""
class ConfigurationGenerator:
    def __init__(self, confDef:ConfigurationDefinition):
        self.confDef = confDef

    #TODO (maybe): instead of providing a single feature array to predict from, provide the feature arrays from all runs of the same sequence? 
    #We could provide the model with the average features of a random sample of the runs, leading to a number of possible inputs to the model = to #runs choose 1 +  # runs choose 2 + etc 
    #This might give the ConfigurationGenerator a way to make multiple attempts when a models predictions don't meet the constraints

    #generate a single new config without features 
    def _generate(self) -> Configuration:
        raise NotImplementedError    

    #process the provided features to produce a new configuration
    def _generate(self, features:ndarray) -> Configuration:
        raise NotImplementedError

    #updates the generation process based on the collected data 
    def update(self, confDB:ConfigurationDB) -> None:
        raise NotImplementedError
    

    #in some cases the "features" attached to a config may be None, for example when the configuration was invalid, and LAAC was told not to evaluate invalid configurations
    #this is just a wrapper to handle such cases
    def generate(self, features:ndarray= None) -> Configuration:
        if features is None:
            conf = self._generate() 
        else:
            conf = self._generate(features)

        return Configuration(self.confDef, conf)


"""
A purely random configuration generator. With this generator LAAC will simply perform a random sampling of the configuration space.
"""
class RandomGenerator(ConfigurationGenerator):
    def __init__(self, confDef:ConfigurationDefinition, seed:int):
        super(RandomGenerator,self).__init__(confDef) 
        self.model = LatinHyperCube(1000, confDef, seed) 

    #LatinHyperCube ignores features entirely, its a random sampler 
    def _generate(self) -> Configuration:
        return self.model.generate(None) 

    #LatinHyperCube ignores features entirely, its a random sampler
    def _generate(self, features:ndarray) -> Configuration:
        return self.model.generate(None) 

    #nothing to do here, this is a random sampler
    def update(self, confDB:ConfigurationDB) -> None:
        pass 


