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
This class is responsible for collecting runs of the target algorithm. 
"""

#TODO: uses Algorithm to perform runs, we want algorithm.run to be called in a separate thread 
#TODO: needs a ConfigurationSampler, and a LandscapeCharacterizer 
#both a required by algorithm to actually perform a run 

#runner just needs to collect all the required runs and pass the data up 

class Runner:
    def schedule(numNewConfigs, ConfSampler, configsToReRun):
        #TODO: use a thread 
        pass 