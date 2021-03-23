#include "FLM.cpp"
#include "Sample.cpp"
#include "Solution.cpp"

#include<iostream>

//TODO: The whole FLA code base needs to be cleaned up and adapted for this project

//A struct for containing results 
struct Characteristics {
    double FDC; 
    double yDist[2]; 
    double pairwise[54];
    double FEM;
    double grad[7];
    double M[2];
    double stag[2];
    double * diversity; 
    double * gBestStep; 
    double * gBestStag;
    double * gBestyDist;
};


/*
    Characterizes the provided solutions. 
    solutions is a 2d array containing the solution from each iteration of the search 
    quality gives the quality of each coresponding solution in solutions 
        The majority of our characteristics assume they are calculated from a series of spatially correlated vectors (along with their qualities)
        Solutions and quality will be used as this series for calculating the majority of the returned characteristics 
        An easy option is to simply use the best solution found thus far at each iteration of your algorithm, however its possible to use any series of vectors/qualities 
        Experimentation will be needed in order to be sure what the best choice is for a particular use case 

    state gives the pool of solutions considered at each iteration of the search
    stateQuality gives the quality of each solution in state 
        In a population based approach state/stateQuality simply represents the population at each iteration 
        It's primarilly used for the calculation of diversity, which can be used as an indicator of exporative vs expoitative behavior, and relates to the amount of variety among the considered solutions 
        So state should help give an idea of the variety or spread of the solutions considered at each iteration 

    numSols is the length of dimension 0 of solutions and quality 
    dims is the length of dimension 1 of solutions and quality/dim 2 of state 
    stateSize is the number of solutions in state at each iteration, ie the size of dimension 1 of each element of state dimension 0
    characteristics will be initialized with a double array containing the computed characteristcs 
    the returned int will give the length of characteristics 
*/
void characterize_cpp(double ** solutions, double * quality, double *** state, double ** stateQuality, int numSolutions, int * stateSize, int dims, Characteristics & characteristics, long seed) {


    //TODO: Adjust dispersion to not throw errors for small samples

    try{//TODO: remove this disgusting try/catch

        //obtain a sample 
        Sample * S = new Sample();

        for(int i = 0; i < numSolutions; i++) {
            Solution * n = new Solution(solutions[i], dims);
            n->setFit(quality[i]);

            //So, some explanation for this mess 
            //Solutions contain a top level vector and quality, as well as a state 
            //The state inside a solution is simply a list of Solutions, which of course can contain lists of solutions themselves 
            //The FLA code we're using here is reused from a different project, and expects the vectors from our state parameters to be stored at 
            // S -> state[0] -> state, so we store them there 

            Solution * clone = new Solution(*n);
            delete[] n -> state ;
            n -> stateLen = 1 ;
            n -> state = new Solution*[n->stateLen]; 
            n -> state[0] = clone; 

            delete[] n -> state[0] -> state ;
            n -> state[0] -> stateLen = stateSize[i];
            n -> state[0] -> state = new Solution*[n -> state[0] -> stateLen]; 

            for(int j = 0; j < n -> state[0] -> stateLen; j++) {
                n -> state[0] -> state[j] = new Solution(state[i][j], dims);
                n -> state[0] -> state[j] -> setFit(stateQuality[i][j]);
            }
            
            S -> add(n);
            
        }

        //Initialize the landscape measures to use 
        int frequency = 1;
        RndGen rnd = RndGen(seed);

        //Landscape characteristics to evaluate 
        FDC fdc;
        yDist  ydist;
        Pairwise pairwise(&rnd);
        FEM fem;
        Grad grad;
        M m;
        Stag stag;
        Diversity diversity(numSolutions,frequency);
        GBestStep gbeststep(numSolutions,frequency);
        //measures[measureCounter] = new SwarmStep(sampleSize, numPart,frequencyForNonCheckpointableFLMS);
        GBestStag gbeststag(dims);
        //measures[measureCounter] = new SwarmStag(dimensionality, numPart);
        GBestyDist gbestydist(dims);
        //measures[measureCounter] = new SwarmyDist(dimensionality, numPart);
        

        double * ret; 
        ret = fdc.calculate(*S);
        characteristics.FDC = ret[0]; 
        //std::cout << characteristics.FDC << "\n";
        delete[] ret;

        ret = ydist.calculate(*S);
        for(int i = 0; i < 2; i++) {
            characteristics.yDist[i] = ret[i];
            //std::cout << ret[i] << " "; 
        }
        //std::cout << "\n";
        delete[] ret;
        
        ret = pairwise.calculate(*S);
        for(int i = 0; i < 54; i++) {
            characteristics.pairwise[i] = ret[i];
            //std::cout << ret[i] << " "; 
        }
        //std::cout << "\n";
        delete[] ret;

        ret = fem.calculate(*S);
        characteristics.FEM = ret[0];
        //std::cout << ret[0] << " "; 
        delete[] ret; 

        ret = grad.calculate(*S);
        for(int i = 0; i < 7; i++) {
            characteristics.grad[i] = ret[i];
            //std::cout << ret[i] << " "; 
        }
        //std::cout << "\n";
        delete[] ret;

        ret = m.calculate(*S);
        for(int i = 0; i < 2; i++) {
            characteristics.M[i] = ret[i];
            //std::cout << ret[i] << " "; 
        }
        //std::cout << "\n";
        delete[] ret;
    
        ret = stag.calculate(*S);
        for(int i = 0; i < 2; i++) {
            characteristics.stag[i] = ret[i];
            //std::cout << ret[i] << " "; 
        }
        //std::cout << "\n";
        delete[] ret;

        //May throw an error if no state is provided, the python code should do its own checking too
        try {
            ret = diversity.calculate(*S);
            for(int i = 0; i < numSolutions; i++) {
                characteristics.diversity[i] = ret[i];
                //std::cout << ret[i] << " ";
            }
            //std::cout << "\n";
            delete[] ret; 
        } catch (const char * c) {
            for(int i = 0; i < numSolutions; i++) 
                characteristics.diversity[i] = 0;
        }
        

        ret = gbeststep.calculate(*S);
        for(int i = 0; i < numSolutions; i++){
            characteristics.gBestStep[i] = ret[i];
            //std::cout << ret[i] << " ";
        }
        //std::cout << "\n";
        delete[] ret; 

        ret = gbeststag.calculate(*S);
        for(int i = 0; i < 2*dims; i++) {
            characteristics.gBestStag[i] = ret[i];
            //std::cout << ret[i] << " ";
        }
        //std::cout << "\n";
        delete[] ret; 

        ret = gbestydist.calculate(*S);
        for(int i = 0; i < 2*dims; i++) {
            characteristics.gBestyDist[i] = ret[i];
            //std::cout << ret[i] << " ";
        }
        //std::cout << "\n";
        delete[] ret;

        //std::cout <<"huh?\n";
        delete S;
    } catch (const char * c) {
        std::cout << c << "\n";
    }
}



extern "C" {
    void characterize(double ** solutions, double * quality, double *** state, double ** stateQuality, int numSolutions, int * stateSize, int dims, Characteristics & characteristics, long seed){ return characterize_cpp(solutions, quality, state, stateQuality, numSolutions, stateSize, dims, characteristics, seed); }
}

