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
from Configurator.Characterizer import Characterizer

"""
Sanity checks for our Characterizer
"""
#TODO: can we really have too many tests?

class TestCharacterizer(unittest.TestCase):

    def setUp(self):
        pass 

    def tearDown(self):
        pass

    def testOutput(self):
        result = dict() 
        result["solutions"] = [
                {   "solution":[ 0.045, 2340.3, 1.0],
                    "quality":100
                },
                {   "solution":[ 0.10, 30.33, 1.0],
                    "quality":92
                },
                {   "solution":[ 0.045, 2340.3, 1.0],
                    "quality":100
                },
                {   "solution":[ 0.10, 30.33, 1.0],
                    "quality":92
                },
                {   "solution":[ 0.045, 2340.3, 1.0],
                    "quality":100
                },
                {   "solution":[ 0.10, 30.33, 1.0],
                    "quality":92
                },
                {   "solution":[ 0.045, 2340.3, 1.0],
                    "quality":100
                },
                {   "solution":[ 0.10, 30.33, 1.0],
                    "quality":92
                },
                {   "solution":[ 0.045, 2340.3, 1.0],
                    "quality":100
                },
                {   "solution":[ 0.10, 30.33, 1.0],
                    "quality":92
                },
                {   "solution":[ 0.045, 2340.3, 1.0],
                    "quality":100
                },
                {   "solution":[ 0.10, 30.33, 1.0],
                    "quality":92
                }
            ]

        result["state"] = [
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ],
                [ 
                    {   "solution":[ 0.045, 2340.3, 1.0],
                        "quality":100
                    },
                    {   "solution":[ 0.10, 30.33, 1.0],
                        "quality":92
                    }
                ]
            ]

        c = Characterizer(12345) 
        print(c.characterize(result))