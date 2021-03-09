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
from typing import List


class ConfigurationDefinition:
    #defintions should be a dictionary generated from the user provided json 
    def __init__(self, definitions: dict):

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

    def validate(self, configuration:"Configuration") -> bool:
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
    
    def __init__(self, expression: str):
        self.expression = expression 
        self.operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
            ast.Div: op.truediv, ast.Lt: op.lt, ast.Gt:op.gt, ast.LtE:op.le, 
            ast.GtE:op.ge, ast.Eq:op.eq, ast.NotEq:op.ne, ast.And:op.and_, ast.Or:op.or_,
            ast.USub:op.neg}

    def test(self, config:"Configuration") -> bool:
        expr = self.expression 
        for k in config.values:
            expr = expr.replace("${0}".format(k), str(config.values[k].value)) 

        result = self.__eval(ast.parse(expr, mode='eval').body)

        if not isinstance(result, bool):
            raise ValueError("Constrains should evaluate to True or False") 

        return result 

    #return type, and type of node is dynamic
    #usually accepts an ast.AST and returns another but somtimes returns a literal 
    #ex when the node represents some constant, it returns the constant, which could be one of many types 
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
    def __init__(self,name: str, type: str, flag:str):
        self.name = name 
        self.type = type 
        self.flag = flag 

        self.__validateIdentifiers()
        
    #Validates the parameter definition
    def __validateIdentifiers(self) -> None:
        #Not really much we can do yet, but can't hurt to make sure we get strings
        if type(self.name) != str or type(self.flag) != str or type(self.type) != str:
            raise ValueError("ValueError: name, type, and flag should be strings")

#for defining real valued parameters
class Real(ParameterDefinition):
    def __init__(self,name:str, type:str, flag:str, default:float, lower:float, upper:float):
        super(Real, self).__init__(name, type, flag) 
        self.default = default 
        self.lower = lower 
        self.upper = upper 
        self.__validateDomain()

    def __validateDomain(self) -> None:
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

    def validate(self, value:float) -> bool:
        return type(value) == float and value >= self.lower and value <= self.upper


#for defining integer valued parameters
class Integer(ParameterDefinition):
    def __init__(self,name:str, type:str, flag:str, default:int, lower:int, upper:int):
        super(Integer, self).__init__(name, type, flag) 
        self.default = default 
        self.lower = lower 
        self.upper = upper 
        self.__validateDomain()

    def __validateDomain(self) -> None:
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

    def validate(self, value:int) -> bool:
        return type(value) == int and value >= self.lower and value <= self.upper

#for defining categorical parameters
class Categorical(ParameterDefinition):
    def __init__(self,name:str, type:str, flag:str, default:str, options:List[str]):
        super(Categorical, self).__init__(name, type, flag) 
        self.options = options
        self.default = default
        self.__validateDomain()

    def __validateDomain(self)->None:
        for opt in self.options:
            if type(opt) != str:
                raise ValueError("ValueError: Categorical options must be strings")

        if self.default not in self.options:
            raise ValueError("ValueError: A categorical default must be from the provided options")  

    def validate(self, value:str)->bool:
        return type(value) == str and value in self.options

#a specific value of a parameter
class ConcreteParameter:
    #Values type depends on the type of parameter, float for Real, int for Integer, etc
    def __init__(self, type:ParameterDefinition, value):
        self.type = type 
        self.value = value 
        if not self.type.validate(value):
            raise ValueError("Invalid value ({0}) for parameter {1}".format(value, type.name))
            

    def toFlags(self)->str:
        return "{0} {1}".format(self.type.flag, self.value)


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
    def __init__(self, configDef: ConfigurationDefinition, values: dict):
        
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
    def toFlags(self) -> str:
        components = [self.values[x].toFlags() for x in self.values]
        components.sort() #make the order of flags consistent 

        return " ".join(components).strip() 
