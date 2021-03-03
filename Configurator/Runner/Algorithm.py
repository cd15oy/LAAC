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
This class represents the target algorithm. 
"""


#TODO: this will also need to make a call to Popen to execute target-runner with the passed parameters 
#This allows for flexibility, target-runner can be any sort of script you choose 
#TODO: gets a configuration sampler, which is used to choose the "next" params to use 
#ends up making multiple calls to target runner with Popen, passing arguments and state to continue the run where it left off 
#TODO: needs a landscapeCharacterizer in order to obtain the features which the sampler needs 
#will return a config sequence, along with features for each config, qualities, all the information we need about the sequence 