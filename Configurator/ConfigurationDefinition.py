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
Parses and represents the user provided definition of valid configurations. 
"""
class ConfigurationDefinition:
    #defintions should be a dictionary generated from the user provided json 
    def __init__(self, definitions):

        #A list of parameter definitions 
        self.parameters = []

        for param in definitions["parameters"]:
            if param["type"] == "real": 
                self.parameters.append(Real(param["name"], param["type"], param["flag"],param["default"], param["lower"], param["upper"]))
            elif param["type"] == "integer":
                self.parameters.append(Integer(param["name"], param["type"], param["flag"], param["default"], param["lower"], param["upper"]))
            elif param["type"] == "categorical":
                self.parameters.append(Categorical(param["name"], param["type"], param["flag"], param["default"], param["options"]))
            else:
                raise ValueError("Invalid parameter type: {0}".format(param["type"]))

        #A list of constraints 
        self.constraints = [] 
        for constraint in definitions["constraints"]:
            self.constraints.append(Constraint(constraint))

    def validate(self, configuration):
        for constraint in self.constraints:
            if not constraint.test(configuration):
                return False 
        return True 


import ast
import operator as op
"""
Defines a constrain from an arithmetic expression 
"""
class Constraint:
    
    def __init__(self, expression):
        self.expression = expression 
        self.operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Lt: op.lt, ast.Gt:op.gt, ast.LtE:op.le, ast.GtE:op.ge, ast.Eq:op.eq, ast.NotEq:op.ne, ast.And:op.and_, ast.Or:op.or_}

    def test(self, config):
        expr = self.expression 
        for k in config.values:
            expr = expr.replace("${0}".format(k), str(config.values[k].value)) 

        result = self.__eval(ast.parse(expr, mode='eval').body)

        if not isinstance(result, bool):
            raise ValueError("Constrains should evaluate to True or False") 

        return result 


    def __eval(self,node):
        if isinstance(node, ast.Constant):
            return node.n
        elif isinstance(node, ast.BinOp): 
            return self.operators[type(node.op)](self.__eval(node.left), self.__eval(node.right))
        elif isinstance(node, ast.UnaryOp): 
            return self.operators[type(node.op)](self.__eval(node.operand))
        elif isinstance(node, ast.Compare): 
            return self.operators[type(node.ops[0])](self.__eval(node.left), self.__eval(node.comparators[0]))
        elif isinstance(node, ast.BoolOp): 
            return self.operators[type(node.op)](self.__eval(node.values[0]), self.__eval(node.values[1]))
        else:
            raise TypeError(node)

#Defines a general parameter 
class ParameterDefinition:
    def __init__(self,name, type, flag):
        self.name = name 
        self.type = type 
        self.flag = flag 

        self.__validateIdentifiers()
        
    #Validates the parameter definition
    def __validateIdentifiers(self):
        #Not really much we can do yet, but can't hurt to make sure we get strings
        if type(self.name) != str or type(self.flag) != str or type(self.type) != str:
            raise ValueError("ValueError: name, type, and flag should be strings")

#for defining real valued parameters
class Real(ParameterDefinition):
    def __init__(self,name, type, flag, default, lower, upper):
        super(Real, self).__init__(name, type, flag) 
        self.default = default 
        self.lower = lower 
        self.upper = upper 
        self.__validateDomain()

    def __validateDomain(self):
        try:
            self.default = float(self.default)
        except:
            raise ValueError("ValueError: For Reals default should be a float. Parameter: {0} Value: {1}".format(self.name, self.default))

        try:
            self.lower = float(self.lower)
        except:
            raise ValueError("ValueError: For Reals lower should be a float. Parameter: {0} Value: {1}".format(self.name, self.lower))

        try:
            self.upper = float(self.upper)
        except:
            raise ValueError("ValueError: For Reals upper should be a float. Parameter: {0} Value: {1}".format(self.name, self.upper))

        if self.lower >= self.upper:
            raise ValueError("ValueError: lower should be less than upper")

        if not (self.default <= self.upper and self.default >= self.lower):
            raise ValueError("ValueError: default should be between lower and upper")

    def validate(self, value):
        return type(value) == float and value >= self.lower and value <= self.upper


#for defining integer valued parameters
class Integer(ParameterDefinition):
    def __init__(self,name, type, flag, default, lower, upper):
        super(Integer, self).__init__(name, type, flag) 
        self.default = default 
        self.lower = lower 
        self.upper = upper 
        self.__validateDomain()

    def __validateDomain(self):
        if not type(self.default) == int:
            raise ValueError("ValueError: For Integers default should be an int. Parameter: {0} Value: {1}".format(self.name, self.default))

        if not type(self.lower) == int:
            raise ValueError("ValueError: For Integers lower should be an int. Parameter: {0} Value: {1}".format(self.name, self.lower))

        if not type(self.upper) == int:
            raise ValueError("ValueError: For Integers upper should be an int. Parameter: {0} Value: {1}".format(self.name, self.upper))

        if self.lower >= self.upper:
            raise ValueError("ValueError: lower should be less than upper")  

        if not (self.default <= self.upper and self.default >= self.lower):
            raise ValueError("ValueError: default should be between lower and upper")

    def validate(self, value):
        return type(value) == int and value >= self.lower and value <= self.upper

#for defining categorical parameters
class Categorical(ParameterDefinition):
    def __init__(self,name, type, flag, default, options):
        super(Categorical, self).__init__(name, type, flag) 
        self.options = options
        self.default = default
        self.__validateDomain()

    def __validateDomain(self):
        for opt in self.options:
            if type(opt) != str:
                raise ValueError("ValueError: Categorical options must be strings")

        if self.default not in self.options:
            raise ValueError("ValueError: A categorical default must be from the provided options")  

    def validate(self, value):
        return type(value) == str and value in self.options

#a specific value of a parameter
class ConcreteParameter:
    def __init__(self, type, value):
        self.type = type 
        self.value = value 
        if not self.type.validate(value):
            raise ValueError("Invalid value ({0}) for parameter {1}".format(value, type.name))
            

    def toFlags(self):
        return "{0} {1}".format(self.type.flag, self.value)