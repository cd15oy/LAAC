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

from typing import List
from Configurator.ConfigurationDefinition import ConfigurationDefinition
from Configurator.ConfigurationDB import ConfigurationDB
import threading
import numpy as np
from numpy import ndarray
import torch 
from math import isfinite
from random import Random,seed as setPythonSeed
import os

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
    
    #LAAC will provide the configurationDb to the model
    #the ConfigurationDB will contain information about the tested configurations, the runs performed with them, and which configurations respresent desirable output 
    #update is responsible for selecting useful information from the DB, and updating the model to produce better predictions
    def update(self, configs:ConfigurationDB) -> None:
        self.lock.acquire()
        self._update(configs) 
        self.lock.release()

    #Model implementations must implement this method to be used by LAAC
    def _generate(self, features:ndarray) -> dict:
        raise NotImplementedError

    #Model implementations must provide a method for updating themselves from a ConfigurationDB 
    def _update(self, configs:ConfigurationDB) -> None:
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

class _NeuralNetworkModel(torch.nn.Module):
    def __init__(self, inputSize:int, configDef:ConfigurationDefinition, cpu:bool=False):
        super(_NeuralNetworkModel, self).__init__()
    
        #construct the network to train for regression 

        self.input = torch.nn.Sequential(
                            torch.nn.Linear(inputSize, 500),
                            torch.nn.Hardtanh(-1,1)
                        )
        
        self.features = torch.nn.Sequential(
                            torch.nn.Linear(500, 500),
                            torch.nn.Hardtanh(-1,1),
                            # torch.nn.Linear(300, 300),
                            # torch.nn.Hardtanh(-1,1),
                            # torch.nn.Linear(300, 500),
                            # torch.nn.Hardtanh(-1,1)
                        )

        #construct regressors (and possibly classifiers) for each parameter to predict
        self.output = []

        for param in configDef.parameters:
            if param.type == "real" or param.type == "integer":
                head = torch.nn.Sequential(
                            torch.nn.Linear(500, 1),
                            torch.nn.Hardtanh(-1,1)
                        )
                criteria = torch.nn.MSELoss()
                self.output.append((param, head, criteria))
            if param.type == "categorical":
                head = torch.nn.Sequential(
                            torch.nn.Linear(500, len(param.options))
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
    def __init__(self, inputSize:int, configDef:ConfigurationDefinition, seed:int, cpu:bool=False):
        super(NeuralNetwork, self).__init__() 
        self.rng = Random(seed) 
        #self.device = torch.device("cuda:0" if torch.cuda.is_available() and not cpu else "cpu")
        #A bunch of stuff to make sure pytorch is reproducible 
        #Commenting this out may improve performance in some cases 
        torch.set_deterministic(True)
        os.environ['PYTHONHASHSEED'] = str(seed)
        setPythonSeed(seed)
        torch.manual_seed(self.rng.randint(0,4000000000))
        torch.cuda.manual_seed_all(self.rng.randint(0,4000000000))
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        np.random.seed(self.rng.randint(0,4000000000))

        self.predictor = _NeuralNetworkModel(inputSize, configDef) 
        self.predictor.eval()
        #self.predictor.to(self.device)

        #TODO: make training paramters, network arch, etc configurable
        #num examples drawn from dataset
        self.batchSize = 32
        self.lr = 0.0001
        self.momentum = 0.001
        self.optimizer =torch.optim.RMSprop(self.predictor.parameters(), lr=self.lr, momentum=self.momentum)
         

    #train the model
    #TODO: something more efficient
    def _update(self, configs:ConfigurationDB) -> None:
        examples = []
        for prob in configs.records:
            for rcrd in configs.records[prob]:
                record = configs.records[prob][rcrd]
                if record.desirable():
                    for run in record.getRuns():
                        examples.append(run) 
        
        #sample desirable runs 
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
        for i, data in enumerate(examples):
            #data = dataset.__get__(i) #enumerate(dataset):
            pattern,target = data  

            #calculated and propagate loss for all outputs
            pattern = torch.from_numpy(pattern).unsqueeze(0) 

            output = self.predictor(pattern.float())
            for out in output:
                targetVal = target.values[out[0].name].value 

                if out[0].type == "real" or out[0].type == "integer":
                    targetVal = [self.__normalizeNumeric(targetVal, out[0])]
                elif out[0].type == "categorical":
                    targetVal = self.__categoryToPred(targetVal, out[0])

                targetVal = torch.tensor(targetVal).unsqueeze(0)

                criteria = out[2]
                if loss is None:
                    loss = criteria(out[1], targetVal) 
                else:
                    loss += criteria(out[1], targetVal)
            
            

            if (1+i) % self.batchSize == 0:
                loss = loss/self.batchSize
                loss.backward()
                print(loss.item())
                optimizer.step()
                optimizer.zero_grad()
                loss = None

        #optimizer.step()
        # optimizer.zero_grad()


        self.predictor.eval()
        

    #generate a config from the provided features
    def _generate(self, features:ndarray) -> dict:
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

    #TODO: update this to better handle nans, infs, large numbers, and potential roundoff errors
    def __cleanInput(self,x):

        featureArray = np.nan_to_num(x, nan=0, posinf=3.4028237e16, neginf=-3.4028237e16)

        featureArray = np.asarray(featureArray, np.float32)
    
        avg = np.mean(featureArray, axis=0)
        std = np.std(featureArray, axis=0) 
        std[std == 0] = 0.000001
        avg = np.nan_to_num(avg)
        featureArray = ((featureArray - avg)/std)
        featureArray = np.nan_to_num(featureArray)

        

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