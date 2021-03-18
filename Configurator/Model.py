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

from Configurator.ConfigurationDefinition import ConfigurationDefinition
from Configurator.ConfigurationDB import ConfigurationDB
import threading
import numpy as np
from numpy import ndarray
from random import Random
import torch 
from math import isfinite

#TODO: all testing

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
#TODO: tests
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

    def __generateReals(self, n:int, lower:float, upper:float) -> list[float]:
        binWidth = (upper - lower)/n
        vals = [] 

        l = lower 
        for i in range(n):
            vals.append((self.rng.random()*binWidth) + l) 
            l += binWidth 

        self.rng.shuffle(vals) 
        return vals

    def __generateInts(self, n:int, lower:int, upper:int) -> list[int]:
        return [int(x) for x in self.__generateReals(n, lower, upper)]

    def __generateCategorical(self, n:int, choices:list[str]):
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
                            torch.nn.Linear(500, 300),
                            torch.nn.Hardtanh(-1,1),
                            torch.nn.Linear(300, 300),
                            torch.nn.Hardtanh(-1,1),
                            torch.nn.Linear(300, 500),
                            torch.nn.Hardtanh(-1,1)
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

class _Data(torch.utils.data.Dataset):
    def __init__(self, examples):
        super(_Data, self).__init__() 
        self.examples = examples

    def __len__(self):
        return len(self.examples) 

    def __getitem__(self, idx):
        data,target = self.examples[idx] 
        return data,target

class NeuralNetwork(Model):
    def __init__(self, inputSize:int, configDef:ConfigurationDefinition, seed:int, cpu:bool=False):
        super(NeuralNetwork, self).__init__() 
        self.rng = Random(seed) 
        torch.set_deterministic(True)
        torch.manual_seed(self.rng.randint(0,4000000000))
        #self.device = torch.device("cuda:0" if torch.cuda.is_available() and not cpu else "cpu")

        self.predictor = _NeuralNetworkModel(inputSize, configDef) 
        self.predictor.eval()
        #self.predictor.to(self.device)

        #TODO: make training paramters, network arch, etc configurable
        #num examples drawn from dataset
        self.batchSize = 32
        self.lr = 0.0001
        self.momentum = 0.001
         

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
        tmp = [] 
        for run in examples:
            for i,c in enumerate(run.configurations[1:]):
                tmp.append((run.configurations[i].features, c))
        examples = tmp

        featureArray = np.asarray([x[0] for x in examples]) 

        avg = np.mean(featureArray, axis=0) 
        std = np.std(featureArray, axis=0) 

        dataset = _Data(examples) 
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True) 

        self.predictor.train()

        optimizer = torch.optim.RMSprop(self.predictor.parameters(), lr=self.lr, momentum=self.momentum) 
        optimizer.zero_grad()
        
        for i,data in enumerate(dataset):
            pattern,target = data 

            #calculated and propogate loss for all outputs
            pattern = (pattern - avg)/std 
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
                loss = criteria(out[1], targetVal) 
                loss.backward(retain_graph=True)

            if i % self.batchSize == 0:
                optimizer.step()
                optimizer.zero_grad()


        self.predictor.eval()
        

    #generate a config from the provided features
    def _generate(self, features:ndarray) -> dict:
        dta = torch.from_numpy(np.asarray([features],dtype=np.float32))
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