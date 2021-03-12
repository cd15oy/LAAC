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

// //Generates a series of solutions according to some rule and evaluates them 
// class Sampler {
//     private:
//         Sampler(const Sampler & a);
//         Sampler& operator=(const Sampler& other);
//         Sampler(){};

//         //Accepts an empty sample, and populates it with sampleSize solutions generated in the appropriate manner
//         //This method actually defines how a sampler samples solutions
//         virtual bool next(Sample & s, Problem & d) = 0;


//     public:
//         int sampleSize;
//         RndGen * rnd;

//         Sampler(int sSize, RndGen * r){
//             sampleSize = sSize;
//             rnd = r;
//         };

//         virtual ~Sampler(){};

        
//         //Get a sampleSize sized sample of evaluated solutions
//         //Basically this method is for any pre/post processing that should be applied to all generic samples 
//         virtual Sample * sample(Problem & d) {
//             //std::cout << d.hasBatch() << " has batch\n";
//             Sample * S = new Sample();
//             next(*S, d);
//             //std::cout << "The size I think I'm returning: " << S->size() << "\n";
//             return S;
//         }
// };

// class UniformRandom : public Sampler {
//     public:
//         UniformRandom(int sampleSize, RndGen * r) : Sampler(sampleSize, r) {}
        
//         ~UniformRandom() {}

//         bool next(Sample & s, Problem & d) {
//             for(int i = 0; i < sampleSize; i++) {
//                 Solution * n = new Solution(rnd, d);
                    
//                 n->evaluate(d);
//                 bool tmp = s.add(n);
//                 if(!tmp) return false;
//             }
//             return true;
//         };
// };

// class ProgressiveSampler : public Sampler {
//     public:
//         double stepSize;

//         ProgressiveSampler(int smplSz, double stpSz, RndGen * r) : Sampler(smplSz, r) {
//             stepSize = stpSz;
//         }
        
// };

// class ProgressiveRandom : public ProgressiveSampler {

//     public:
//         ProgressiveRandom(int smplSz, double stpSz, RndGen * r) : ProgressiveSampler(smplSz, stpSz, r) {}

//         ~ProgressiveRandom() { 
//             //Don't delete anything else, all of the other things were initialzed outside, and can be used by other objects
//         }

//         bool next(Sample & s, Problem & d) {
//             int direction[d.dims()];

//             for(int l = 0; l < d.dims(); l++) { 
//                 if(rnd->rnd() <= 0.5)
//                     direction[l] = -1;
//                 else 
//                     direction[l] = 1;
//             }

//             //Generate a new solution randomly placed in the space
//             Solution * n = new Solution(rnd, d);
//             n->evaluate(d);
//             bool tmp = s.add(n);

//             if(!tmp) return tmp;

//             //Generate each step of the walk
//             for(int x = 0; x < sampleSize-1;x++){
//                 Solution * last = s.get(s.size()-1);
//                 Solution * n = new Solution(d);
                
//                 for(int l = 0; l < d.dims(); l++) {
//                     n-> set(l, last->get(l) + (direction[l]*rnd -> rnd()*stepSize));

//                     if(n->get(l) > d.maxVal()) {
//                         direction[l] *= -1;
//                         double diff = n->get(l) - d.maxVal(); 
//                         n->set(l, d.maxVal() - diff);
//                     } else if(n->get(l) < d.minVal()) {
//                         direction[l] *= -1;
//                         double diff = d.minVal() - n->get(l); 
//                         n->set(l, d.minVal() + diff);
//                     }
//                 }

//                 n->evaluate(d);
//                 bool tmp = s.add(n);
//                 if(!tmp) return tmp;
//             }
//             return true;
//         };
// };

// class ManhattanProgressiveRandom : public ProgressiveSampler {
 
//     public:
//         ManhattanProgressiveRandom(int smplSz, double stpSz, RndGen * r) : ProgressiveSampler(smplSz, stpSz, r) {}

//         ~ManhattanProgressiveRandom() { 
//             //Don't delete anything else, all of the other things were initialzed outside, and can be used by other objects
//         }

//         bool next(Sample & s,Problem & d) {
//             int direction[d.dims()];

//             for(int l = 0; l < d.dims(); l++) { 
//                 if(rnd->rnd() <= 0.5)
//                     direction[l] = -1;
//                 else 
//                     direction[l] = 1;
//             }

//             //Generate a new solution randomly placed in the space
//             Solution * n = new Solution(rnd, d);
//             n->evaluate(d);
//             bool tmp = s.add(n);

//             if(!tmp) return tmp;
        
//             //Generate the remaining steps of the walk
//             //Generate each step of the walk
//             for(int x = 0; x < sampleSize-1;x++){
//                 Solution * last = s.get(s.size()-1);
//                 Solution * n = new Solution(d);

//                 int chosenDim = (int)(rnd->rnd()*d.dims());


//                 for(int l = 0; l < d.dims(); l++) {

//                     if(l == chosenDim) {
//                         n-> set(l, last->get(l) + (direction[l]*stepSize));

//                         if(n->get(l) > d.maxVal()) {
//                             direction[l] *= -1;
//                             double diff = n->get(l) - d.maxVal(); 
//                             n->set(l, d.maxVal() - diff);
//                         } else if(n->get(l) < d.minVal()) {
//                             direction[l] *= -1;
//                             double diff = d.minVal() - n->get(l); 
//                             n->set(l, d.minVal() + diff);
//                         }
//                     } else {
//                         n-> set(l, last->get(l));
//                     }
//                 }
//                 n->evaluate(d);
//                 bool tmp = s.add(n);
//                 if(!tmp) return tmp;
//             }
//             return true;
//         };
// };

// //Samples points using an async gbest PSO
// class PSO : public Sampler {
//     private:
//         double c1 = 1.49618;
//         double c2 = 1.49618;
//         double w = 0.729844;
//         int numPart = 30;
//     public:
//         PSO(int sampleSize, RndGen * r) : Sampler(sampleSize, r) {}

//         PSO(int sampleSize, double cog, double soc, double omg, int ps, RndGen * r) : Sampler(sampleSize, r) {
//             c1 = cog;
//             c2 = soc;
//             w = omg;
//             numPart = ps;
//         }
        
//         ~PSO() {}

//         bool next(Sample & s, Problem & d) {
//             //s starts out as an empty sample

//             //First we need to construct a solution with state appropriate for PSO 

//             //The upper level solution represents the gobal best, the state represents the swarm 
//             Solution * init = new Solution(d);

//             //state contains
//             //current position at [0]
//             //personal best at [1] 
//             //velocity at [2] 
//             delete[] init -> state;
//             init -> stateLen = 3;
//             init -> state = new Solution*[init->stateLen];
//             //the solutions at state [0-2] are meaningless, and unused 

//             //Fill up the states at 0-2 to accomodate numPart particles
//             //Initialize current position, and personal best randomly in the search space
//             //Velocity is initialized to 0
//             for(int i = 0; i < 3; i++) {
//                 init -> state[i] = new Solution(d);
//                 Solution * cur = init->state[i];
//                 delete[] cur->state;
//                 cur->state = new Solution*[numPart];
//                 cur -> stateLen = numPart;
//                 for(int j = 0; j < numPart; j++) {
//                     if(i < 2)
//                         cur ->state[j] = new Solution(rnd, d);
//                     else 
//                         cur -> state[j] = new Solution(d);
//                 }
//             }

//             init -> setFit(DBLMAX);

//             //Evaluate the personal best and current positions, and swap if needed
//             //Also track and update the global best 
//             for(int i = 0; i < numPart; i++) {
             
//                 Solution * curPos = init -> state[0]->state[i];
//                 Solution * pBest = init -> state[1]->state[i];
//                 curPos -> evaluate(d);
//                 pBest -> evaluate(d);
             
//                 if(curPos->getFit() < pBest->getFit()) {
//                     init -> state[0]->state[i] = pBest; 
//                     init -> state[1]->state[i] = curPos;
//                     pBest = curPos;
//                 }
        
//                 if(pBest->getFit() < init ->getFit()) {
//                     for(int j = 0; j < d.dims(); j++) 
//                         init -> set(j, pBest->get(j));
//                     init -> setFit(pBest->getFit());
//                 }
                
//             }

//             //Add the initial swarm to the sample
//             bool tmp = s.add(init);
//             if(!tmp) return false;

//             //get more solutions
//             for(int i = 0; i < sampleSize-1; i++) {
//                 //Clone the previous iteration
//                 Solution * n = new Solution(*s.get(s.size()-1));

//                 //Syncronous pBest and gBest update 
//                 for(int j = 0; j < numPart; j++) {
//                     Solution * curPos = n -> state[0]->state[j];
//                     Solution * pBest = n -> state[1]->state[j];
//                     if(curPos->getFit() < pBest->getFit()) {
//                         //Delete the old pBest and clone the current position 
//                         delete n -> state[1] -> state[j];
//                         n -> state[1] -> state[j] = new Solution(*curPos);
//                         pBest = n -> state[1] -> state[j];
//                     }
//                     if(pBest->getFit() < n ->getFit()) {
//                         for(int k = 0; k < d.dims(); k++) 
//                             n -> set(k, pBest->get(k));
//                         n -> setFit(pBest->getFit());
//                     }
//                 }

//                 //update velocity, positions, and current fitness 
//                 for(int j = 0; j < numPart; j++) {
//                     Solution * curPos = n -> state[0]->state[j];
//                     Solution * pBest = n -> state[1]->state[j];
//                     Solution * vel = n -> state[2]->state[j];

//                     bool boundViolation = false;

//                     for(int k = 0; k < vel -> numDim(); k++) {
//                         vel -> set(k, (w*vel->get(k)) + (c1*rnd->rnd()*(pBest->get(k) - curPos->get(k))) + (c2*rnd->rnd()*(n->get(k) - curPos->get(k))));
//                         double newPos = curPos->get(k) + vel->get(k);
//                         curPos->set(k, newPos);
//                         if(newPos > d.maxVal() || newPos < d.minVal())
//                             boundViolation = true;
//                     }

//                     bool canUpdate = true; 
//                     if(d.isBounded()) 
//                         if(boundViolation)
//                             canUpdate = false;

                    

//                     if(canUpdate)
//                         curPos->evaluate(d);
//                     else 
//                         curPos->setFit(DBLMAX);
                    
//                 }

           
//                 bool tmp = s.add(n);
//                 if(!tmp) return false;
//             }
//             return true;
//         };

// };


