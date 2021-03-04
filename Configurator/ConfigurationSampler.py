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

"""
This class is responsible for producing new configurations to be run with the algorithm. Similarly, it is responsible for using a model to choose the next configuration to be used with an algorithm.
"""

class ConfigurationSampler:

    #should parse the config definition file, provide any tools required by the models for generation, and provide methods for validating configs produced by the model 
    
    #Returns a new Configuration based on the provided features 
    #Uses the underlying model, must aquire the model before generating
    def generate(features):
        pass