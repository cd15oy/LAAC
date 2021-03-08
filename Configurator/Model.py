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
import threading
from numpy import ndarray

""" 
This class defines a method for selecting the "next" configuration to be used with the algorithm
"""
class Model:

    #One model may be shared among multiple workers which are waiting on results from the target algorithm 
    #Since models may be statefull, we need to ensure that only one worker is able to use the model at a time, thus Locking is required
    def __init__(self):
        self.lock = threading.Lock()

    #This method should return a dictionary where the keys are the parameter names and the values are the parameter values
    def generate(self, features:ndarray) -> dict:
        self.lock.acquire() 
        config = self._generate(features) 
        self.lock.release() 
        return config

    #Model implementations must implement this method to be used by LAAC
    def _generate(self, features:ndarray) -> dict:
        pass
    
    #LAAC will provide the configurationDb to the model
    #the ConfigurationDB will contain information about the tested configurations, the runs performed with them, and which configurations respresent desirable output 
    #update is responsible for selecting useful information from the DB, and updating the model to produce better predictions
    def update(self, configs:ConfigurationDB) -> None:
        pass

#TODO: random sampler as a testing/proof of concept for fleshing out 

#TODO: NN backed model 