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


import pickle
from random import Random
from statistics import mean
from typing import Dict, Tuple
from Configurator.ConfigurationDB import ConfigurationDB
from Configurator.ConfigurationDefinition import ConfigurationDefinition,Configuration
from Configurator.Model import LatinHyperCube, NeuralNetwork
from numpy import ndarray
from copy import deepcopy

def initModel(state:dict, seed:int=None) -> "ConfigurationGenerator":
    return state["type"].loadState(state, seed)


"""
Responsible for acquiring configurations from a model or models, preprocessing/postprocessing, and validation of the config. 

In practice we will need two main methods, a way to generate initial configs, ie without features to predict from, and a way to select configs based on provided features. 
The underlying approaches will likely use combinations of predictions and random sampling, possibly applying constraints to either or both. Internally a ConfigurationGenerator
could be entirely random, could make use of/train multiple different models, etc. That logic should be contained in the ConfigurationGenerator, and the rest of LAAC should not need to be aware of the logic behind how configs are generated.
"""
class ConfigurationGenerator:
    def __init__(self, confDef:ConfigurationDefinition):
        #self.lock = Lock()
        self.confDef = confDef

    #TODO (maybe): instead of providing a single feature array to predict from, provide the feature arrays from all runs of the same sequence? 
    #We could provide the model with the average features of a random sample of the runs, leading to a number of possible inputs to the model = to #runs choose 1 +  # runs choose 2 + etc 
    #This might give the ConfigurationGenerator a way to make multiple attempts when a models predictions don't meet the constraints

    #Both _generateWithoutFeatures, and _generateWithFeatures should return a str identifying the method with which the configuration was generated and a dict defining the configuration
    #generate a single new config without using a feature vector
    def _generateWithoutFeatures(self) -> Tuple[str,dict]:
        raise NotImplementedError    

    #process the provided features to produce a new configuration
    def _generateWithFeatures(self, features:ndarray) -> Tuple[str,dict]:
        raise NotImplementedError

    #update the underlying model(s) 
    def _update(self, confDB:ConfigurationDB) -> None:
        raise NotImplementedError

    #updates the generation process based on the collected data 
    def update(self, confDB:ConfigurationDB) -> None:
        #with self.lock:
        self._update(confDB)
        
    #in some cases the "features" attached to a config may be None, for example when the configuration was invalid, and LAAC was told not to evaluate invalid configurations
    #this is just a wrapper to handle such cases
    def generate(self, features:ndarray= None) -> Configuration:
        #with self.lock:
        if features is None:
            method,conf = self._generateWithoutFeatures() 
        else:
            method,conf = self._generateWithFeatures(features)

        config = Configuration(self.confDef, conf)
        config.generationMethod = method

        return config

    #Should return a copy of the models internal state. Saving and restoring the state of the model should not impact the output of the model.
    def getState(self) -> Dict:
        raise NotImplementedError

    #Should return a new ConfigurationGenerator initialized with the provided state. Saving and restoring the state of the model should not impact the output of the model.
    @classmethod
    def loadState(cls, state:Dict, seed:int = None) -> None:
        raise NotImplementedError

    #produces a dict describing the training history of the model 
    def history(self) -> Dict:
        raise NotImplementedError

"""
A purely random configuration generator. With this generator LAAC will simply perform a random sampling of the configuration space.
"""
class RandomGenerator(ConfigurationGenerator):
    def __init__(self, confDef:ConfigurationDefinition, seed:int):
        super(RandomGenerator,self).__init__(confDef) 
        self.confDef = confDef
        self.model = LatinHyperCube(1000, confDef, seed) 
        self.training_history = {"history":[]}

    #LatinHyperCube ignores features entirely, its a random sampler
    def _generateWithoutFeatures(self) -> Tuple[str,dict]:
        return "Random", self.model.generate(None) 

    #LatinHyperCube ignores features entirely, its a random sampler
    def _generateWithFeatures(self, features:ndarray=None) -> Tuple[str,dict]:
        return "Random", self.model.generate(None) 

    #nothing to do here, this is a random sampler
    def _update(self, confDB:ConfigurationDB) -> None:
        iterHist = dict()
        probQuality = dict() 
        for run in confDB.getDesirables():
            prob = run.instance.problem 
            if prob not in probQuality:
                probQuality[prob] = [] 
            
            probQuality[prob].append(run.quality())

        bestQual = dict()
        aveQual = dict()
        for prob in probQuality:
            bestQual[prob] = min(probQuality[prob])
            aveQual[prob] = mean(probQuality[prob])

        iterHist["bestQualities"] = bestQual 
        iterHist["aveQualities"] = aveQual

        iterHist["informedPercent"] = 0
        iterHist["loss"] = []

        self.training_history["history"].append(iterHist)
            

    #should return a copy of the models internal state. Saving and restoring the state of the model should not impact the output of the model.
    def getState(self) -> Dict:
        state = dict() 
        state["type"] = RandomGenerator 
        state["confDef"] = pickle.dumps(self.confDef) 
        state["state"] = deepcopy(self.model.state())
        
        return state 

    #should initialzie the ConfigurationGenerator with the provided state. Saving and restoring the state of the model should not impact the output of the model.
    @classmethod
    def loadState(cls, state:Dict, seed:int = None) -> None:
        if seed is None:
            initSeed = 0 
        else:
            initSeed = seed 

        model = cls(pickle.loads(state["confDef"]), initSeed) 

        if seed is None:
            model.model.load(state["state"])

        return model 

    #produces a dict describing the training history of the model 
    def history(self) -> Dict:
        return self.training_history

"""
An adaptive ConfigurationGenerator. This implementation attempts to balance random sampling (for exploration) with features predicted via neural network. The proportions of randomly sampled parameters vs predicted paramters are determined automatically based on the quality of previously produced configurations.
"""
class AdaptiveGenerator(ConfigurationGenerator):
    #featureSize is the size of feature vectors
    #cpu indicates whether CPU should be used for training 
    #minInformedPercent indicates the minimum percentage of configurations which should be generated via NN prediction
    #maxInformedPercent indicates the maximum percentage of configurations which should be generated via NN prediction
    #informedPercentVariance is the acceptable variance in informedPercent. In pratice the percentage of predictions to perform via NN will be updated periodically, and chosen via informedPercent + N(0, variance)
    #period refers to the initial number of times _generateWithFeatures will be called before the percentage of predictons to perform via NN updates. This value will updated adaptively at run time based on the expected number of calls to _generateWithFeatures per run 
    def __init__(self, featureSize:int, confDef:ConfigurationDefinition, seed:int, cpu:bool = True, minInformedPercent:float=0.05, maxInformedPercent:float=0.95, informedPercentVariance:float=0.1):
        super(AdaptiveGenerator,self).__init__(confDef) 
        self.rng = Random(seed)
        self.rndModel = LatinHyperCube(1000, confDef, self.rng.randint(0,4000000000)) 
        self.nn = NeuralNetwork(featureSize, confDef, self.rng.randint(0,4000000000), cpu)
        self.minInformedPercent = minInformedPercent
        self.maxInformedPercent = maxInformedPercent
        self.informedPercentVariance = informedPercentVariance
        self.featureSize = featureSize

        #TODO: should informedPercent be selected on a per problem basis?
        self._informedPercent = self.minInformedPercent
        self._informedPercentRnd = None 

        self._chooseNewInformedPercentRnd()

        self._starterConfigs = [] #Will contain a list of initial configurations which previous led to desirable runs 

        self.training_history = {"history":[]}

    def _chooseNewInformedPercentRnd(self):
        self._informedPercentRnd = self._informedPercent + self.rng.normalvariate(0, self.informedPercentVariance)
        if self._informedPercentRnd > self.maxInformedPercent:
            self._informedPercentRnd = self.maxInformedPercent 
        if self._informedPercentRnd < self.minInformedPercent:
            self._informedPercentRnd = self.minInformedPercent

    #LatinHyperCube is used when no features are provided, since we have nothing to base feature selection on 
    def _generateWithoutFeatures(self) -> Tuple[str,dict]:
        if len(self._starterConfigs) > 0 and self.rng.random() < self._informedPercentRnd:
            return "Informed", self.rng.choice(self._starterConfigs)
        else:
            return "Random", self.rndModel.generate(None) 

    #Here we adaptively choose between random sampling, and informed prediction 
    #The main goal is to strike a balance between exploration of the parameter space, and exploitation of the trained models knowledge to improve performance
    def _generateWithFeatures(self, features:ndarray=None) -> Tuple[str,dict]:

        if self.rng.random() < self._informedPercentRnd:
            r1,r2 = "Informed", self.nn.generate(features) 
            return r1,r2
        else:
            r1,r2 = "Random", self.rndModel.generate(None)
            return r1,r2

    #Testing to see if we can use the RandomGenerator and torch at the same time despite the GIL
    def generate(self, features:ndarray= None) -> Configuration:

        if features is None:
            method,conf = self._generateWithoutFeatures() 
        else:
            method,conf = self._generateWithFeatures(features)


        config = Configuration(self.confDef, conf)
        config.generationMethod = method

        return config

    #Train the model, update informedPercent and period 
    def _update(self, confDB:ConfigurationDB) -> None:
        iterHist = dict() 

        self.nn.update(confDB) #Train the network 

        iterHist["loss"] = self.nn.history[-1] 

        observedInformedConfigs = 0
        observedConfigs = 0 

        #We first determine the average number of configurations, and average number of informed configurations, per desirable run 
        #We also refresh the list of start configs 

        del self._starterConfigs 
        self._starterConfigs = [] 

        #TODO: once the new evaluator is done (and getDesirables is updated) consider modifying this to grab a sample of desirable runs, then only store the top such and such percent initial configs per problem 
        #that way the generators informed predictions will represent strong initial configs, rather than initial configs the model performed well at improving upon
        probQuality = dict() 
        for run in confDB.getDesirables(128):
            self._starterConfigs.append(deepcopy(run.configurations[0]._origDict))

            observedConfigs += len(run.configurations)
            for conf in run.configurations:
                if conf.generationMethod == "Informed":
                    observedInformedConfigs += 1 

            prob = run.instance.problem 
            if prob not in probQuality:
                probQuality[prob] = [] 
            
            probQuality[prob].append(run.quality())

        bestQual = dict()
        aveQual = dict()
        for prob in probQuality:
            bestQual[prob] = min(probQuality[prob])
            aveQual[prob] = mean(probQuality[prob])

        iterHist["bestQualities"] = bestQual 
        iterHist["aveQualities"] = aveQual

        aveInformedConfig = observedInformedConfigs/observedConfigs 

        self._informedPercent = aveInformedConfig #On average, the percentage of predictions which should be "informed" are chosen based on the percentage of informed predictions among the desirable configurations 

        iterHist["informedPercent"] = self._informedPercent 

        self.training_history["history"].append(iterHist)

        self._chooseNewInformedPercentRnd()


    #should return a copy of the models internal state. Saving and restoring the state of the model should not impact the output of the model.
    def getState(self) -> Dict:
        state = dict()
        state["nn"] = self.nn.state()
        state["rnd"] = self.rndModel.state() 
        state["rng"] = pickle.dumps(self.rng)
        state["minInfPerc"] = self.minInformedPercent 
        state["maxInfPerc"] = self.maxInformedPercent 
        state["infPercVar"] = self.informedPercentVariance
        state["starterConfigs"] = self._starterConfigs 
        state["featureSize"] = self.featureSize
        state["informedPercent"] = self._informedPercent
        state["informedPercentRnd"] = self._informedPercentRnd
        state["confDef"] = pickle.dumps(self.confDef)
        state["type"] = AdaptiveGenerator
        return deepcopy(state)

    #should initialzie the ConfigurationGenerator with the provided state. Saving and restoring the state of the model should not impact the output of the model.
    @classmethod
    def loadState(cls, state:Dict, seed:int=None) -> None:

        if seed is None:
            initSeed = 0
        else:
            initSeed = seed 

        model = cls(state["featureSize"], pickle.loads(state["confDef"]), initSeed, True, state["minInfPerc"], state["maxInfPerc"], state["infPercVar"])

        model.nn.load(state["nn"])
        model._starterConfigs = state["starterConfigs"]
        model._informedPercent = state["informedPercent"]

        if seed is None:
            model.rndModel.load(state["rnd"])
            model.rng = pickle.loads(state["rng"]) 
            model._informedPercentRnd = state["informedPercentRnd"]


        #Each "run" will load its own copy of the model, and thus use a semi-random value for informedPercentRnd
        #This should allow the percentage of predicted parameters to increase over time once the predicted parameters begin to perform well
        if seed is not None:
            model._chooseNewInformedPercentRnd()

        return model

    #produces a dict describing the training history of the model 
    def history(self) -> Dict:
        return self.training_history