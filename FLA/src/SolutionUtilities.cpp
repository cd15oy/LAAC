#pragma once
#include "Solution.cpp"

double dist(Solution * a, Solution * b) {
    double dist = 0.0000000000000000001;
    if(a->numDim() != b->numDim())
        throw "Cannot calculate the distance between solutions of different length!";
    else {
        for(int i = 0; i < b->numDim(); i++)
            dist += pow(a->get(i) - b->get(i), 2);
    }
        return sqrt(dist);
}