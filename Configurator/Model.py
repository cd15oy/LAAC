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

from copy import deepcopy
from io import BytesIO
import pickle
from typing import Dict, List
from Configurator.ConfigurationDefinition import ConfigurationDefinition
from Configurator.ConfigurationDB import ConfigurationDB
import numpy as np
from numpy import ndarray
from math import isfinite
from random import Random,seed as setPythonSeed
import torch


#TODO: remove model level locking, its moved up to  the config generator
""" 
This class defines a method for selecting the "next" configuration to be used with the algorithm
"""
class Model:

    #This method should return a dictionary where the keys are the parameter names and the values are the parameter values
    def generate(self, features:ndarray) -> dict:
        config = self._generate(features) 
        return config
    
    #LAAC will provide the configurationDb to the model
    #the ConfigurationDB will contain information about the tested configurations, the runs performed with them, and which configurations respresent desirable output 
    #update is responsible for selecting useful information from the DB, and updating the model to produce better predictions
    def update(self, configs:ConfigurationDB) -> None:
        self._update(configs) 

    #Model implementations must implement this method to be used by LAAC
    def _generate(self, features:ndarray) -> dict:
        raise NotImplementedError

    #Model implementations must provide a method for updating themselves from a ConfigurationDB 
    def _update(self, configs:ConfigurationDB) -> None:
        raise NotImplementedError

    #returns a dict defining the internal state of the model 
    def state(self) -> Dict:
        raise NotImplementedError

    #loads the provided state into the model.
    def load(self, state:Dict) -> None:
        raise NotImplementedError

#purely random configuration sampling
class LatinHyperCube(Model):
    def __init__(self, bufferSize:int, configDef:ConfigurationDefinition, seed:int):
        super(LatinHyperCube, self).__init__() 
        self.configs = [] 
        self.configDef = configDef 
        self.bufferSize = bufferSize
        self.rng = Random(seed) 

    #this is a purely random sampler, no updating is possible
    def _update(self, configs:ConfigurationDB) -> None:
        pass 


    #Simple latin hyper-cube sampling
    def _generate(self, features:ndarray) -> dict:

        #If needed generate a new random sample 
        if len(self.configs) == 0:
            #generate a sample of bufferSize for each param
            paramSamples = []

            for param in self.configDef.parameters:
                if param.type == "real":
                    vals = self.__generateReals(self.bufferSize, param.lower, param.upper)
                elif param.type == "integer":
                    vals = self.__generateInts(self.bufferSize, param.lower, param.upper)
                elif param.type == "categorical":
                    vals = self.__generateCategorical(self.bufferSize, param.options)

                paramSamples.append([(param.name,x) for x in vals]) 

            #param samples is a list of lists of random samples for each parameter
            #each sublist was shuffled by the generate functions 

            #now we just zip them up to create new random configs
            tmpConfs = zip(*paramSamples) 
            for tmpConf in tmpConfs:
                conf = dict() 
                for param in tmpConf:
                    conf[param[0]] = param[1] 
                self.configs.append(conf) 
            
        return self.configs.pop()

    def __generateReals(self, n:int, lower:float, upper:float) -> List[float]:
        binWidth = (upper - lower)/n
        vals = [] 

        l = lower 
        for i in range(n):
            vals.append((self.rng.random()*binWidth) + l) 
            l += binWidth 

        self.rng.shuffle(vals) 
        return vals

    def __generateInts(self, n:int, lower:int, upper:int) -> List[int]:
        return [int(x) for x in self.__generateReals(n, lower, upper)]

    def __generateCategorical(self, n:int, choices:List[str]):
        vals = [choices[x%len(choices)] for x in range(n)]
        self.rng.shuffle(vals)

        return vals 

    #returns a dict defining the internal state of the model 
    def state(self) -> Dict:
        ret = dict() 
        ret["configs"] = self.configs 
        ret["confDef"] = pickle.dumps(self.configDef)
        ret["bufferSize"] = self.bufferSize 
        ret["rng"] = pickle.dumps(self.rng)
        return ret

    #loads the provided state into the model.
    def load(self, state:Dict) -> None:
        state = deepcopy(state) 
        self.configs = state["configs"]
        self.configDef = pickle.loads(state["confDef"])
        self.bufferSize = state["bufferSize"] 
        self.rng = pickle.loads(state["rng"])

class _NeuralNetworkModel(torch.nn.Module):
    def __init__(self, inputSize:int, configDef:ConfigurationDefinition, cpu:bool=True):
        super(_NeuralNetworkModel, self).__init__()
    
        #construct the network to train for regression 

        self.input = torch.nn.Sequential(
                            torch.nn.Linear(inputSize, 500),
                            torch.nn.ELU()
                        )
        
        self.features = torch.nn.Sequential(
                            torch.nn.Linear(500, 250),
                            torch.nn.ELU(),
                            torch.nn.Linear(250, 125),
                            torch.nn.ELU(),
                            torch.nn.Linear(125, 50),
                            torch.nn.ELU()
                        )

        #construct regressors (and possibly classifiers) for each parameter to predict
        self.output = []

        for param in configDef.parameters:
            if param.type == "real" or param.type == "integer":
                head = torch.nn.Sequential(
                            torch.nn.Linear(50, 1),
                            torch.nn.Tanh()
                        )
                criteria = torch.nn.MSELoss()
                self.output.append((param, head, criteria))
            if param.type == "categorical":
                head = torch.nn.Sequential(
                            torch.nn.Linear(50, len(param.options))
                )
                criteria = torch.nn.CrossEntropyLoss() 
                self.output.append((param, head, criteria))

    def forward(self, x):
        x = self.input(x) 
        x = self.features(x) 
        out = [] 
        for param,head,criteria in self.output:
            out.append((param,head(x),criteria))
        
        return out


class NeuralNetwork(Model):
    
    def __init__(self, inputSize:int, configDef:ConfigurationDefinition, seed:int, cpu:bool=True):
        super(NeuralNetwork, self).__init__() 

        self.origSeed = seed 
        self.rng = Random(seed) 
        #TODO: enable GPU accelerated training
        #self.device = torch.device("cuda:0" if torch.cuda.is_available() and not cpu else "cpu")
        torch.cuda.manual_seed_all(self.rng.randint(0,4000000000))
        #A bunch of stuff to make sure pytorch is reproducible 
        #Commenting this out may improve performance in some cases 
        torch.set_deterministic(True)
        #os.environ['PYTHONHASHSEED'] = str(seed)
        setPythonSeed(seed)
        torch.manual_seed(self.rng.randint(0,4000000000))
        
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        np.random.seed(self.rng.randint(0,4000000000))

        self.predictor = _NeuralNetworkModel(inputSize, configDef) 
        self.predictor.eval()
        #self.predictor.to(self.device)

        #TODO: make training paramters, network arch, etc configurable
        #num examples drawn from dataset
        # self.batchSize = 128
        # self.lr = 0.001
        # self.momentum = 0.1
        # self.epochs = 5
        # self.optimizer =torch.optim.RMSprop(self.predictor.parameters(), lr=self.lr, momentum=self.momentum)
        self.batchSize = 32
        self.lr = 0.00000001
        self.momentum = 0.000001
        self.epochs = 20
        self.optimizer =torch.optim.SGD(self.predictor.parameters(), lr=self.lr, momentum=self.momentum)
        self.history = [] 
         

    #train the model
    #TODO: something more efficient
    def _update(self, configs:ConfigurationDB) -> None:
        #TODO???
        torch.manual_seed(self.rng.randint(0,4000000000))
        np.random.seed(self.rng.randint(0,4000000000))
        setPythonSeed(self.rng.randint(0,4000000000))
        #torch.cuda.manual_seed_all(self.rng.randint(0,4000000000))
        #######
        examples = []

        for run in configs.getDesirables():
            examples.append(run) 
        
        #sample desirable runs #TODO: use random.sample, and resample on each epoch , alternatively we can stick with choice, and replace epochs with k, 
        #it would be more fine grained control over how much training is done
        examples = self.rng.choices(examples, k=128)
        
        #convert the runs into training examples 
        featureArray = []
        configs = [] 
        for run in examples:
            for i,c in enumerate(run.configurations[1:]):
                featureArray.append(run.configurations[i].features)
                configs.append(c)
    
        featureArray = self.__cleanInput(featureArray)

        examples = [x for x in zip(featureArray,configs)]
  
        self.predictor.train()

        optimizer = self.optimizer 
        optimizer.zero_grad()
        loss = None

        lossList = [] 

        for e in range(self.epochs):
            self.rng.shuffle(examples)

            for i in range(0, len(examples), self.batchSize):
                data = examples[i:i+self.batchSize]

                pattern = np.asarray([x[0] for x in data])
                targets = [x[1] for x in data]
            #for i, data in enumerate(examples):
                #data = dataset.__get__(i) #enumerate(dataset):
                #pattern,target = data  

                #calculated and propagate loss for all outputs
                pattern = torch.from_numpy(pattern)

                outputs = self.predictor(pattern.float())

                for out in outputs:
                    targetVals = [] 

                    for config in targets:
                        targetVal = config.values[out[0].name].value 

                        if out[0].type == "real" or out[0].type == "integer":
                            targetVal = [self.__normalizeNumeric(targetVal, out[0])]
                        elif out[0].type == "categorical":
                            targetVal = self.__categoryToPred(targetVal, out[0])

                        targetVals.append(targetVal) 

                    targetVals = torch.tensor(targetVals)

                    criteria = out[2]
                    if loss is None:
                        loss = criteria(out[1], targetVals) 
                    else:
                        loss += criteria(out[1], targetVals)
                
                


                loss = loss/len(data)
                loss.backward()
                print(f"loss: {loss.item()}              \r", end="")
                optimizer.step()
                optimizer.zero_grad()
                lossList.append(loss.item()) 
                loss = None

        self.predictor.eval()
        print("")
        self.history.append(lossList)
        

    #generate a config from the provided features
    def _generate(self, features:ndarray) -> dict:
         #TODO???
        torch.manual_seed(self.rng.randint(0,4000000000))
        np.random.seed(self.rng.randint(0,4000000000))
        setPythonSeed(self.rng.randint(0,4000000000))
        #torch.cuda.manual_seed_all(self.rng.randint(0,4000000000))
        #####
        dta = self.__cleanInput(np.asarray([features],dtype=np.float32))
        dta = torch.from_numpy(dta)
        #dta.to(self.device) 

        
        preds = self.predictor(dta)
        ret = dict() 

        for pred in preds:
            if pred[0].type == "real":
                val = self.__denormalizeNumeric(pred[1][0].item(), pred[0])
                ret[pred[0].name] = val
            elif pred[0].type == "integer":
                val = self.__denormalizeNumeric(pred[1][0].item(), pred[0])
                ret[pred[0].name] = int(val)
            elif pred[0].type == "categorical":
                ret[pred[0].name] = self.__predToCategory(pred[1][0], pred[0])

        return ret

    #returns a dict defining the internal state of the model 
    def state(self) -> Dict:
        
        state = dict() 
        state["rng"] = pickle.dumps(self.rng)
        #state["nnParams"] = pickle.dumps(self.predictor.state_dict()) 
        state["batchSize"] = self.batchSize 
        state["lr"] = self.lr
        state["momentum"] = self.momentum 
        state["epochs"] = self.epochs 
        #state["optimizerParams"] = pickle.dumps(self.optimizer.state_dict()) 
        state["origSeed"] = self.origSeed 
        #state["predictor"] = pickle.dumps(self.predictor) 
        #state["optimizer"] = pickle.dumps(self.optimizer)
        nnStateBytes = BytesIO()
        torch.save({'predictor':self.predictor.state_dict(), 'optimizer':self.optimizer.state_dict()}, nnStateBytes, pickle_module=pickle)
        nnStateBytes.seek(0)
        state["torchParams"] = pickle.dumps(nnStateBytes) 
        
        return state 

    #loads the provided state into the model.
    def load(self, state:Dict) -> None:
        state = deepcopy(state)
        self.rng = pickle.loads(state["rng"])
        self.origSeed = state["origSeed"] 
        self.batchSize = state["batchSize"]
        self.lr = state["lr"] 
        self.momentum = state["momentum"]
        self.epochs = state["epochs"] 
        
        nnState = torch.load(pickle.loads(state["torchParams"])) 
        self.predictor.load_state_dict(nnState["predictor"]) 
        self.optimizer.load_state_dict(nnState["optimizer"])
        self.predictor.eval()

    #TODO: update this to better handle nans, infs, large numbers, and potential roundoff errors
    def __cleanInput(self,x):

        #featureArray = np.nan_to_num(x, nan=0, posinf=3.4028237e16, neginf=-3.4028237e16)
        featureArray = np.nan_to_num(x, nan=0, posinf=0, neginf=0)

        featureArray = np.asarray(featureArray, np.float32)
    
        avg = np.mean(featureArray, axis=0)
        std = np.std(featureArray, axis=0) 
        std[std == 0] = 0.000001
        avg = np.nan_to_num(avg, nan=0, posinf=0, neginf=0)
        featureArray = ((featureArray - avg)/std)
        featureArray = np.nan_to_num(featureArray, nan=0, posinf=0, neginf=0)

        return featureArray

            
    def __denormalizeNumeric(self, value, param):
        if isfinite(value): #TODO: different nan handling?
            val = value
            val = (val + 1.0)/2.0 
            val = (val*(param.upper - param.lower)) + param.lower
            return val
        else:
            return param.default

    def __normalizeNumeric(self, value, param):
        if isfinite(value): #TODO: different nan handling?
            val = value
        else:
            val = param.default
        val = (val - param.lower)/(param.upper - param.lower) 
        val = (val*2.0) - 1.0
        return val 

    def __predToCategory(self, value, param):
        return param.options[torch.argmax(value[0])] 

    def __categoryToPred(self, value, param):
        return param.options.index(value)
