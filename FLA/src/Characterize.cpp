#include "FLM.cpp"
#include "Sample.cpp"
#include "Solution.cpp"

#include<iostream>

//TODO: The whole FLA code base needs to be cleaned up and adapted for this project

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
int characterize_cpp(double ** solutions, double * quality, double *** state, double ** stateQuality, int numSolutions, int * stateSize, int dims, double * characteristics, long seed) {
    std::cout << "1" << "\n";
    //obtain a sample 
    Sample * S = new Sample();

    for(int i = 0; i < numSolutions; i++) {
        std::cout << "1.0" << "\n";
        std::cout << "1.01" << solutions[i][0] << "\n";
        std::cout << "1.02" << "\n";
        Solution * n = new Solution(solutions[i], dims);
        std::cout << "1.05" << "\n";
        n->setFit(quality[i]);
        std::cout << "1.1" << "\n";
        //So, some explanation for this mess 
        //Solutions contain a top level vector and quality, as well as a state 
        //The state inside a solution is simply a list of Solutions, which of course can contain lists of solutions themselves 
        //The FLA code we're using here is reused from a different project, and expects the vectors from our state parameters to be stored at 
        // S -> state[0] -> state, so we store them there 

        Solution * clone = new Solution(*n);
        delete[] n -> state ;
        std::cout << "1.101" << "\n";
        n -> stateLen = 1 ;
        n -> state = new Solution*[n->stateLen]; 
        std::cout << "1.102" << "\n";
        n -> state[0] = clone; 

        std::cout << "1.11" << "\n";

        delete[] n -> state[0] -> state ;
        n -> state[0] -> stateLen = stateSize[i];
        n -> state[0] -> state = new Solution*[n -> state[0] -> stateLen]; 

        std::cout << "1.2" << "\n";
        for(int j = 0; j < n -> state[0] -> stateLen; j++) {
            n -> state[0] -> state[j] = new Solution(state[i][j], dims);
            n -> state[0] -> state[j] -> setFit(stateQuality[i][j]);
        }
        
        std::cout << "1.3" << "\n";
        S -> add(n);
        
    }

    std::cout << "2" << "\n";

    //Initialize the landscape measures to use 
    int numFLMs = 11;
    FLM * measures[numFLMs]; //The measures to use 
    int frequency = 1;
    RndGen rnd = RndGen(seed);

    //Landscape characteristics to evaluate 
    measures[0] = new FDC();
    measures[1] = new yDist();
    measures[2] = new Pairwise(&rnd);
    measures[3] = new FEM();
    measures[4] = new Grad();
    measures[5] = new M();
    measures[6] = new Stag();
    measures[7] = new Diversity(numSolutions,frequency);
    measures[8] = new GBestStep(numSolutions,frequency);
    //measures[measureCounter] = new SwarmStep(sampleSize, numPart,frequencyForNonCheckpointableFLMS);
    measures[9] = new GBestStag(dims);
    //measures[measureCounter] = new SwarmStag(dimensionality, numPart);
    measures[10] = new GBestyDist(dims);
    //measures[measureCounter] = new SwarmyDist(dimensionality, numPart);
            

    std::cout << "3" << "\n";
   
    double * FLMEs[numFLMs];    //An array of arrays containing FLM estimates

    try {
        //Estimate the FLMs
        for(int j = 0; j < numFLMs; j++) {
            FLMEs[j] = measures[j]->calculate(*S);
        }
    } catch (const char * c) {
        std::cout << c << "\n";
    }

    std::cout << "4" << "\n";

    int characteristicVectorLength = 0; 
    for(int j = 0; j < numFLMs; j++)
        characteristicVectorLength += measures[j]-> lenOut();

    //delete[] characteristics;
    //characteristics = new double[characteristicVectorLength]; 

    int ptr = 0; 
    std::cout << "------\n";
    for(int i = 0; i < numFLMs; i++) {
        for(int j = 0; j < measures[i] -> lenOut(); j++) {
            characteristics[ptr] = FLMEs[i][j];
            std::cout << FLMEs[i][j] << " ";
            ptr++;
        }
        std::cout << "\n\n";
    }

    std::cout << "5" << "\n";

    //TODO: free memory

    return characteristicVectorLength;
}



extern "C" {
    int characterize(double ** solutions, double * quality, double *** state, double ** stateQuality, int numSolutions, int * stateSize, int dims, double characteristics[104], long seed){ return characterize_cpp(solutions, quality, state, stateQuality, numSolutions, stateSize, dims, characteristics, seed); }
}