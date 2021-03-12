#pragma once 

#include<iostream>
#include "RndGen.cpp"
#include<limits>
static const double DBLMAX = std::numeric_limits<double>::max();

//Used to encapsulated a solution to some problem
//A solution is simply a vector of real values
class Solution {
    protected:
        double * x;
        int length;
        double fit;
        bool evaled;

    public:
        Solution ** state;
        int stateLen; 

        Solution(double * sol, int len){
            stateLen = 0;
            state = new Solution*[stateLen];

            x = new double[len];
            for(int i = 0; i < len; i++)
                x[i] = sol[i];
            
            length = len;
            evaled = false;
            fit = DBLMAX;
        }

        //Cloning constructor
        Solution(Solution & s) {

            std::cout << "in cloning 1.0 \n";
            length = s.length; 
            x = new double[length];
            for(int i = 0; i < length; i++)
                x[i] = s.get(i);
            fit = s.fit; 
            evaled = s.evaled;

            std::cout << "in cloning 1.1 \n";
            stateLen = s.stateLen;
            state = new Solution*[stateLen];
            std::cout << "in cloning 1.2 \n";
            for(int i = 0; i < stateLen; i++) {
                state[i] = new Solution(*s.state[i]);
            }
            
        }

        virtual ~Solution() {
            delete[] x;

            for(int i = 0; i < stateLen; i++)
                delete state[i];
            delete[] state;
        }

 
        
        //Get the dimensionality of this solution
        virtual int numDim() {
            return length;
        }

        //Get the value of a specific dimension
        virtual double get(int i) {
            return x[i];
        }

        virtual void set(int i, double val) {
            evaled = false; 
            x[i] = val;
        }

        //Tests if this solution has been evaluated
        virtual bool evaluated() {
            return evaled;
        }

        virtual double getFit() {
            if(evaled) {
                return fit;
            } else {
                throw "Solution not evaluated!";
            }
        }

        virtual void setFit(double f) {
            evaled = true; 
            fit = f;
        }

}; 
