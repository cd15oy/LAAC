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

#compares feature vectors
#in rare cases curve_fit, which is used by RoC will produe different results when given the same input 
#this is likely a result of using minpack, and well beyond out ability to control 
#so we don't require the RoC features to be identical in feature vectors 
#I think its likely related to whether or not the provided "curve" is to flat 
#since RoC assumes a steep curve at first followed by a flattened section
from math import isfinite, isnan
from unittest import TestCase

from numpy.lib.ufunclike import isneginf, isposinf
from numpy import ndarray


def compareFeatures(self:TestCase, f1:ndarray, f2:ndarray):
    for i,(x,y) in enumerate(zip(f1,f2)):
        #only assert for non-RoC features 
        if not (i >= 69 and i <= 72) and not (i >= 74 and i <= 77):
            
            if isfinite(x) and isfinite(y):
                self.assertEqual(x,y, "Characterizing the same solution twice should yield the same result. Element {} was different".format(i))

            else:
                if isnan(x):
                    self.assertTrue(isnan(x) and isnan(y), "Outputted feature values should match.") 
                elif isposinf(x):
                    self.assertTrue(isposinf(x) and isposinf(y), "Outputted feature values should match.") 
                elif isneginf(x):
                    self.assertTrue(isneginf(x) and isneginf(y), "Outputted feature values should match.")
                else:
                    self.assertTrue(False, "I don't know what that value is. Value {} Element {}".format(x,i))