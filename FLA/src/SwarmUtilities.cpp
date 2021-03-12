#pragma once
#include"Solution.cpp"

//In this system, swarms (or more generally groups of solutions from the same time index) are stored in a tree like state structure
//The shape of this structure is not enforced through type safety, it's simply a convention
//So this class is responsible for knowing how to extra swarms from the state structure
//TODO:maybe add more structure to solution states... I'm not sure that it will be worth the effort for my purposes, since I only plan on testing a single algorithm

bool isSwarm(Solution * x) {
    if(x->stateLen != 1) {
        throw "Provided solution doesn't not appear to represent a swarm";
    } else {
        if(x->state[0]->stateLen == 0) 
            throw "Swarm is empty";
        else
            return true;
    }
    throw "Huh?!?!?";
    return false; // to get gcc to stop whining
}

int getSwarmSize(Solution * x) {
    if(isSwarm(x))
        return x->state[0]->stateLen;
    else 
        throw "Huh?!?!?!?"; //gets gcc to stop whining, this line can't run
}

Solution ** getSwarm(Solution * x) {
    if(isSwarm(x))
        return x->state[0]->state;
    else 
        throw "Huh?!?!?!?"; //gets gcc to stop whining, this line can't run
}