#pragma once 

#include "RndGen.cpp"
#include "Solution.cpp"
#include<vector>
#include<iostream>

//TODO:update a sample so that start and end are configurable, ex the actual size could be 100, the advertized size 10, and start/end variables exist internally to specify which consecutive 10 solutions consitute the advertised sample
//This is probably the easiest way to extend samples for local FLA and online tuning 

//Encapsulates a set of evaluated solutions for use in FLA calculations
class Sample { 
    private:
        Sample(const Sample & a);
        Sample& operator=(const Sample& other);
        std::vector<Solution *> * solutions;
        int advertisedSize; //Allows a sample to be treated as smaller than it actually is

    public:
        Sample() {
            solutions = new std::vector<Solution *>();
            advertisedSize = -1; //Any size less than 0 means use the actual size
        }

        virtual ~Sample() { 
            for(ulong i = 0; i < solutions->size(); i++)
                delete (*solutions)[i];
            delete solutions; 
        }

        //adds an evaluated solution to the sample. The order in which solutions are added will be preserved 
        //This method should verify that the solution is actually evaluated
        virtual bool add(Solution * n) {
            if( n -> evaluated()) {
                solutions -> push_back(n);
                return true;
            } else {
                return false;
            }
        }

        //Returns the size of the sample
        virtual int size() {
            if(advertisedSize < 0)
                return solutions -> size();
            else
                return advertisedSize;
        }

        virtual void resetAdvertisedSize() {
            advertisedSize = -1;
        }

        virtual bool setAdvertisedSize(unsigned long i) {
            if(i <= solutions->size()) {
                advertisedSize = i;
                return true;
            } else {
                return false;
            }
        }

        //Gets a point from the sample 
        virtual Solution * get(int i) {
            return (*solutions)[i];
        }

        //remove all the pointers to solutions from solutions. This is usefull when two samples point to the same solution objects
        virtual void reset() {
            while(solutions->size() > 0)
                solutions->clear();
        }
};

