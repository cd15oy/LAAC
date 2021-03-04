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
This file should act as a wrapper to the algorithm to configure. For demonstration purposes a simple random search is included with this repository. 
"""

from subprocess import Popen, PIPE 
import sys 

#argv[1] will contain a thread ID. This could be used to ensure that multiple simultaneous runs of the algorithm will output to different locations 
#argv[2] will contain a seed 
#argv[3] and onward will contain flags for the underlying algorithm, here we're ensuring that LAAC uses the same naming and formatting conventions as the underlying algorithm 
#in practice it may be necessary to parse the arguments passed to target-algorithm.py and then provide them to the underlying optimizer in the correct format 

if len(sys.argv) > 3:
    args = " ".join(sys.argv[3:]) 
    args += " "
else:
    args = ""

cmd = "python3 RandomSearch/python/randomSearch.py {0}-aSeed {1}".format(args, sys.argv[2]) 

print(cmd)

io = Popen(cmd.split(" "), stdout=PIPE, stderr=PIPE)

#wait for the process to finish 
_stdout,_stderr = io.communicate() 

#here you would do any error checking or validation you need
#then reformat the target algorithms output to the JSON required by LAAC 

#randomsearch already produces the JSON we need, so we just print it
print("RESULTS FOLLOW") #LAAC will interpret everything after the line RESULTS FOLLOW as the algorithm output 
print(_stdout.decode()) 

#If you're having issues the first place to check would be the output on stderr
#print(_stderr.decode()) 